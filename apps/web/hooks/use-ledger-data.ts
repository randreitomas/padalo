"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api/client";
import { queryKeys } from "@/lib/query-keys";

export function useHouseholds() {
  return useQuery({ queryKey: queryKeys.households, queryFn: api.listHouseholds });
}

export function useDashboard(householdId: string) {
  return useQuery({
    queryKey: queryKeys.dashboard(householdId),
    queryFn: () => api.getDashboard(householdId),
    enabled: Boolean(householdId),
  });
}

export function useEnvelopes(householdId: string) {
  return useQuery({
    queryKey: queryKeys.envelopes(householdId),
    queryFn: () => api.listEnvelopes(householdId),
    enabled: Boolean(householdId),
  });
}

export function useTransactions(householdId: string) {
  return useQuery({
    queryKey: queryKeys.transactions(householdId),
    queryFn: () => api.listTransactions(householdId),
    enabled: Boolean(householdId),
  });
}

export function useBills(householdId: string) {
  return useQuery({
    queryKey: queryKeys.bills(householdId),
    queryFn: () => api.listBills(householdId),
    enabled: Boolean(householdId),
  });
}

export function useRemittances(householdId: string) {
  return useQuery({
    queryKey: queryKeys.remittances(householdId),
    queryFn: () => api.listRemittances(householdId),
    enabled: Boolean(householdId),
  });
}
