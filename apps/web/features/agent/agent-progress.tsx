import { Check, Circle, LoaderCircle, TriangleAlert } from "lucide-react";

import { cn } from "@/lib/utils";

export type AgentProgressState = "active" | "complete" | "error" | "pending";

export type AgentProgressStep = {
  id: string;
  label: string;
  state: AgentProgressState;
  toolName?: string;
};

type AgentProgressProps = {
  steps: AgentProgressStep[];
};

export function AgentProgress({ steps }: AgentProgressProps) {
  if (steps.length === 0) return null;

  const activeStep = steps.find((step) => step.state === "active");

  return (
    <section aria-label="Household review progress" className="border-y border-line py-3">
      <p className="sr-only" aria-live="polite">
        {activeStep?.label ?? steps.at(-1)?.label}
      </p>
      <ol className="grid gap-2 sm:grid-cols-2">
        {steps.map((step) => (
          <li key={step.id} className="flex min-w-0 items-center gap-2 text-xs leading-5">
            <ProgressIcon state={step.state} />
            <span
              className={cn(
                "min-w-0",
                step.state === "active" && "font-semibold text-ink",
                step.state === "complete" && "text-muted",
                step.state === "error" && "text-coral",
                step.state === "pending" && "text-muted",
              )}
            >
              {step.label}
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}

function ProgressIcon({ state }: { state: AgentProgressState }) {
  if (state === "complete") {
    return <Check className="size-3.5 shrink-0 text-lagoon" aria-hidden="true" />;
  }
  if (state === "active") {
    return (
      <LoaderCircle className="size-3.5 shrink-0 animate-spin text-lagoon" aria-hidden="true" />
    );
  }
  if (state === "error") {
    return <TriangleAlert className="size-3.5 shrink-0 text-coral" aria-hidden="true" />;
  }
  return <Circle className="size-3.5 shrink-0 text-line" aria-hidden="true" />;
}
