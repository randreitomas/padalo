"use client";

import { LoaderCircle, RotateCcw } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ApiError, api } from "@/lib/api/client";

const DEMO_HOUSEHOLD_KEY = "padalo.active-household";
const WELCOME_KEY = "padalo.demo-welcome-dismissed";
const CONVERSATION_KEY_PREFIX = "padalo-agent-conversation:";

export function DemoMode({ compact = false }: { compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (process.env.NEXT_PUBLIC_DEMO_MODE !== "true") return null;

  async function resetDemo() {
    setError(null);
    setIsResetting(true);

    try {
      await api.resetDemo();
      clearBrowserDemoState();
      window.location.assign("/dashboard");
    } catch (resetError) {
      setError(
        resetError instanceof ApiError
          ? resetError.message
          : "The demo household could not be reset. Try again in a moment.",
      );
      setIsResetting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {compact ? (
          <Button size="sm" type="button" variant="ghost">
            <RotateCcw className="size-3.5" aria-hidden="true" />
            Reset demo
          </Button>
        ) : (
          <Button
            aria-label="Reset the Santos Family demo"
            className="h-auto w-full justify-between px-3 py-3 text-left"
            type="button"
            variant="secondary"
          >
            <div>
              <p className="text-xs font-semibold text-ink">Demo mode</p>
              <p className="mt-1 text-xs leading-5 text-muted">Restore Santos Family</p>
            </div>
            <span className="flex size-9 items-center justify-center rounded-md text-muted">
              <RotateCcw className="size-4" aria-hidden="true" />
            </span>
          </Button>
        )}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-ink">Reset the demo?</DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            This restores the original Santos Family records, clears this browser&apos;s
            conversation, and returns to the dashboard. Other households are not changed.
          </DialogDescription>
        </DialogHeader>
        {error ? (
          <p
            className="rounded-md border border-[#e5bbb1] bg-[#fffafa] px-3 py-2 text-sm leading-6 text-coral"
            role="alert"
          >
            {error}
          </p>
        ) : null}
        <DialogFooter>
          <Button
            disabled={isResetting}
            type="button"
            variant="secondary"
            onClick={() => setOpen(false)}
          >
            Keep current demo
          </Button>
          <Button disabled={isResetting} type="button" onClick={() => void resetDemo()}>
            {isResetting ? (
              <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
            ) : (
              <RotateCcw className="size-4" aria-hidden="true" />
            )}
            Restore demo
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function clearBrowserDemoState() {
  window.localStorage.removeItem(DEMO_HOUSEHOLD_KEY);
  window.localStorage.removeItem(WELCOME_KEY);

  for (let index = window.sessionStorage.length - 1; index >= 0; index -= 1) {
    const key = window.sessionStorage.key(index);
    if (key?.startsWith(CONVERSATION_KEY_PREFIX)) window.sessionStorage.removeItem(key);
  }
}
