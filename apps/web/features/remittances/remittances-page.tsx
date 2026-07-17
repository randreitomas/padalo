"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Send } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useActiveHousehold } from "@/components/household-provider";
import { PageHeader } from "@/components/layout/page-header";
import { ResourceSkeleton } from "@/components/resource/resource-skeleton";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import type { Remittance, RemittancePayload } from "@/lib/api/types";
import { queryKeys } from "@/lib/query-keys";
import {
  formatDateTime,
  formatDecimal,
  formatPhp,
  toDateTimeLocalInput,
  toMoneyInput,
} from "@/lib/utils";
import { useRemittances } from "@/hooks/use-ledger-data";
import { useOptimisticListDelete } from "@/hooks/use-optimistic-list-delete";

const remittanceSchema = z.object({
  amount_php: z.coerce.number().positive("Enter an amount greater than zero."),
  source_amount: z.coerce.number().positive("Enter an amount greater than zero."),
  source_currency: z.string().trim().length(3, "Use a 3-letter currency code."),
  provider: z.string().trim().min(1, "Enter the provider name.").max(120),
  fee_php: z.coerce.number().min(0, "Fee cannot be negative."),
  rate_used: z.coerce.number().positive("Enter a rate greater than zero."),
  sent_at: z.string().min(1, "Choose the send date and time."),
});

type RemittanceFormInput = z.input<typeof remittanceSchema>;
type RemittanceFormValues = z.output<typeof remittanceSchema>;

function errorMessage(error: unknown) {
  return error instanceof ApiError
    ? error.message
    : "The remittance could not be saved. Try again.";
}

