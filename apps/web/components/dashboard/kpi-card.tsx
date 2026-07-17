import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type KpiCardProps = {
  detail: string;
  emphasis?: "primary" | "secondary";
  label: string;
  status?: string;
  value: string;
};

export function KpiCard({ detail, emphasis = "secondary", label, status, value }: KpiCardProps) {
  const primary = emphasis === "primary";

  return (
    <Card
      className={cn(
        "shadow-none",
        primary ? "border-[#192724] bg-[#192724] text-white" : "min-h-[108px]",
      )}
    >
      <CardContent
        className={cn(
          "pt-4",
          primary ? "flex min-h-36 flex-col justify-between pb-5 sm:px-6 sm:py-5" : "pb-4",
        )}
      >
        <div>
          <p className={cn("text-xs font-medium", primary ? "text-[#bfd0ca]" : "text-muted")}>
            {label}
          </p>
          <p
            className={cn(
              "mt-2 font-semibold",
              primary ? "text-3xl sm:text-4xl" : "text-2xl text-ink",
            )}
          >
            {value}
          </p>
        </div>
        <div
          className={cn(
            "mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs",
            primary ? "text-[#bfd0ca]" : "text-muted",
          )}
        >
          <span>{detail}</span>
          {status ? (
            <span className="inline-flex items-center gap-1.5 font-medium text-[#82e1b9]">
              <span className="size-1.5 rounded-full bg-[#82e1b9]" aria-hidden="true" />
              {status}
            </span>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
