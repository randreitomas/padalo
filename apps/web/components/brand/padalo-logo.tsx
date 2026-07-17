import Image from "next/image";

import { cn } from "@/lib/utils";

type PadaloLogoProps = {
  className?: string;
  priority?: boolean;
};

export function PadaloLogo({ className, priority = false }: PadaloLogoProps) {
  return (
    <Image
      alt=""
      aria-hidden="true"
      className={cn("h-7 w-auto", className)}
      height={1317}
      priority={priority}
      src="/brand/padalo-logo.svg"
      width={1199}
    />
  );
}