function RemittanceDialog({
  householdId,
  remittance,
  open,
  onOpenChange,
}: {
  householdId: string;
  remittance?: Remittance;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const form = useForm<RemittanceFormInput, unknown, RemittanceFormValues>({
    resolver: zodResolver(remittanceSchema),
    defaultValues: {
      amount_php: 0,
      source_amount: 0,
      source_currency: "USD",
      provider: "",
      fee_php: 0,
      rate_used: 0,
      sent_at: toDateTimeLocalInput(new Date().toISOString()),
    },
  });

  useEffect(() => {
    form.reset({
      amount_php: Number(remittance?.amount_php ?? 0),
      source_amount: Number(remittance?.source_amount ?? 0),
      source_currency: remittance?.source_currency ?? "USD",
      provider: remittance?.provider ?? "",
      fee_php: Number(remittance?.fee_php ?? 0),
      rate_used: Number(remittance?.rate_used ?? 0),
      sent_at: remittance
        ? toDateTimeLocalInput(remittance.sent_at)
        : toDateTimeLocalInput(new Date().toISOString()),
    });
  }, [form, open, remittance]);

  const save = useMutation({
    mutationFn: (values: RemittanceFormValues) => {
      const shared = {
        amount_php: toMoneyInput(values.amount_php),
        source_amount: toMoneyInput(values.source_amount),
        source_currency: values.source_currency.toUpperCase(),
        provider: values.provider,
        fee_php: toMoneyInput(values.fee_php),
        rate_used: Number(values.rate_used).toFixed(8),
        sent_at: new Date(values.sent_at).toISOString(),
      };
      if (remittance) return api.updateRemittance(householdId, remittance.id, shared);
      const payload: RemittancePayload = { ...shared, recorded_by_member_id: null };
      return api.createRemittance(householdId, payload);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.remittances(householdId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard(householdId) }),
      ]);
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-ink">
            {remittance ? "Edit remittance" : "Record remittance"}
          </DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            Store the remittance received by the household. This does not initiate a transfer.
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
          noValidate
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="remittance-provider"
              label="Provider"
              error={form.formState.errors.provider?.message}
            >
              <Input
                id="remittance-provider"
                autoFocus
                placeholder="For example: Wise"
                {...form.register("provider")}
              />
            </FormField>
            <FormField
              id="remittance-sent-at"
              label="Sent at"
              error={form.formState.errors.sent_at?.message}
            >
              <Input id="remittance-sent-at" type="datetime-local" {...form.register("sent_at")} />
            </FormField>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="remittance-php"
              label="Received amount (PHP)"
              error={form.formState.errors.amount_php?.message}
            >
              <Input
                id="remittance-php"
                type="number"
                min="0.01"
                step="0.01"
                {...form.register("amount_php")}
              />
            </FormField>
            <FormField
              id="remittance-source"
              label="Sent amount"
              error={form.formState.errors.source_amount?.message}
            >
              <Input
                id="remittance-source"
                type="number"
                min="0.01"
                step="0.01"
                {...form.register("source_amount")}
              />
            </FormField>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <FormField
              id="remittance-currency"
              label="Source currency"
              error={form.formState.errors.source_currency?.message}
            >
              <Input id="remittance-currency" maxLength={3} {...form.register("source_currency")} />
            </FormField>
            <FormField
              id="remittance-fee"
              label="Fee (PHP)"
              error={form.formState.errors.fee_php?.message}
            >
              <Input
                id="remittance-fee"
                type="number"
                min="0"
                step="0.01"
                {...form.register("fee_php")}
              />
            </FormField>
            <FormField
              id="remittance-rate"
              label="Rate used"
              error={form.formState.errors.rate_used?.message}
            >
              <Input
                id="remittance-rate"
                type="number"
                min="0.00000001"
                step="0.00000001"
                {...form.register("rate_used")}
              />
            </FormField>
          </div>
          <FormError message={save.isError ? errorMessage(save.error) : undefined} />
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending ? "Saving..." : remittance ? "Save changes" : "Record remittance"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function RemittancesPage() {
  const { householdId } = useActiveHousehold();
  const query = useRemittances(householdId);
  const [editor, setEditor] = useState<Remittance | "new" | null>(null);
  const remittances = query.data?.items ?? [];
  const remove = useOptimisticListDelete<Remittance>({
    queryKey: queryKeys.remittances(householdId),
    mutationFn: (id) => api.deleteRemittance(householdId, id),
    invalidate: [queryKeys.remittances(householdId), queryKeys.dashboard(householdId)],
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Household inflows"
        title="Remittances"
        description="Keep a transparent record of money sent to the household without initiating transfers."
        actions={
          <Button size="sm" onClick={() => setEditor("new")}>
            <Plus className="size-3.5" aria-hidden="true" />
            Record remittance
          </Button>
        }
      />
      {query.isLoading ? <ResourceSkeleton rows={6} /> : null}
      {query.isError ? (
        <ErrorState
          title="Remittances could not be loaded"
          description="Check the API connection and try again."
          onRetry={() => query.refetch()}
        />
      ) : null}
      {!query.isLoading && !query.isError && remittances.length === 0 ? (
        <EmptyState
          title="No remittances yet"
          description="Record the first household remittance to create a transparent history."
          action={
            <Button size="sm" onClick={() => setEditor("new")}>
              <Plus className="size-3.5" aria-hidden="true" />
              Record remittance
            </Button>
          }
        />
      ) : null}
      {remittances.length > 0 ? (
        <Card>
          <CardContent className="overflow-x-auto p-0">
            <table className="w-full min-w-[46rem] text-left text-sm">
              <thead className="border-b border-line bg-[#f8faf9] text-xs font-semibold uppercase tracking-[0.08em] text-muted">
                <tr>
                  <th className="px-5 py-3">Provider</th>
                  <th className="px-5 py-3">Sent at</th>
                  <th className="px-5 py-3">Source amount</th>
                  <th className="px-5 py-3">Fee</th>
                  <th className="px-5 py-3 text-right">Received</th>
                  <th className="w-24 px-5 py-3 text-right">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {remittances.map((remittance) => (
                  <tr key={remittance.id} className="hover:bg-[#fbfcfc]">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <span className="flex size-8 items-center justify-center rounded-md bg-[#e4eff6] text-sky">
                          <Send className="size-4" aria-hidden="true" />
                        </span>
                        <div>
                          <p className="font-medium text-ink">{remittance.provider}</p>
                          <p className="mt-1 text-xs text-muted">
                            Rate {formatDecimal(remittance.rate_used, 4)}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-muted">{formatDateTime(remittance.sent_at)}</td>
                    <td className="px-5 py-4 text-muted">
                      {formatDecimal(remittance.source_amount)} {remittance.source_currency}
                    </td>
                    <td className="px-5 py-4 text-muted">{formatPhp(remittance.fee_php)}</td>
                    <td className="px-5 py-4 text-right font-semibold text-lagoon">
                      {formatPhp(remittance.amount_php)}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex justify-end">
                        <IconButton label="Edit remittance" onClick={() => setEditor(remittance)}>
                          <Pencil className="size-4" aria-hidden="true" />
                        </IconButton>
                        <DeleteDialog
                          entityName="remittance"
                          isPending={remove.isPending}
                          onConfirm={() => remove.mutateAsync(remittance.id)}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      ) : null}
      <RemittanceDialog
        householdId={householdId}
        remittance={editor === "new" ? undefined : (editor ?? undefined)}
        open={editor !== null}
        onOpenChange={(open) => !open && setEditor(null)}
      />
    </div>
  );
}
