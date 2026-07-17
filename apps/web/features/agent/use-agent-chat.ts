"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from "react";
import { z } from "zod";

import {
  consumeAgentStream,
  type AgentStreamEvent,
  type ForecastRecommendation,
} from "@/features/agent/agent-stream";
import type { AgentProgressStep } from "@/features/agent/agent-progress";
import { api } from "@/lib/api/client";
import { queryKeys } from "@/lib/query-keys";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const conversationStorageKey = (householdId: string) => `padalo-agent-conversation:${householdId}`;

export function useAgentChat(householdId: string) {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [recommendation, setRecommendation] = useState<ForecastRecommendation | null>(null);
  const [activity, setActivity] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  const [progressSteps, setProgressSteps] = useState<AgentProgressStep[]>([]);

  useEffect(() => {
    setMessages([]);
    setRecommendation(null);
    setActivity(null);
    setError(null);
    setProgressSteps([]);
    setLastMessage(null);
    setConversationId(readConversationId(householdId));
  }, [householdId]);

  const invalidateLedger = useCallback(
    (resource: "transaction" | "remittance") => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard(householdId) });
      if (resource === "transaction") {
        void queryClient.invalidateQueries({ queryKey: queryKeys.transactions(householdId) });
        void queryClient.invalidateQueries({ queryKey: queryKeys.envelopes(householdId) });
      } else {
        void queryClient.invalidateQueries({ queryKey: queryKeys.remittances(householdId) });
      }
    },
    [householdId, queryClient],
  );

  const sendMessage = useCallback(
    async (content: string, { appendUserMessage = true }: { appendUserMessage?: boolean } = {}) => {
      const message = content.trim();
      if (!message || !householdId || isStreaming) return;

      const assistantMessageId = createId();
      setLastMessage(message);
      setMessages((current) => [
        ...current,
        ...(appendUserMessage ? [{ id: createId(), role: "user" as const, content: message }] : []),
        { id: assistantMessageId, role: "assistant", content: "" },
      ]);
      setActivity("Reading household details.");
      setError(null);
      setProgressSteps([createInitialProgressStep()]);
      setIsStreaming(true);

      try {
        const response = await api.openAgentStream(householdId, {
          message,
          conversation_id: conversationId,
        });
        await consumeAgentStream(response, (event) => {
          handleAgentEvent({
            event,
            assistantMessageId,
            householdId,
            invalidateLedger,
            setActivity,
            setConversationId,
            setError,
            setMessages,
            setProgressSteps,
            setRecommendation,
          });
        });
      } catch (streamError) {
        const messageText = agentErrorMessage(streamError);
        setError(messageText);
        setProgressSteps((steps) => markActiveProgressError(steps));
        setMessages((current) =>
          current.map((chatMessage) =>
            chatMessage.id === assistantMessageId && !chatMessage.content
              ? { ...chatMessage, content: "I could not complete that request right now." }
              : chatMessage,
          ),
        );
      } finally {
        setActivity(null);
        setIsStreaming(false);
      }
    },
    [conversationId, householdId, invalidateLedger, isStreaming],
  );

  const retryLastMessage = useCallback(async () => {
    if (!lastMessage || isStreaming) return;
    await sendMessage(lastMessage, { appendUserMessage: false });
  }, [isStreaming, lastMessage, sendMessage]);

  return {
    activity,
    error,
    isStreaming,
    messages,
    progressSteps,
    recommendation,
    retryLastMessage,
    sendMessage,
  };
}

type EventHandlerArgs = {
  event: AgentStreamEvent;
  assistantMessageId: string;
  householdId: string;
  invalidateLedger: (resource: "transaction" | "remittance") => void;
  setActivity: Dispatch<SetStateAction<string | null>>;
  setConversationId: Dispatch<SetStateAction<string | undefined>>;
  setError: Dispatch<SetStateAction<string | null>>;
  setMessages: Dispatch<SetStateAction<ChatMessage[]>>;
  setProgressSteps: Dispatch<SetStateAction<AgentProgressStep[]>>;
  setRecommendation: Dispatch<SetStateAction<ForecastRecommendation | null>>;
};

