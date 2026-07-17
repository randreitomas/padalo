import { Skeleton } from "@/components/ui/skeleton";

export function DashboardSkeleton() {
  return (
    <div
      className="mx-auto max-w-[1180px] space-y-5"
      aria-label="Loading dashboard"
      aria-busy="true"
    >
      <div className="space-y-3 border-b border-line pb-5">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-9 w-72" />
        <Skeleton className="h-4 w-full max-w-xl" />
      </div>
      <Skeleton className="h-36" />
      <div className="grid gap-3 sm:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <Skeleton key={item} className="h-28" />
        ))}
      </div>
      <Skeleton className="h-20" />
      <Skeleton className="h-44" />
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
      </div>
    </div>
  );
}
