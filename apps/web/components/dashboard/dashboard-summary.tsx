import { KpiCard } from "@/components/dashboard/kpi-card";
import type { DashboardSummary as DashboardSummaryData } from "@/lib/api/types";
import { formatPhp } from "@/lib/utils";

export function DashboardSummary({ summary }: { summary: DashboardSummaryData }) {
  return (
    <section className="space-y-3" aria-label="Household summary">
      <KpiCard
        detail={`${formatPhp(summary.total_envelope_target_php)} allocated across envelopes`}
        emphasis="primary"
        label="Available balance"
        status="On track for the month"
        value={formatPhp(summary.total_envelope_balance_php)}
      />
      <div className="grid gap-3 sm:grid-cols-3">
        <KpiCard
          detail="Recorded household inflows"
          label="Total remitted"
          value={formatPhp(summary.total_remitted_php)}
        />
        <KpiCard
          detail={`${summary.upcoming_bill_count} scheduled commitment${summary.upcoming_bill_count === 1 ? "" : "s"}`}
          label="Upcoming bills"
          value={formatPhp(summary.total_upcoming_bills_php)}
        />
        <KpiCard
          detail="Expenses and ledger adjustments"
          label="Spent this month"
          value={formatPhp(summary.total_spent_this_month_php)}
        />
      </div>
    </section>
  );
}
