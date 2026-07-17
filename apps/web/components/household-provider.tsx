"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

const LOCAL_STORAGE_KEY = "padalo.active-household";
const defaultHouseholdId =
  process.env.NEXT_PUBLIC_DEMO_HOUSEHOLD_ID ?? "cccccccc-cccc-4ccc-8ccc-cccccccccccc";

type HouseholdContextValue = {
  householdId: string;
  setHouseholdId: (householdId: string) => void;
};

const HouseholdContext = createContext<HouseholdContextValue | null>(null);

export function HouseholdProvider({ children }: { children: React.ReactNode }) {
  const [householdId, setHouseholdId] = useState(defaultHouseholdId);

  useEffect(() => {
    const storedHouseholdId = window.localStorage.getItem(LOCAL_STORAGE_KEY);
    if (storedHouseholdId) setHouseholdId(storedHouseholdId);
  }, []);

  const value = useMemo(
    () => ({
      householdId,
      setHouseholdId: (nextHouseholdId: string) => {
        window.localStorage.setItem(LOCAL_STORAGE_KEY, nextHouseholdId);
        setHouseholdId(nextHouseholdId);
      },
    }),
    [householdId],
  );

  return <HouseholdContext.Provider value={value}>{children}</HouseholdContext.Provider>;
}

export function useActiveHousehold() {
  const context = useContext(HouseholdContext);
  if (!context) throw new Error("useActiveHousehold must be used inside HouseholdProvider.");
  return context;
}
