"use client";

import { ErrorState } from "@/components/ui/state-panel";

export default function DashboardError({ reset }: { error: Error; reset: () => void }) {
  return (
    <ErrorState
      title="This workspace could not be opened"
      description="The dashboard is taking longer than expected. Please try again."
      onRetry={reset}
    />
  );
}
