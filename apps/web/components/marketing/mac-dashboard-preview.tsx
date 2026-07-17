import {
  ArrowUpRight,
  Bot,
  CalendarDays,
  ChartNoAxesCombined,
  Check,
  ChevronRight,
  Sparkles,
  WalletCards,
} from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type MacDashboardPreviewProps = {
  className?: string;
  variant: "hero" | "overview" | "assist" | "fxpilot";
};

type WindowProps = {
  children: ReactNode;
  className?: string;
  title: string;
};

function Window({ children, className, title }: WindowProps) {
  return (
    <figure
      aria-label={title}
      className={cn(
        "overflow-hidden rounded-[18px] border border-[#d8dfdc] bg-[#f7f9f8] shadow-[0_22px_70px_rgba(24,37,32,0.12)]",
        className,
      )}
    >
      <div className="flex h-9 items-center border-b border-[#e3e8e5] bg-white/85 px-3 sm:px-4">
        <div aria-hidden="true" className="flex items-center gap-1.5">
          <span className="size-2 rounded-full bg-[#ff5f57]" />
          <span className="size-2 rounded-full bg-[#febc2e]" />
          <span className="size-2 rounded-full bg-[#28c840]" />
        </div>
        <span className="ml-3 truncate text-[10px] font-semibold text-[#66736e] sm:text-[11px]">
          {title}
        </span>
        <span className="ml-auto hidden text-[10px] font-medium text-lagoon sm:inline">
          Live view
        </span>
      </div>
      {children}
    </figure>
  );
}

function SmallMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-[#e2e8e5] bg-white px-3 py-2.5">
      <p className="text-[10px] font-medium text-[#71807a]">{label}</p>
      <p className="mt-1 text-sm font-bold tracking-tight text-[#1b2924]">{value}</p>
    </div>
  );
}

function BudgetLine({ label, amount, value }: { label: string; amount: string; value: string }) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-3 text-[10px]">
        <span className="font-medium text-[#41524c]">{label}</span>
        <span className="font-semibold text-[#1f302a]">{amount}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-[#e6ece9]">
        <div className="h-full rounded-full bg-lagoon" style={{ width: value }} />
      </div>
    </div>
  );
}

