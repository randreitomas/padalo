"use client";

import { Sparkles, X } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

const DISMISSAL_STORAGE_KEY = "padalo.demo-welcome-dismissed";

export function DemoWelcome() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(window.localStorage.getItem(DISMISSAL_STORAGE_KEY) !== "true");
  }, []);

  function dismiss() {
    window.localStorage.setItem(DISMISSAL_STORAGE_KEY, "true");
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <section
      aria-labelledby="demo-welcome-heading"
      className="flex items-start justify-between gap-4 border border-[#bdd9d3] bg-mist px-5 py-4 transition-colors"
    >
      <div className="flex min-w-0 gap-3">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-md bg-surface text-lagoon shadow-panel">
          <Sparkles className="size-4" aria-hidden="true" />
        </span>
        <div>
          <h2 id="demo-welcome-heading" className="text-base font-semibold text-ink">
            Welcome to Padalo
          </h2>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-muted">
            Padalo helps OFW families coordinate remittances, household budgets, bills, and savings
            with AI. Try asking one of the suggested questions below.
          </p>
        </div>
      </div>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            aria-label="Dismiss welcome message"
            className="-mr-2 -mt-2 shrink-0"
            size="icon"
            type="button"
            variant="ghost"
            onClick={dismiss}
          >
            <X className="size-4" aria-hidden="true" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Dismiss welcome message</TooltipContent>
      </Tooltip>
    </section>
  );
}
