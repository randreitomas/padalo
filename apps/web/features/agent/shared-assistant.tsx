"use client";

import { RefreshCw, Send, X } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { AgentProgress, type AgentProgressStep } from "@/features/agent/agent-progress";
import type { ChatMessage } from "@/features/agent/use-agent-chat";
import { cn } from "@/lib/utils";

type SharedAssistantProps = {
  activity: string | null;
  className?: string;
  error: string | null;
  isStreaming: boolean;
  messages: ChatMessage[];
  progressSteps: AgentProgressStep[];
  suggestedPrompts: readonly string[];
  onSend: (message: string) => Promise<void>;
  onRetry: () => Promise<void>;
};

const WELCOME_MESSAGE =
  "Hi, I'm here to help with envelope balances, bills, and spending for the Santos household. What would you like to know?";

export function SharedAssistant({
  activity,
  className,
  error,
  isStreaming,
  messages,
  progressSteps,
  suggestedPrompts,
  onSend,
  onRetry,
}: SharedAssistantProps) {
  const [draft, setDraft] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const conversationRef = useRef<HTMLDivElement>(null);
  const launcherRef = useRef<HTMLButtonElement>(null);
  const openedFromLauncherRef = useRef(false);

  useEffect(() => {
    if (!messages.length && !activity && progressSteps.length === 0) return;
    const conversation = conversationRef.current;
    if (!conversation) return;
    conversation.scrollTo({ top: conversation.scrollHeight, behavior: "smooth" });
  }, [activity, messages, progressSteps]);

  useEffect(() => {
    if (isStreaming) setIsOpen(true);
  }, [isStreaming]);

  useEffect(() => {
    if (isOpen) {
      if (!openedFromLauncherRef.current) return;

      const frame = window.requestAnimationFrame(() => {
        document.getElementById("padalo-assist-composer")?.focus();
      });
      return () => window.cancelAnimationFrame(frame);
    }

    if (!openedFromLauncherRef.current) return;

    const frame = window.requestAnimationFrame(() => {
      launcherRef.current?.focus();
      openedFromLauncherRef.current = false;
    });
    return () => window.cancelAnimationFrame(frame);
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setIsOpen(false);
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isStreaming) return;
    setDraft("");
    await onSend(message);
  }

  function handleOpen() {
    openedFromLauncherRef.current = true;
    setIsOpen(true);
  }

  return (
    <section aria-label="PadaloAssist" className={className}>
      {!isOpen ? (
        <button
          aria-controls="padalo-assist-panel"
          aria-expanded={false}
          className="fixed bottom-5 right-5 z-40 inline-flex h-10 items-center gap-2 rounded-full bg-[#172b25] px-4 text-xs font-semibold text-white shadow-[0_14px_28px_rgba(20,42,35,0.2)] transition duration-200 hover:bg-[#234137] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lagoon focus-visible:ring-offset-2 motion-reduce:transition-none sm:bottom-6 sm:right-6"
          ref={launcherRef}
          type="button"
          onClick={handleOpen}
        >
          <span aria-hidden="true" className="size-1.5 rounded-full bg-[#7ee2b8]" />
          Ask PadaloAssist
        </button>
      ) : (
        <aside
          aria-labelledby="assistant-heading"
          aria-modal="false"
          className={cn(
            "fixed bottom-4 right-4 z-40 flex h-[32rem] max-h-[calc(100dvh-2rem)] w-[calc(100vw-2rem)] max-w-[22rem] flex-col overflow-hidden rounded-lg border border-[#c8d8d2] bg-surface shadow-[0_18px_48px_rgba(20,42,35,0.22)] transition motion-reduce:transition-none sm:bottom-6 sm:right-6",
            className,
          )}
          id="padalo-assist-panel"
          role="dialog"
        >
          <header className="flex h-11 shrink-0 items-center justify-between bg-[#172b25] px-3.5 text-white">
            <div className="flex items-center gap-2">
              <span aria-hidden="true" className="size-1.5 rounded-full bg-[#7ee2b8]" />
              <h2 id="assistant-heading" className="text-xs font-semibold">
                PadaloAssist
              </h2>
            </div>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  aria-label="Close PadaloAssist"
                  className="-mr-1 inline-flex size-7 items-center justify-center rounded-sm text-white/75 transition hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white motion-reduce:transition-none"
                  type="button"
                  onClick={() => setIsOpen(false)}
                >
                  <X className="size-4" aria-hidden="true" />
                </button>
              </TooltipTrigger>
              <TooltipContent>Close assistant</TooltipContent>
            </Tooltip>
          </header>

          <div
            ref={conversationRef}
            aria-live="polite"
            aria-relevant="additions text"
            className="min-h-0 flex-1 space-y-3 overflow-y-auto px-3 py-3"
          >
            {messages.length === 0 ? (
              <div className="max-w-[88%] rounded-md bg-mist px-3 py-2 text-xs leading-5 text-ink">
                {WELCOME_MESSAGE}
              </div>
            ) : (
              messages.map((message) => {
                if (message.role === "assistant" && !message.content && isStreaming) return null;

                return (
                  <div
                    key={message.id}
                    className={cn(
                      "max-w-[88%] rounded-md px-3 py-2 text-xs leading-5",
                      message.role === "user"
                        ? "ml-auto bg-[#e1f1ec] text-[#176654]"
                        : "bg-mist text-ink",
                    )}
                  >
                    {message.content || "I could not complete that request."}
                  </div>
                );
              })
            )}

            {activity ? <p className="text-xs text-muted">{activity}</p> : null}

            <AgentProgress steps={progressSteps} />

            {error ? (
              <div className="rounded-md border border-coral/30 bg-[#fffafa] p-2.5" role="alert">
                <p className="text-xs leading-5 text-coral">{error}</p>
                <Button
                  className="mt-2 h-7 px-2 text-xs"
                  disabled={isStreaming}
                  size="sm"
                  type="button"
                  variant="secondary"
                  onClick={() => void onRetry()}
                >
                  <RefreshCw className="mr-1 size-3" aria-hidden="true" />
                  Try again
                </Button>
              </div>
            ) : null}
          </div>

          <div className="shrink-0 border-t border-line bg-surface px-3 py-2.5">
            <div className="mb-2 flex gap-1.5 overflow-x-auto pb-0.5" aria-label="Suggested questions">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  className="shrink-0 rounded-sm border border-line bg-canvas px-2 py-1 text-left text-[11px] leading-4 text-muted transition hover:border-lagoon/40 hover:text-lagoon focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-lagoon disabled:cursor-not-allowed disabled:opacity-60 motion-reduce:transition-none"
                  disabled={isStreaming}
                  type="button"
                  onClick={() => void onSend(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <form className="flex items-end gap-2" onSubmit={handleSubmit}>
              <Textarea
                aria-label="Message the Padalo assistant"
                className="h-9 min-h-0 resize-none py-2 text-xs leading-5"
                disabled={isStreaming}
                id="padalo-assist-composer"
                maxLength={2000}
                placeholder="Ask about a bill, envelope, or remittance"
                rows={1}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
              />
              <Button
                aria-label="Send message"
                className="h-9 shrink-0 px-3 text-xs"
                disabled={isStreaming || !draft.trim()}
                size="sm"
                type="submit"
              >
                <Send className="mr-1 size-3" aria-hidden="true" />
                Send
              </Button>
            </form>
          </div>
        </aside>
      )}
    </section>
  );
}
