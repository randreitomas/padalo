import type { ReactNode } from "react";

import { Label } from "@/components/ui/label";

export function FormField({
  id,
  label,
  error,
  children,
}: {
  id: string;
  label: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id}>{label}</Label>
      {children}
      {error ? <p className="text-xs text-coral">{error}</p> : null}
    </div>
  );
}
