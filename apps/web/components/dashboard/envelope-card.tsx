import { WalletCards } from "lucide-react";
import type { ReactNode } from "react";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { Envelope } from "@/lib/api/types";
import { cn, formatPhp } from "@/lib/utils";

export function EnvelopeCard({ envelope, actions }: { envelope: Envelope; actions?: ReactNode }) {
  const target = Number(envelope.target_amount_php);
  const balance = Number(envelope.current_balance_php);
  const percent = target > 0 ? Math.min(100, Math.max(0, (balance / target) * 100)) : 0;
  const low = target > 0 && percent < 25;

  return (
    <Card className="min-w-0">
      <CardHeader className="pb-2">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-ink">{envelope.name}</p>
          <p className="mt-1 text-xs text-muted">
            of {formatPhp(envelope.target_amount_php)} allocated
          </p>
        </div>
        {actions ?? <WalletCards className="size-4 shrink-0 text-lagoon" aria-hidden="true" />}
      </CardHeader>
      <CardContent>
        <p className="text-xl font-semibold tabular-nums text-ink">
          {formatPhp(envelope.current_balance_php)}
        </p>
        <div
          className="mt-4 h-2 overflow-hidden rounded bg-[#e8efed]"
          aria-label={`${percent.toFixed(0)}% remaining`}
        >
          <div
            className={cn("h-full rounded", low ? "bg-coral" : "bg-lagoon")}
            style={{ width: `${percent}%` }}
          />
        </div>
        <p className={cn("mt-2 text-xs", low ? "text-coral" : "text-muted")}>
          {percent.toFixed(0)}% remaining
        </p>
      </CardContent>
    </Card>
  );
}
