import { Skeleton } from "@/components/ui/skeleton";

export function ResourceSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3" aria-label="Loading records" aria-busy="true">
      <Skeleton className="h-12 w-full" />
      {Array.from({ length: rows }, (_, index) => (
        <Skeleton key={index} className="h-16 w-full" />
      ))}
    </div>
  );
}