function HeroPreview() {
  return (
    <Window title="Padalo · Santos household">
      <div className="grid gap-3 p-3 sm:p-4 lg:grid-cols-[1.32fr_0.68fr]">
        <section className="rounded-lg bg-[#17312a] p-4 text-white sm:p-5">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#c6dfd8]">
            Santos household
          </p>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs text-[#d5e5df]">Available this month</p>
              <p className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">P24,381</p>
            </div>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-2.5 py-1 text-[10px] font-semibold text-[#d8f3e9]">
              <Check className="size-3" aria-hidden="true" />
              On track
            </span>
          </div>
          <div className="mt-5 grid grid-cols-3 gap-2 border-t border-white/10 pt-4 text-[10px] text-[#c7d9d3]">
            <div>
              <p>Sent home</p>
              <p className="mt-1 text-xs font-bold text-white">P38,000</p>
            </div>
            <div>
              <p>Due soon</p>
              <p className="mt-1 text-xs font-bold text-white">P12,469</p>
            </div>
            <div>
              <p>Spent</p>
              <p className="mt-1 text-xs font-bold text-white">P13,619</p>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-[#d9e5df] bg-[#eaf4ef] p-4 sm:p-5">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-[#176b58]">
              <Sparkles className="size-3.5" aria-hidden="true" />
              <p className="text-[10px] font-bold uppercase tracking-[0.1em]">FXPilot</p>
            </div>
            <ArrowUpRight className="size-3.5 text-[#176b58]" aria-hidden="true" />
          </div>
          <p className="mt-5 text-xs font-medium text-[#53645d]">Recommended day</p>
          <p className="mt-1 text-2xl font-bold tracking-tight text-[#17312a]">Thursday</p>
          <p className="mt-3 text-[10px] leading-4 text-[#587067]">
            Historically lower provider fees in this payday window.
          </p>
        </section>

        <section className="rounded-lg border border-[#e1e7e4] bg-white p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="flex size-6 items-center justify-center rounded-md bg-[#e7f3ef] text-lagoon">
                <WalletCards className="size-3.5" aria-hidden="true" />
              </span>
              <p className="text-xs font-bold text-[#263830]">Envelope balances</p>
            </div>
            <span className="text-[10px] font-semibold text-lagoon">View all</span>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <BudgetLine label="Groceries" amount="P5,350" value="67%" />
            <BudgetLine label="Education" amount="P6,250" value="52%" />
            <BudgetLine label="Bills" amount="P2,481" value="50%" />
            <BudgetLine label="Savings" amount="P8,000" value="80%" />
          </div>
        </section>

        <section className="rounded-lg border border-[#e1e7e4] bg-white p-4 sm:p-5">
          <div className="flex items-center gap-2">
            <span className="flex size-6 items-center justify-center rounded-md bg-[#edf0ff] text-[#5367b8]">
              <Bot className="size-3.5" aria-hidden="true" />
            </span>
            <p className="text-xs font-bold text-[#263830]">PadaloAssist</p>
          </div>
          <p className="mt-4 max-w-[240px] rounded-md bg-[#f1f5f3] px-3 py-2 text-[10px] leading-4 text-[#52615b]">
            Can we still afford tuition this month?
          </p>
          <p className="ml-auto mt-2 max-w-[210px] rounded-md bg-[#dff0ea] px-3 py-2 text-[10px] leading-4 text-[#176554]">
            Yes. P2,481 remains after the Meralco bill.
          </p>
        </section>
      </div>
    </Window>
  );
}

function OverviewPreview() {
  return (
    <Window className="h-full" title="Padalo · Household overview">
      <div className="flex h-full flex-col p-3 sm:p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-medium text-[#71807a]">Household overview</p>
            <p className="mt-1 text-lg font-bold tracking-tight text-[#1b2924]">
              Clear at a glance.
            </p>
          </div>
          <span className="rounded-full bg-[#e7f3ef] px-2 py-1 text-[9px] font-bold text-lagoon">
            July
          </span>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2">
          <SmallMetric label="Available" value="P24,381" />
          <SmallMetric label="Bills due" value="P12,469" />
          <SmallMetric label="Spent" value="P13,619" />
          <SmallMetric label="Remitted" value="P38,000" />
        </div>
        <div className="mt-3 flex-1 rounded-md border border-[#dce7e2] bg-[#f3f8f6] p-3">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-bold text-[#2a4038]">Budget health</p>
            <ChartNoAxesCombined className="size-3.5 text-lagoon" aria-hidden="true" />
          </div>
          <div className="mt-4 space-y-3">
            <BudgetLine label="Groceries" amount="67% left" value="67%" />
            <BudgetLine label="Education" amount="52% left" value="52%" />
            <BudgetLine label="Savings" amount="80% left" value="80%" />
          </div>
        </div>
      </div>
    </Window>
  );
}

function AssistPreview() {
  return (
    <Window className="h-full" title="Padalo · Ask anything">
      <div className="flex h-full flex-col p-3 sm:p-4">
        <div className="flex items-center gap-2">
          <span className="flex size-7 items-center justify-center rounded-md bg-[#e7f3ef] text-lagoon">
            <Bot className="size-3.5" aria-hidden="true" />
          </span>
          <div>
            <p className="text-[10px] font-bold text-[#263830]">PadaloAssist</p>
            <p className="text-[9px] text-[#71807a]">Household context, clearly explained</p>
          </div>
        </div>
        <div className="mt-5 space-y-2.5 text-[10px] leading-4">
          <p className="max-w-[88%] rounded-md bg-[#eff4f2] px-3 py-2 text-[#52615b]">
            Can we still afford tuition this month?
          </p>
          <p className="ml-auto max-w-[82%] rounded-md bg-[#dff0ea] px-3 py-2 text-[#176554]">
            Check our bills first.
          </p>
          <p className="max-w-[90%] rounded-md bg-[#eff4f2] px-3 py-2 text-[#52615b]">
            Yes. After Meralco and Converge, P2,481 stays in the Bills envelope.
          </p>
        </div>
        <div className="mt-auto flex items-center justify-between rounded-md border border-[#dbe5e1] bg-white px-3 py-2 text-[10px] text-[#71807a]">
          <span>Ask about a bill or envelope</span>
          <ChevronRight className="size-3.5 text-lagoon" aria-hidden="true" />
        </div>
      </div>
    </Window>
  );
}

function FxPilotPreview() {
  return (
    <Window className="h-full" title="Padalo · FXPilot">
      <div className="flex h-full flex-col p-3 sm:p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-md bg-[#fcf3da] text-[#9b6c00]">
              <CalendarDays className="size-3.5" aria-hidden="true" />
            </span>
            <p className="text-[10px] font-bold text-[#263830]">FXPilot</p>
          </div>
          <span className="text-[9px] font-bold text-lagoon">85% confidence</span>
        </div>
        <div className="mt-5 rounded-md bg-[#183129] p-4 text-white">
          <p className="text-[10px] text-[#c9dfd7]">Recommended day</p>
          <p className="mt-1 text-3xl font-bold tracking-tight">Thursday</p>
          <p className="mt-3 text-[10px] leading-4 text-[#d7e8e2]">Estimated savings: P112</p>
        </div>
        <div className="mt-4 flex items-end gap-2 px-1">
          {[38, 52, 44, 70, 58, 46, 34].map((height, index) => (
            <div key={height} className="flex flex-1 flex-col items-center gap-1">
              <div
                className={cn("w-full rounded-t-sm bg-[#dce7e3]", index === 3 && "bg-lagoon")}
                style={{ height }}
              />
              <span className="text-[8px] text-[#7a8983]">
                {["M", "T", "W", "T", "F", "S", "S"][index]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </Window>
  );
}

export function MacDashboardPreview({ className, variant }: MacDashboardPreviewProps) {
  return (
    <div className={className}>
      {variant === "hero" ? <HeroPreview /> : null}
      {variant === "overview" ? <OverviewPreview /> : null}
      {variant === "assist" ? <AssistPreview /> : null}
      {variant === "fxpilot" ? <FxPilotPreview /> : null}
    </div>
  );
}
