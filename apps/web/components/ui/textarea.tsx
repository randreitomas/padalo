import type { TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={cn(
        "flex min-h-20 w-full resize-y rounded-md border border-line bg-surface px-3 py-2 text-sm text-ink outline-none placeholder:text-muted focus:border-lagoon focus:ring-2 focus:ring-[#b9ded8] disabled:cursor-not-allowed disabled:opacity-60",
        className,
      )}
      {...props}
    />
  );
}