function handleAgentEvent({
  event,
  assistantMessageId,
  householdId,
  invalidateLedger,
  setActivity,
  setConversationId,
  setError,
  setMessages,
  setProgressSteps,
  setRecommendation,
}: EventHandlerArgs) {
  switch (event.event) {
    case "conversation":
      setConversationId(event.data.conversation_id);
      persistConversationId(householdId, event.data.conversation_id);
      break;
    case "status":
      setActivity(statusActivity(event.data.message));
      if (event.data.message === "Reviewing your request.") {
        setProgressSteps((steps) =>
          activateProgressStep(
            completeActiveProgressSteps(steps),
            "cash-flow",
            "Reviewing household cash flow",
          ),
        );
      }
      if (event.data.message === "Using the household result to finish the answer.") {
        setProgressSteps((steps) => ensureRecommendationProgressStep(steps));
      }
      break;
    case "tool_call":
      setActivity(toolActivity(event.data.name));
      setProgressSteps((steps) => startToolProgressStep(steps, event.data.name));
      break;
    case "tool_result":
      setProgressSteps((steps) => finishToolProgressStep(steps, event.data.name, event.data.ok));
      if (!event.data.ok) {
        setActivity(event.data.error?.message ?? "The household action needs more detail.");
        break;
      }
      if (event.data.name === "forecast_remittance") {
        const recommendation = parseRecommendation(event.data.data);
        if (recommendation) setRecommendation(recommendation);
      }
      if (event.data.name === "log_expense") invalidateLedger("transaction");
      if (event.data.name === "create_remittance") invalidateLedger("remittance");
      break;
    case "assistant_delta":
      setActivity("Preparing your recommendation.");
      setProgressSteps((steps) => ensureRecommendationProgressStep(steps));
      setMessages((current) =>
        current.map((chatMessage) =>
          chatMessage.id === assistantMessageId
            ? { ...chatMessage, content: `${chatMessage.content}${event.data.delta}` }
            : chatMessage,
        ),
      );
      break;
    case "final":
      setActivity("Complete.");
      setProgressSteps((steps) => completeProgressSteps(steps));
      setMessages((current) =>
        current.map((chatMessage) =>
          chatMessage.id === assistantMessageId
            ? { ...chatMessage, content: event.data.response.message }
            : chatMessage,
        ),
      );
      if (event.data.response.recommendation) {
        setRecommendation(event.data.response.recommendation);
      }
      event.data.response.records_changed.forEach(invalidateLedger);
      break;
    case "error":
      setError(event.data.message);
      setActivity(event.data.message);
      setProgressSteps((steps) => markActiveProgressError(steps));
      break;
    case "done":
      setActivity(null);
      break;
  }
}

function createInitialProgressStep(): AgentProgressStep {
  return {
    id: "household",
    label: "Reading household",
    state: "active",
  };
}

function activateProgressStep(
  steps: AgentProgressStep[],
  id: string,
  label: string,
): AgentProgressStep[] {
  if (steps.some((step) => step.id === id && step.state === "active")) return steps;

  return [...completeActiveProgressSteps(steps), { id, label, state: "active" }];
}

function startToolProgressStep(steps: AgentProgressStep[], toolName: string): AgentProgressStep[] {
  const ordinal = steps.filter((step) => step.toolName === toolName).length + 1;
  return [
    ...completeActiveProgressSteps(steps),
    {
      id: `tool:${toolName}:${ordinal}`,
      label: toolProgressLabel(toolName),
      state: "active",
      toolName,
    },
  ];
}

