"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowDownRight, ArrowUpRight, Pencil, Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
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
import type { Envelope, Transaction, TransactionPayload, TransactionType } from "@/lib/api/types";
import { queryKeys } from "@/lib/query-keys";
import { formatDate, formatPhp, toDateInput, toMoneyInput } from "@/lib/utils";
import { useEnvelopes, useTransactions } from "@/hooks/use-ledger-data";
import { useOptimisticListDelete } from "@/hooks/use-optimistic-list-delete";

const transactionSchema = z.object({
  envelope_id: z.string(),
  amount_php: z.coerce.number().positive("Enter an amount greater than zero."),
  transaction_type: z.enum(["expense", "refund", "adjustment"]),
  merchant: z.string().trim().max(160),
  note: z.string().trim().max(10_000),
  occurred_on: z.string().min(1, "Choose the date the transaction occurred."),
});

type TransactionFormInput = z.input<typeof transactionSchema>;
type TransactionFormValues = z.output<typeof transactionSchema>;

const selectClass =
  "h-10 w-full rounded-md border border-line bg-surface px-3 text-sm text-ink outline-none focus:border-lagoon focus:ring-2 focus:ring-[#b9ded8]";

function errorMessage(error: unknown) {
  return error instanceof ApiError
    ? error.message
    : "The transaction could not be saved. Try again.";
}

