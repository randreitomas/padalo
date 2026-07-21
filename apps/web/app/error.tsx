"use client";

import { ErrorState } from "@/components/ui/state-panel";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main
      id="main-content"
      className="flex min-h-dvh items-center justify-center bg-canvas px-5"
    >
      <ErrorState
        title="Padalo needs another moment"
        description="The page could not be loaded. Nothing was changed in the household record."
        onRetry={reset}
      />
    </main>
  );
}