function finishToolProgressStep(
  steps: AgentProgressStep[],
  toolName: string,
  ok: boolean,
): AgentProgressStep[] {
  for (let index = steps.length - 1; index >= 0; index -= 1) {
    const step = steps[index];
    if (step.toolName === toolName && step.state === "active") {
      return steps.map((candidate, candidateIndex) =>
        candidateIndex === index ? { ...candidate, state: ok ? "complete" : "error" } : candidate,
      );
    }
  }
  return steps;
}

function ensureRecommendationProgressStep(steps: AgentProgressStep[]): AgentProgressStep[] {
  if (steps.some((step) => step.id === "recommendation" && step.state === "active")) {
    return steps;
  }

  return activateProgressStep(steps, "recommendation", "Preparing recommendation");
}

function completeActiveProgressSteps(steps: AgentProgressStep[]): AgentProgressStep[] {
  return steps.map((step) => (step.state === "active" ? { ...step, state: "complete" } : step));
}

function completeProgressSteps(steps: AgentProgressStep[]): AgentProgressStep[] {
  const completedSteps = completeActiveProgressSteps(steps);
  if (completedSteps.some((step) => step.id === "complete")) return completedSteps;
  return [...completedSteps, { id: "complete", label: "Complete", state: "complete" }];
}

function markActiveProgressError(steps: AgentProgressStep[]): AgentProgressStep[] {
  return steps.map((step) => (step.state === "active" ? { ...step, state: "error" } : step));
}

function parseRecommendation(data: Record<string, unknown> | null) {
  if (!data) return null;
  const result = ForecastRecommendationSchema.safeParse(data);
  return result.success ? result.data : null;
}

const ForecastRecommendationSchema = z.object({
  recommended_day: z.string(),
  expected_savings_php: z.string(),
  confidence: z.string(),
  provider: z.string(),
  amount_php: z.string(),
  is_mock: z.boolean(),
  disclaimer: z.string(),
});

function statusActivity(message: string) {
  const labels: Record<string, string> = {
    "Reviewing your request.": "Reviewing household cash flow.",
    "Using the household result to finish the answer.": "Preparing your recommendation.",
    "Reconnecting to the assistant.": "Restoring the household review.",
  };
  return labels[message] ?? "Reviewing household details.";
}

function toolActivity(toolName: string) {
  const labels: Record<string, string> = {
    create_remittance: "Preparing the remittance entry.",
    forecast_remittance: "Calling FXPilot.",
    get_budget_status: "Fetching envelope balances.",
    log_expense: "Preparing the expense entry.",
    search_transactions: "Reviewing recent expenses.",
    upcoming_bills: "Checking upcoming bills.",
  };
  return labels[toolName] ?? "Reviewing household details.";
}

function toolProgressLabel(toolName: string) {
  const labels: Record<string, string> = {
    create_remittance: "Preparing remittance entry",
    forecast_remittance: "Calling FXPilot",
    get_budget_status: "Fetching envelope balances",
    log_expense: "Preparing expense entry",
    search_transactions: "Reviewing recent expenses",
    upcoming_bills: "Checking upcoming bills",
  };
  return labels[toolName] ?? "Reviewing household details";
}

function createId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
}

function agentErrorMessage(error: unknown) {
  if (error instanceof Error && "status" in error) {
    const status = Number((error as { status?: number }).status);
    if (status === 429) return "The assistant is busy right now. Please try again in a moment.";
    if (status >= 500)
      return "The assistant is not available right now. Please try again in a moment.";
  }
  if (error instanceof TypeError) {
    return "We could not reach the assistant. Check the connection and try again.";
  }
  return "The assistant could not complete that request right now. Please try again.";
}

function readConversationId(householdId: string) {
  if (typeof window === "undefined") return undefined;
  const value = window.sessionStorage.getItem(conversationStorageKey(householdId));
  return value ?? undefined;
}

function persistConversationId(householdId: string, conversationId: string) {
  window.sessionStorage.setItem(conversationStorageKey(householdId), conversationId);
}
