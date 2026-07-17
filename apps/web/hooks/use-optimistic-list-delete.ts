"use client";

import { useMutation, useQueryClient, type QueryKey } from "@tanstack/react-query";

import type { Paginated } from "@/lib/api/types";

type DeleteContext<T> = { previous?: Paginated<T> };

export function useOptimisticListDelete<T extends { id: string }>({
  queryKey,
  mutationFn,
  invalidate,
}: {
  queryKey: QueryKey;
  mutationFn: (id: string) => Promise<void>;
  invalidate: QueryKey[];
}) {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string, DeleteContext<T>>({
    mutationFn,
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey });
      const previous = queryClient.getQueryData<Paginated<T>>(queryKey);
      queryClient.setQueryData<Paginated<T>>(queryKey, (current) =>
        current ? { ...current, items: current.items.filter((item) => item.id !== id) } : current,
      );
      return { previous };
    },
    onError: (_, __, context) => {
      if (context?.previous) queryClient.setQueryData(queryKey, context.previous);
    },
    onSettled: async () => {
      await Promise.all(invalidate.map((key) => queryClient.invalidateQueries({ queryKey: key })));
    },
  });
}
