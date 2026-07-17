import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center rounded px-2 py-1 text-xs font-semibold", {
  variants: {
    variant: {
      neutral: "bg-[#edf1f0] text-muted",
      success: "bg-[#dff1eb] text-[#16624e]",
      warning: "bg-[#f8edd1] text-[#8b5b00]",
      danger: "bg-[#f9e5e1] text-[#a33b28]",
      info: "bg-[#e4eff6] text-[#245d83]",
    },
  },
  defaultVariants: { variant: "neutral" },
});

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
