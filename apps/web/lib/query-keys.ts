export const queryKeys = {
  households: ["households"] as const,
  household: (householdId: string) => ["households", householdId] as const,
  dashboard: (householdId: string) => ["dashboard", householdId] as const,
  envelopes: (householdId: string) => ["envelopes", householdId] as const,
  transactions: (householdId: string) => ["transactions", householdId] as const,
  remittances: (householdId: string) => ["remittances", householdId] as const,
  bills: (householdId: string) => ["bills", householdId] as const,
};
