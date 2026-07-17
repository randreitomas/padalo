"use client";

import { useActiveHousehold } from "@/components/household-provider";
import { DEMO_AGENT_PROMPTS } from "@/features/agent/demo-prompts";
import { FxPilotRecommendation } from "@/features/agent/fxpilot-recommendation";
import { SharedAssistant } from "@/features/agent/shared-assistant";
import { useAgentChat } from "@/features/agent/use-agent-chat";

type AgentExperienceProps = {
  assistantClassName?: string;
  fxPilotClassName?: string;
};

export function AgentExperience({ assistantClassName, fxPilotClassName }: AgentExperienceProps) {
  const { householdId } = useActiveHousehold();
  const agent = useAgentChat(householdId);

  return (
    <>
      <FxPilotRecommendation className={fxPilotClassName} recommendation={agent.recommendation} />
      <SharedAssistant
        activity={agent.activity}
        className={assistantClassName}
        error={agent.error}
        isStreaming={agent.isStreaming}
        messages={agent.messages}
        progressSteps={agent.progressSteps}
        suggestedPrompts={DEMO_AGENT_PROMPTS}
        onSend={agent.sendMessage}
        onRetry={agent.retryLastMessage}
      />
    </>
  );
}
