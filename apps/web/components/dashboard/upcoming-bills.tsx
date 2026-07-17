import { CalendarDays, ChevronRight, Plus } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/state-panel";
import type { Bill } from "@/lib/api/types";
import { formatDate, formatPhp } from "@/lib/utils";

export function UpcomingBills({ bills }: { bills: Bill[] }) {
  return (
    <section aria-labelledby="upcoming-bills-heading">
      <Card className="h-full shadow-none">
        <CardHeader>
          <div>
            <h2 id="upcoming-bills-heading" className="text-base font-semibold text-ink">
              Upcoming bills
            </h2>
            <p className="mt-1 text-sm text-muted">Scheduled commitments in the next window.</p>
          </div>
          <Button asChild variant="ghost" size="sm">
            <Link href="/bills">
              Manage
              <ChevronRight className="size-3.5" aria-hidden="true" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          {bills.length === 0 ? (
            <EmptyState
              title="No upcoming bills"
              description="Add a scheduled bill to keep the household's next commitments visible."
              action={
                <Button asChild size="sm">
                  <Link href="/bills">
                    <Plus className="size-3.5" aria-hidden="true" />
                    Add bill
                  </Link>
                </Button>
              }
            />
          ) : (
            <ul className="divide-y divide-line" role="list">
              {bills.map((bill) => (
                <li key={bill.id} className="flex items-center gap-3 px-5 py-4">
                  <span className="flex size-8 items-center justify-center rounded-md bg-[#f8edd1] text-gold">
                    <CalendarDays className="size-4" aria-hidden="true" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-ink">{bill.name}</p>
                    <p className="mt-1 text-xs text-muted">Due {formatDate(bill.due_date)}</p>
                  </div>
                  {bill.recurring ? <Badge variant="info">Recurring</Badge> : null}
                  <p className="text-sm font-semibold text-ink">{formatPhp(bill.amount_php)}</p>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
