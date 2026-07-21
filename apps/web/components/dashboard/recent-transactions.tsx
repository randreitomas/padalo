import { ArrowDownRight, ArrowUpRight, Plus, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/state-panel";
import type { Transaction } from "@/lib/api/types";
import { formatDate, formatPhp } from "@/lib/utils";

const labels = {
  expense: "Expense",
  refund: "Refund",
  adjustment: "Adjustment",
};

export function RecentTransactions({ transactions }: { transactions: Transaction[] }) {
  return (
    <section aria-labelledby="recent-transactions-heading">
      <Card className="h-full shadow-none">
        <CardHeader>
          <div>
            <h2 id="recent-transactions-heading" className="text-base font-semibold text-ink">
              Recent transactions
            </h2>
            <p className="mt-1 text-sm text-muted">Latest activity in this household.</p>
          </div>
          <Button asChild variant="ghost" size="sm">
            <Link href="/transactions">
              <SlidersHorizontal className="size-3.5" aria-hidden="true" />
              View all
            </Link>
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          {transactions.length === 0 ? (
            <EmptyState
              title="No expenses recorded"
              description="Record a household expense to keep shared envelope balances up to date."
              action={
                <Button asChild size="sm">
                  <Link href="/transactions">
                    <Plus className="size-3.5" aria-hidden="true" />
                    Add expense
                  </Link>
                </Button>
              }
            />
          ) : (
            <ul className="divide-y divide-line" role="list">
              {transactions.map((transaction) => {
                const credit = transaction.transaction_type === "refund";
                return (
                  <li key={transaction.id} className="flex items-center gap-3 px-5 py-4">
                    <span className={credit ? "text-lagoon" : "text-coral"}>
                      {credit ? (
                        <ArrowUpRight className="size-4" aria-hidden="true" />
                      ) : (
                        <ArrowDownRight className="size-4" aria-hidden="true" />
                      )}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-ink">
                        {transaction.merchant ?? transaction.note ?? "Recorded transaction"}
                      </p>
                      <p className="mt-1 text-xs text-muted">
                        {formatDate(transaction.occurred_on)}
                      </p>
                    </div>
                    <Badge variant={credit ? "success" : "neutral"}>
                      {labels[transaction.transaction_type]}
                    </Badge>
                    <p
                      className={
                        credit
                          ? "text-sm font-semibold tabular-nums text-lagoon"
                          : "text-sm font-semibold tabular-nums text-ink"
                      }
                    >
                      {credit ? "+" : "-"}
                      {formatPhp(transaction.amount_php)}
                    </p>
                  </li>
                );
              })}
            </ul>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
