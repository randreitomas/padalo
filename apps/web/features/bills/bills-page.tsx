"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, Pencil, Plus, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useActiveHousehold } from "@/components/household-provider";
import { PageHeader } from "@/components/layout/page-header";
import { ResourceSkeleton } from "@/components/resource/resource-skeleton";
import { Badge } from "@/components/ui/badge";
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
import type { Bill, BillPayload, BillStatus } from "@/lib/api/types";
import { queryKeys } from "@/lib/query-keys";
import { formatDate, formatPhp, toMoneyInput } from "@/lib/utils";
import { useBills } from "@/hooks/use-ledger-data";
import { useOptimisticListDelete } from "@/hooks/use-optimistic-list-delete";

const billSchema = z
  .object({
    name: z.string().trim().min(1, "Enter a bill name.").max(160),
    amount_php: z.coerce.number().positive("Enter an amount greater than zero."),
    due_date: z.string().min(1, "Choose a due date."),
    category: z.string().trim().max(120),
    recurring: z.boolean(),
    recurrence_rule: z.string().trim().max(160),
    status: z.enum(["scheduled", "paid", "skipped"]),
  })
  .superRefine((values, context) => {
    if (values.recurring && !values.recurrence_rule) {
      context.addIssue({
        code: "custom",
        path: ["recurrence_rule"],
        message: "Add a recurrence rule for a recurring bill.",
      });
    }
  });

type BillFormInput = z.input<typeof billSchema>;
type BillFormValues = z.output<typeof billSchema>;

const selectClass =
  "h-10 w-full rounded-md border border-line bg-surface px-3 text-sm text-ink outline-none focus:border-lagoon focus:ring-2 focus:ring-[#b9ded8]";

const statusTone: Record<BillStatus, "warning" | "success" | "neutral"> = {
  scheduled: "warning",
  paid: "success",
  skipped: "neutral",
};

function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : "The bill could not be saved. Try again.";
}

