"use client";

import {
  BadgeDollarSign,
  Building2,
  ChevronDown,
  ClipboardList,
  LayoutDashboard,
  PanelLeftClose,
  PanelLeftOpen,
  ReceiptText,
  Send,
  WalletCards,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { PadaloLogo } from "@/components/brand/padalo-logo";
import { useActiveHousehold } from "@/components/household-provider";
import { DemoMode } from "@/components/layout/demo-mode";
import { IconButton } from "@/components/ui/icon-button";
import { useHouseholds } from "@/hooks/use-ledger-data";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/remittances", label: "Remittances", icon: Send },
  { href: "/envelopes", label: "Envelopes", icon: WalletCards },
  { href: "/transactions", label: "Transactions", icon: ReceiptText },
  { href: "/bills", label: "Bills", icon: ClipboardList },
  { href: "/households", label: "Households", icon: Building2 },
];

function NavLinks({ mobile = false }: { mobile?: boolean }) {
  const pathname = usePathname();
  return (
    <nav
      className={cn(mobile ? "flex min-w-max gap-1 px-4 py-2" : "space-y-1 px-3 py-4")}
      aria-label="Primary navigation"
    >
      {navigation.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              mobile && "shrink-0",
              active ? "bg-mist text-lagoon" : "text-muted hover:bg-mist hover:text-ink",
            )}
          >
            <Icon className="size-4" aria-hidden="true" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

function HouseholdSwitcher() {
  const { householdId, setHouseholdId } = useActiveHousehold();
  const { data, isLoading } = useHouseholds();
  const households = useMemo(() => data?.items ?? [], [data?.items]);

  useEffect(() => {
    if (households.length > 0 && !households.some((household) => household.id === householdId)) {
      setHouseholdId(households[0].id);
    }
  }, [householdId, households, setHouseholdId]);

  return (
    <label className="relative block px-3 py-3">
      <span className="sr-only">Active household</span>
      <select
        className="h-10 w-full appearance-none rounded-md border border-line bg-surface px-3 pr-9 text-sm font-semibold text-ink outline-none focus:border-lagoon focus:ring-2 focus:ring-[#b9ded8]"
        value={householdId}
        onChange={(event) => setHouseholdId(event.target.value)}
        disabled={isLoading || households.length === 0}
      >
        {households.length === 0 ? <option value={householdId}>Demo household</option> : null}
        {households.map((household) => (
          <option key={household.id} value={household.id}>
            {household.name}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-6 top-1/2 size-4 -translate-y-1/2 text-muted" />
    </label>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div
      className={cn(
        "min-h-screen bg-canvas lg:grid lg:transition-[grid-template-columns] lg:duration-300 motion-reduce:lg:transition-none",
        isSidebarCollapsed
          ? "lg:grid-cols-[0_minmax(0,1fr)]"
          : "lg:grid-cols-[15.5rem_minmax(0,1fr)]",
      )}
    >
      <aside
        aria-hidden={isSidebarCollapsed}
        className={cn(
          "hidden min-h-screen w-[15.5rem] min-w-0 overflow-hidden border-r border-line bg-surface opacity-100 transition-[opacity,transform] duration-300 motion-reduce:transition-none lg:flex lg:flex-col",
          isSidebarCollapsed && "pointer-events-none -translate-x-full opacity-0",
        )}
        inert={isSidebarCollapsed}
      >
        <div className="flex items-center gap-3 px-5 py-5 text-ink">
          <Link href="/" className="flex min-w-0 flex-1 items-center gap-3">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-md border border-line bg-white">
              <PadaloLogo className="h-5" priority />
            </span>
            <span className="min-w-0">
              <span className="block text-base font-semibold">Padalo</span>
              <span className="block text-xs text-muted">Household ledger</span>
            </span>
          </Link>
          <IconButton
            aria-expanded={!isSidebarCollapsed}
            className="shrink-0"
            label="Hide sidebar"
            type="button"
            onClick={() => setIsSidebarCollapsed(true)}
          >
            <PanelLeftClose className="size-4" aria-hidden="true" />
          </IconButton>
        </div>
        <HouseholdSwitcher />
        <NavLinks />
        <div className="mt-auto space-y-3 border-t border-line p-4">
          <DemoMode />
          <div className="flex items-center gap-3 rounded-md bg-mist px-3 py-3">
            <BadgeDollarSign className="size-5 text-lagoon" aria-hidden="true" />
            <p className="text-xs leading-5 text-muted">
              Shared planning, clear context, and no judgment.
            </p>
          </div>
        </div>
      </aside>

      <div className="min-w-0">
        {isSidebarCollapsed ? (
          <div className="fixed left-4 top-4 z-30 hidden lg:block">
            <IconButton
              aria-expanded={!isSidebarCollapsed}
              className="border border-line bg-surface shadow-panel hover:bg-mist"
              label="Show sidebar"
              type="button"
              onClick={() => setIsSidebarCollapsed(false)}
            >
              <PanelLeftOpen className="size-4" aria-hidden="true" />
            </IconButton>
          </div>
        ) : null}
        <header className="border-b border-line bg-surface lg:hidden">
          <div className="flex h-16 items-center justify-between px-4">
            <Link href="/" className="flex items-center gap-2 text-ink">
              <span className="flex size-7 items-center justify-center rounded-md border border-line bg-white">
                <PadaloLogo className="h-3.5" priority />
              </span>
              <span className="text-sm font-semibold">Padalo</span>
            </Link>
            <div className="flex items-center gap-2">
              <DemoMode compact />
              <HouseholdSwitcher />
            </div>
          </div>
          <div className="overflow-x-auto border-t border-line">
            <NavLinks mobile />
          </div>
        </header>
        <main
          id="main-content"
          className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-9 lg:py-8"
        >
          {children}
        </main>
      </div>
    </div>
  );
}
