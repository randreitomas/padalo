import { AlertCircle, Inbox } from "lucide-react";
import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";

type StatePanelProps = {
  title: string;
  description: string;
  action?: ReactNode;
  onRetry?: () => void;
};

export function EmptyState({ title, description, action }: Omit<StatePanelProps, "onRetry">) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center border border-dashed border-line px-6 py-10 text-center">
      <Inbox className="mb-3 size-6 text-lagoon" aria-hidden="true" />
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      <p className="mt-1 max-w-sm text-sm leading-6 text-muted">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function ErrorState({ title, description, onRetry }: StatePanelProps) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center border border-dashed border-[#e5bbb1] bg-[#fffafa] px-6 py-10 text-center">
      <AlertCircle className="mb-3 size-6 text-coral" aria-hidden="true" />
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      <p className="mt-1 max-w-sm text-sm leading-6 text-muted">{description}</p>
      {onRetry ? (
        <Button className="mt-4" variant="secondary" size="sm" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}