function BillDialog({
  householdId,
  bill,
  open,
  onOpenChange,
}: {
  householdId: string;
  bill?: Bill;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const form = useForm<BillFormInput, unknown, BillFormValues>({
    resolver: zodResolver(billSchema),
    defaultValues: {
      name: "",
      amount_php: 0,
      due_date: "",
      category: "",
      recurring: false,
      recurrence_rule: "",
      status: "scheduled",
    },
  });
  const recurring = form.watch("recurring");

  useEffect(() => {
    form.reset({
      name: bill?.name ?? "",
      amount_php: Number(bill?.amount_php ?? 0),
      due_date: bill?.due_date ?? "",
      category: bill?.category ?? "",
      recurring: bill?.recurring ?? false,
      recurrence_rule: bill?.recurrence_rule ?? "",
      status: bill?.status ?? "scheduled",
    });
  }, [bill, form, open]);

  const save = useMutation({
    mutationFn: (values: BillFormValues) => {
      const payload: BillPayload = {
        name: values.name,
        amount_php: toMoneyInput(values.amount_php),
        due_date: values.due_date,
        category: values.category || null,
        recurring: values.recurring,
        recurrence_rule: values.recurring ? values.recurrence_rule : null,
        status: values.status as BillStatus,
      };
      return bill
        ? api.updateBill(householdId, bill.id, payload)
        : api.createBill(householdId, payload);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.bills(householdId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard(householdId) }),
      ]);
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-ink">
            {bill ? "Edit bill" : "Add bill"}
          </DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            Track scheduled household commitments without moving money automatically.
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
          noValidate
        >
          <FormField id="bill-name" label="Bill name" error={form.formState.errors.name?.message}>
            <Input id="bill-name" autoFocus {...form.register("name")} />
          </FormField>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="bill-amount"
              label="Amount (PHP)"
              error={form.formState.errors.amount_php?.message}
            >
              <Input
                id="bill-amount"
                type="number"
                min="0.01"
                step="0.01"
                {...form.register("amount_php")}
              />
            </FormField>
            <FormField
              id="bill-due-date"
              label="Due date"
              error={form.formState.errors.due_date?.message}
            >
              <Input id="bill-due-date" type="date" {...form.register("due_date")} />
            </FormField>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="bill-category"
              label="Category"
              error={form.formState.errors.category?.message}
            >
              <Input id="bill-category" placeholder="Optional" {...form.register("category")} />
            </FormField>
            <FormField
              id="bill-status"
              label="Status"
              error={form.formState.errors.status?.message}
            >
              <select id="bill-status" className={selectClass} {...form.register("status")}>
                <option value="scheduled">Scheduled</option>
                <option value="paid">Paid</option>
                <option value="skipped">Skipped</option>
              </select>
            </FormField>
          </div>
          <label className="flex items-center gap-2 text-sm font-medium text-ink">
            <input
              type="checkbox"
              className="size-4 rounded border-line text-lagoon focus:ring-lagoon"
              {...form.register("recurring")}
            />
            Recurring bill
          </label>
          {recurring ? (
            <FormField
              id="bill-recurrence"
              label="Recurrence rule"
              error={form.formState.errors.recurrence_rule?.message}
            >
              <Input
                id="bill-recurrence"
                placeholder="For example: monthly"
                {...form.register("recurrence_rule")}
              />
            </FormField>
          ) : null}
          <FormError message={save.isError ? errorMessage(save.error) : undefined} />
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending ? "Saving..." : bill ? "Save changes" : "Add bill"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function BillsPage() {
  const { householdId } = useActiveHousehold();
  const query = useBills(householdId);
  const [editor, setEditor] = useState<Bill | "new" | null>(null);
  const bills = query.data?.items ?? [];
  const remove = useOptimisticListDelete<Bill>({
    queryKey: queryKeys.bills(householdId),
    mutationFn: (id) => api.deleteBill(householdId, id),
    invalidate: [queryKeys.bills(householdId), queryKeys.dashboard(householdId)],
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Commitments"
        title="Bills"
        description="Keep due dates and recurring household commitments visible to everyone."
        actions={
          <Button size="sm" onClick={() => setEditor("new")}>
            <Plus className="size-3.5" aria-hidden="true" />
            Add bill
          </Button>
        }
      />
      {query.isLoading ? <ResourceSkeleton rows={6} /> : null}
      {query.isError ? (
        <ErrorState
          title="Bills could not be loaded"
          description="Check the API connection and try again."
          onRetry={() => query.refetch()}
        />
      ) : null}
      {!query.isLoading && !query.isError && bills.length === 0 ? (
        <EmptyState
          title="No bills yet"
          description="Add a scheduled bill to keep the household's next commitments visible."
          action={
            <Button size="sm" onClick={() => setEditor("new")}>
              <Plus className="size-3.5" aria-hidden="true" />
              Add bill
            </Button>
          }
        />
      ) : null}
      {bills.length > 0 ? (
        <Card>
          <CardContent className="overflow-x-auto p-0">
            <table className="w-full min-w-[42rem] text-left text-sm">
              <thead className="border-b border-line bg-[#f8faf9] text-xs font-semibold uppercase tracking-[0.08em] text-muted">
                <tr>
                  <th className="px-5 py-3">Bill</th>
                  <th className="px-5 py-3">Due date</th>
                  <th className="px-5 py-3">Schedule</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3 text-right">Amount</th>
                  <th className="w-24 px-5 py-3 text-right">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {bills.map((bill) => (
                  <tr key={bill.id} className="hover:bg-[#fbfcfc]">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <CalendarClock className="size-4 text-gold" aria-hidden="true" />
                        <div className="max-w-52">
                          <p className="truncate font-medium text-ink">{bill.name}</p>
                          <p className="mt-1 truncate text-xs text-muted">
                            {bill.category ?? "Uncategorized"}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-muted">{formatDate(bill.due_date)}</td>
                    <td className="px-5 py-4 text-muted">
                      {bill.recurring ? (
                        <span className="inline-flex items-center gap-1.5">
                          <RefreshCw className="size-3.5" aria-hidden="true" />
                          {bill.recurrence_rule}
                        </span>
                      ) : (
                        "One-time"
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <Badge variant={statusTone[bill.status]}>{bill.status}</Badge>
                    </td>
                    <td className="px-5 py-4 text-right font-semibold tabular-nums text-ink">
                      {formatPhp(bill.amount_php)}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex justify-end">
                        <IconButton label="Edit bill" onClick={() => setEditor(bill)}>
                          <Pencil className="size-4" aria-hidden="true" />
                        </IconButton>
                        <DeleteDialog
                          entityName={bill.name}
                          isPending={remove.isPending}
                          onConfirm={() => remove.mutateAsync(bill.id)}
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
      <BillDialog
        householdId={householdId}
        bill={editor === "new" ? undefined : (editor ?? undefined)}
        open={editor !== null}
        onOpenChange={(open) => !open && setEditor(null)}
      />
    </div>
  );
}
