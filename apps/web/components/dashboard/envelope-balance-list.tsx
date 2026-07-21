import { Card, CardContent } from "@/components/ui/card";
import type { Envelope } from "@/lib/api/types";
import { cn, formatPhp } from "@/lib/utils";

export function EnvelopeBalanceList({ envelopes }: { envelopes: Envelope[] }) {
  return (
    <Card className="shadow-none">
      <CardContent className="pt-5">
        <ul className="grid gap-x-7 gap-y-5 sm:grid-cols-2 xl:grid-cols-3" role="list">
          {envelopes.map((envelope) => {
            const target = Number(envelope.target_amount_php);
            const balance = Number(envelope.current_balance_php);
            const percent = target > 0 ? Math.min(100, Math.max(0, (balance / target) * 100)) : 0;
            const low = target > 0 && percent < 25;

            return (
              <li key={envelope.id}>
                <div className="flex items-baseline justify-between gap-3">
                  <p className="truncate text-sm font-semibold text-ink">{envelope.name}</p>
                  <p
                    className={cn(
                      "shrink-0 text-sm font-medium tabular-nums",
                      low ? "text-coral" : "text-muted",
                    )}
                  >
                    {formatPhp(envelope.current_balance_php)}
                  </p>
                </div>
                <div
                  aria-label={`${envelope.name}: ${percent.toFixed(0)}% remaining`}
                  className="mt-2 h-1.5 overflow-hidden rounded bg-[#e8efed]"
                >
                  <div
                    className={cn("h-full rounded", low ? "bg-coral" : "bg-lagoon")}
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      </CardContent>
    </Card>
  );
}