function TransactionDialog({
  householdId,
  envelopes,
  transaction,
  open,
  onOpenChange,
}: {
  householdId: string;
  envelopes: Envelope[];
  transaction?: Transaction;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const form = useForm<TransactionFormInput, unknown, TransactionFormValues>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      envelope_id: "",
      amount_php: 0,
      transaction_type: "expense",
      merchant: "",
      note: "",
      occurred_on: toDateInput(new Date().toISOString()),
    },
  });

  useEffect(() => {
    form.reset({
      envelope_id: transaction?.envelope_id ?? "",
      amount_php: Number(transaction?.amount_php ?? 0),
      transaction_type: transaction?.transaction_type ?? "expense",
      merchant: transaction?.merchant ?? "",
      note: transaction?.note ?? "",
      occurred_on: transaction?.occurred_on ?? toDateInput(new Date().toISOString()),
    });
  }, [form, open, transaction]);

  const save = useMutation({
    mutationFn: (values: TransactionFormValues) => {
      const shared = {
        envelope_id: values.envelope_id || null,
        amount_php: toMoneyInput(values.amount_php),
        transaction_type: values.transaction_type as TransactionType,
        merchant: values.merchant || null,
        note: values.note || null,
        occurred_on: values.occurred_on,
      };
      if (transaction) return api.updateTransaction(householdId, transaction.id, shared);
      const payload: TransactionPayload = {
        ...shared,
        logged_by_member_id: null,
        source: "manual",
        receipt_url: null,
      };
      return api.createTransaction(householdId, payload);
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.transactions(householdId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.envelopes(householdId) }),
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
            {transaction ? "Edit transaction" : "Add transaction"}
          </DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            Record a manual household expense, refund, or debit adjustment.
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
          noValidate
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="transaction-type"
              label="Type"
              error={form.formState.errors.transaction_type?.message}
            >
              <select
                id="transaction-type"
                className={selectClass}
                {...form.register("transaction_type")}
              >
                <option value="expense">Expense</option>
                <option value="refund">Refund</option>
                <option value="adjustment">Adjustment</option>
              </select>
            </FormField>
            <FormField
              id="transaction-envelope"
              label="Envelope"
              error={form.formState.errors.envelope_id?.message}
            >
              <select
                id="transaction-envelope"
                className={selectClass}
                {...form.register("envelope_id")}
              >
                <option value="">Unassigned</option>
                {envelopes.map((envelope) => (
                  <option key={envelope.id} value={envelope.id}>
                    {envelope.name}
                  </option>
                ))}
              </select>
            </FormField>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="transaction-amount"
              label="Amount (PHP)"
              error={form.formState.errors.amount_php?.message}
            >
              <Input
                id="transaction-amount"
                type="number"
                min="0.01"
                step="0.01"
                {...form.register("amount_php")}
              />
            </FormField>
            <FormField
              id="transaction-date"
              label="Date"
              error={form.formState.errors.occurred_on?.message}
            >
              <Input id="transaction-date" type="date" {...form.register("occurred_on")} />
            </FormField>
          </div>
          <FormField
            id="transaction-merchant"
            label="Merchant"
            error={form.formState.errors.merchant?.message}
          >
            <Input
              id="transaction-merchant"
              placeholder="Optional"
              {...form.register("merchant")}
            />
          </FormField>
          <FormField id="transaction-note" label="Note" error={form.formState.errors.note?.message}>
            <Input
              id="transaction-note"
              placeholder="Optional context"
              {...form.register("note")}
            />
          </FormField>
          <FormError message={save.isError ? errorMessage(save.error) : undefined} />
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending ? "Saving..." : transaction ? "Save changes" : "Add transaction"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function TransactionsPage() {
  const { householdId } = useActiveHousehold();
  const transactionsQuery = useTransactions(householdId);
  const envelopesQuery = useEnvelopes(householdId);
  const [editor, setEditor] = useState<Transaction | "new" | null>(null);
  const transactions = transactionsQuery.data?.items ?? [];
  const envelopes = useMemo(() => envelopesQuery.data?.items ?? [], [envelopesQuery.data?.items]);
  const envelopeNames = useMemo(
    () => new Map(envelopes.map((envelope) => [envelope.id, envelope.name])),
    [envelopes],
  );
  const remove = useOptimisticListDelete<Transaction>({
    queryKey: queryKeys.transactions(householdId),
    mutationFn: (id) => api.deleteTransaction(householdId, id),
    invalidate: [
      queryKeys.transactions(householdId),
      queryKeys.envelopes(householdId),
      queryKeys.dashboard(householdId),
    ],
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Ledger activity"
        title="Transactions"
        description="Record household spending and keep every envelope balance reconciled."
        actions={
          <Button size="sm" onClick={() => setEditor("new")}>
            <Plus className="size-3.5" aria-hidden="true" />
            Add transaction
          </Button>
        }
      />
      {transactionsQuery.isLoading ? <ResourceSkeleton rows={6} /> : null}
      {transactionsQuery.isError ? (
        <ErrorState
          title="Transactions could not be loaded"
          description="Check the API connection and try again."
          onRetry={() => transactionsQuery.refetch()}
        />
      ) : null}
      {!transactionsQuery.isLoading && !transactionsQuery.isError && transactions.length === 0 ? (
        <EmptyState
          title="No transactions yet"
          description="Record the first expense to begin building the shared ledger."
          action={
            <Button size="sm" onClick={() => setEditor("new")}>
              <Plus className="size-3.5" aria-hidden="true" />
              Add transaction
            </Button>
          }
        />
      ) : null}
      {transactions.length > 0 ? (
        <Card>
          <CardContent className="overflow-x-auto p-0">
            <table className="w-full min-w-[44rem] text-left text-sm">
              <thead className="border-b border-line bg-[#f8faf9] text-xs font-semibold uppercase tracking-[0.08em] text-muted">
                <tr>
                  <th className="px-5 py-3">Transaction</th>
                  <th className="px-5 py-3">Envelope</th>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3 text-right">Amount</th>
                  <th className="w-24 px-5 py-3 text-right">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {transactions.map((transaction) => {
                  const credit = transaction.transaction_type === "refund";
                  return (
                    <tr key={transaction.id} className="hover:bg-[#fbfcfc]">
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-3">
                          {credit ? (
                            <ArrowUpRight className="size-4 text-lagoon" aria-hidden="true" />
                          ) : (
                            <ArrowDownRight className="size-4 text-coral" aria-hidden="true" />
                          )}
                          <div className="max-w-56">
                            <p className="truncate font-medium text-ink">
                              {transaction.merchant ?? transaction.note ?? "Recorded transaction"}
                            </p>
                            {transaction.note && transaction.merchant ? (
                              <p className="mt-1 truncate text-xs text-muted">{transaction.note}</p>
                            ) : null}
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-muted">
                        {transaction.envelope_id
                          ? (envelopeNames.get(transaction.envelope_id) ?? "Unavailable envelope")
                          : "Unassigned"}
                      </td>
                      <td className="px-5 py-4 text-muted">
                        {formatDate(transaction.occurred_on)}
                      </td>
                      <td className="px-5 py-4">
                        <Badge variant={credit ? "success" : "neutral"}>
                          {transaction.transaction_type}
                        </Badge>
                      </td>
                      <td
                        className={
                          credit
                            ? "px-5 py-4 text-right font-semibold tabular-nums text-lagoon"
                            : "px-5 py-4 text-right font-semibold tabular-nums text-ink"
                        }
                      >
                        {credit ? "+" : "-"}
                        {formatPhp(transaction.amount_php)}
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex justify-end">
                          <IconButton
                            label="Edit transaction"
                            onClick={() => setEditor(transaction)}
                          >
                            <Pencil className="size-4" aria-hidden="true" />
                          </IconButton>
                          <DeleteDialog
                            entityName="transaction"
                            isPending={remove.isPending}
                            onConfirm={() => remove.mutateAsync(transaction.id)}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </CardContent>
        </Card>
      ) : null}
      <TransactionDialog
        householdId={householdId}
        envelopes={envelopes}
        transaction={editor === "new" ? undefined : (editor ?? undefined)}
        open={editor !== null}
        onOpenChange={(open) => !open && setEditor(null)}
      />
    </div>
  );
}
