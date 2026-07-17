"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Pencil, Plus, UsersRound } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useActiveHousehold } from "@/components/household-provider";
import { PageHeader } from "@/components/layout/page-header";
import { ResourceSkeleton } from "@/components/resource/resource-skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { DeleteDialog } from "@/components/ui/delete-dialog";
import { FormError } from "@/components/ui/form-error";
import { FormField } from "@/components/ui/form-field";
import { IconButton } from "@/components/ui/icon-button";
import { Input } from "@/components/ui/input";
import { EmptyState, ErrorState } from "@/components/ui/state-panel";
import { api, ApiError } from "@/lib/api/client";
import type { Household, HouseholdPayload } from "@/lib/api/types";
import { queryKeys } from "@/lib/query-keys";
import { useHouseholds } from "@/hooks/use-ledger-data";
import { useOptimisticListDelete } from "@/hooks/use-optimistic-list-delete";

const householdSchema = z.object({
  name: z.string().trim().min(1, "Enter a household name.").max(160),
  base_currency: z.string().trim().length(3, "Use a 3-letter currency code."),
  home_country: z.string().trim().length(2, "Use a 2-letter country code."),
});

type HouseholdFormValues = z.infer<typeof householdSchema>;

function getMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "The change could not be saved. Try again.";
}

function HouseholdDialog({
  household,
  open,
  onOpenChange,
}: {
  household?: Household;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { setHouseholdId } = useActiveHousehold();
  const queryClient = useQueryClient();
  const form = useForm<HouseholdFormValues>({
    resolver: zodResolver(householdSchema),
    defaultValues: { name: "", base_currency: "PHP", home_country: "PH" },
  });

  useEffect(() => {
    form.reset({
      name: household?.name ?? "",
      base_currency: household?.base_currency ?? "PHP",
      home_country: household?.home_country ?? "PH",
    });
  }, [form, household, open]);

  const save = useMutation({
    mutationFn: (values: HouseholdFormValues) => {
      const payload: HouseholdPayload = {
        ...values,
        base_currency: values.base_currency.toUpperCase(),
        home_country: values.home_country.toUpperCase(),
      };
      return household ? api.updateHousehold(household.id, payload) : api.createHousehold(payload);
    },
    onSuccess: async (saved) => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.households });
      if (!household) setHouseholdId(saved.id);
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-ink">
            {household ? "Edit household" : "Create household"}
          </DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            This identifies the shared financial workspace and its base currency.
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
          noValidate
        >
          <FormField
            id="household-name"
            label="Household name"
            error={form.formState.errors.name?.message}
          >
            <Input id="household-name" autoFocus {...form.register("name")} />
          </FormField>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="household-currency"
              label="Base currency"
              error={form.formState.errors.base_currency?.message}
            >
              <Input id="household-currency" maxLength={3} {...form.register("base_currency")} />
            </FormField>
            <FormField
              id="household-country"
              label="Home country"
              error={form.formState.errors.home_country?.message}
            >
              <Input id="household-country" maxLength={2} {...form.register("home_country")} />
            </FormField>
          </div>
          <FormError message={save.isError ? getMessage(save.error) : undefined} />
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending ? "Saving..." : household ? "Save changes" : "Create household"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function HouseholdsPage() {
  const { householdId, setHouseholdId } = useActiveHousehold();
  const householdsQuery = useHouseholds();
  const queryClient = useQueryClient();
  const [editor, setEditor] = useState<Household | "new" | null>(null);
  const households = householdsQuery.data?.items ?? [];
  const deleteHousehold = useOptimisticListDelete<Household>({
    queryKey: queryKeys.households,
    mutationFn: api.deleteHousehold,
    invalidate: [queryKeys.households],
  });

  async function deleteSelected(household: Household) {
    await deleteHousehold.mutateAsync(household.id);
    if (household.id === householdId) {
      const next = households.find((item) => item.id !== household.id);
      if (next) setHouseholdId(next.id);
    }
    await queryClient.invalidateQueries({ queryKey: queryKeys.dashboard(household.id) });
  }

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Workspace settings"
        title="Households"
        description="Switch between shared financial workspaces or create another household."
        actions={
          <Button size="sm" onClick={() => setEditor("new")}>
            <Plus className="size-3.5" aria-hidden="true" />
            New household
          </Button>
        }
      />

      {householdsQuery.isLoading ? <ResourceSkeleton rows={4} /> : null}
      {householdsQuery.isError ? (
        <ErrorState
          title="Households could not be loaded"
          description="Check the API connection and try again."
          onRetry={() => householdsQuery.refetch()}
        />
      ) : null}
      {!householdsQuery.isLoading && !householdsQuery.isError && households.length === 0 ? (
        <EmptyState
          title="No households yet"
          description="Create a household to begin organizing shared finances."
          action={
            <Button size="sm" onClick={() => setEditor("new")}>
              <Plus className="size-3.5" aria-hidden="true" />
              Create household
            </Button>
          }
        />
      ) : null}
      {households.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {households.map((household) => {
            const active = household.id === householdId;
            return (
              <Card key={household.id} className={active ? "border-lagoon" : undefined}>
                <CardHeader>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <UsersRound className="size-4 text-lagoon" aria-hidden="true" />
                      <h2 className="truncate text-base font-semibold text-ink">
                        {household.name}
                      </h2>
                    </div>
                    <p className="mt-2 text-sm text-muted">
                      {household.base_currency} / {household.home_country}
                    </p>
                  </div>
                  {active ? <Badge variant="success">Active</Badge> : null}
                </CardHeader>
                <CardContent className="flex items-center justify-between gap-3">
                  <Button
                    variant={active ? "secondary" : "primary"}
                    size="sm"
                    onClick={() => setHouseholdId(household.id)}
                  >
                    {active ? <Check className="size-3.5" aria-hidden="true" /> : null}
                    {active ? "Selected" : "Select"}
                  </Button>
                  <div className="flex items-center">
                    <IconButton
                      label={`Edit ${household.name}`}
                      onClick={() => setEditor(household)}
                    >
                      <Pencil className="size-4" aria-hidden="true" />
                    </IconButton>
                    <DeleteDialog
                      entityName={household.name}
                      isPending={deleteHousehold.isPending}
                      onConfirm={() => deleteSelected(household)}
                    />
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : null}
      <HouseholdDialog
        household={editor === "new" ? undefined : (editor ?? undefined)}
        open={editor !== null}
        onOpenChange={(open) => !open && setEditor(null)}
      />
    </div>
  );
}
