"use client";

import { ArrowDownToLine, Plus } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";

import { DashboardSummary } from "@/components/dashboard/dashboard-summary";
import { DemoWelcome } from "@/components/dashboard/demo-welcome";
import { EnvelopeBalanceList } from "@/components/dashboard/envelope-balance-list";
import { DashboardSkeleton } from "@/components/dashboard/dashboard-skeleton";
import { RecentTransactions } from "@/components/dashboard/recent-transactions";
import { UpcomingBills } from "@/components/dashboard/upcoming-bills";
import { useActiveHousehold } from "@/components/household-provider";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState, EmptyState } from "@/components/ui/state-panel";
import { useDashboard } from "@/hooks/use-ledger-data";

const AgentExperience = dynamic(
  () => import("@/features/agent/agent-experience").then((module) => module.AgentExperience),
  {
    loading: () => <div className="order-1 h-20 animate-pulse rounded-md border border-line bg-surface" />,
    ssr: false,
  },
);

export function DashboardPage() {
  const { householdId } = useActiveHousehold();
  const dashboard = useDashboard(householdId);

  if (dashboard.isLoading) return <DashboardSkeleton />;

  if (dashboard.isError) {
    return (
      <ErrorState
        title="The household summary is unavailable"
        description="Check that the FastAPI service is running and that this household exists in the configured database."
        onRetry={() => dashboard.refetch()}
      />
    );
  }

  const summary = dashboard.data;
  if (!summary) return null;

  return (
    <div className="mx-auto flex max-w-[1180px] flex-col gap-5">
      <PageHeader
        eyebrow="Household overview"
        title={summary.household.name}
        description="A shared view of the money allocated, spent, received, and due next."
        actions={
          <>
            <Button asChild variant="secondary" size="sm">
              <Link href="/remittances">
                <ArrowDownToLine className="size-3.5" aria-hidden="true" />
                Add remittance
              </Link>
            </Button>
            <Button asChild size="sm">
              <Link href="/transactions">
                <Plus className="size-3.5" aria-hidden="true" />
                Add expense
              </Link>
            </Button>
          </>
        }
      />

      <DemoWelcome />

      <DashboardSummary summary={summary} />

      <AgentExperience assistantClassName="order-4" fxPilotClassName="order-1" />

      <section aria-labelledby="envelope-heading" className="order-2">
        <div className="mb-3 flex items-end justify-between gap-4">
          <div>
            <h2 id="envelope-heading" className="text-base font-semibold text-ink">
              Envelope balances
            </h2>
            <p className="mt-1 text-sm text-muted">
              What remains available in each shared category.
            </p>
          </div>
          <Button asChild variant="ghost" size="sm">
            <Link href="/envelopes">Manage envelopes</Link>
          </Button>
        </div>
        {summary.envelopes.length === 0 ? (
          <EmptyState
            title="No envelopes yet"
            description="Set up a shared budget envelope to begin tracking remaining funds."
            action={
              <Button asChild size="sm">
                <Link href="/envelopes">Create envelope</Link>
              </Button>
            }
          />
        ) : (
          <EnvelopeBalanceList envelopes={summary.envelopes} />
        )}
      </section>

      <div className="order-3 grid gap-4 lg:grid-cols-2">
        <RecentTransactions transactions={summary.recent_transactions} />
        <UpcomingBills bills={summary.upcoming_bills} />
      </div>
    </div>
  );
}
