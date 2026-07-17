"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { EnvelopeCard } from "@/components/dashboard/envelope-card";
import { useActiveHousehold } from "@/components/household-provider";
import { PageHeader } from "@/components/layout/page-header";
import { ResourceSkeleton } from "@/components/resource/resource-skeleton";
import { Button } from "@/components/ui/button";
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
import type { Envelope, EnvelopePayload } from "@/lib/api/types";
import { queryKeys } from "@/lib/query-keys";
import { toMoneyInput } from "@/lib/utils";
import { useEnvelopes } from "@/hooks/use-ledger-data";
import { useOptimisticListDelete } from "@/hooks/use-optimistic-list-delete";

const envelopeSchema = z.object({
  name: z.string().trim().min(1, "Enter an envelope name.").max(120),
  target_amount_php: z.coerce.number().min(0, "Target cannot be negative."),
  current_balance_php: z.coerce.number().min(0, "Balance cannot be negative."),
  sort_order: z.coerce.number().int().min(0, "Order cannot be negative."),
});

type EnvelopeFormInput = z.input<typeof envelopeSchema>;
type EnvelopeFormValues = z.output<typeof envelopeSchema>;

function message(error: unknown) {
  return error instanceof ApiError ? error.message : "The envelope could not be saved. Try again.";
}

function EnvelopeDialog({
  householdId,
  envelope,
  open,
  onOpenChange,
}: {
  householdId: string;
  envelope?: Envelope;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const queryClient = useQueryClient();
  const form = useForm<EnvelopeFormInput, unknown, EnvelopeFormValues>({
    resolver: zodResolver(envelopeSchema),
    defaultValues: { name: "", target_amount_php: 0, current_balance_php: 0, sort_order: 0 },
  });

  useEffect(() => {
    form.reset({
      name: envelope?.name ?? "",
      target_amount_php: Number(envelope?.target_amount_php ?? 0),
      current_balance_php: Number(envelope?.current_balance_php ?? 0),
      sort_order: envelope?.sort_order ?? 0,
    });
  }, [envelope, form, open]);

  const save = useMutation({
    mutationFn: (values: EnvelopeFormValues) => {
      const payload: EnvelopePayload = {
        name: values.name,
        target_amount_php: toMoneyInput(values.target_amount_php),
        current_balance_php: toMoneyInput(values.current_balance_php),
        sort_order: values.sort_order,
      };
      return envelope
        ? api.updateEnvelope(householdId, envelope.id, payload)
        : api.createEnvelope(householdId, payload);
    },
    onSuccess: async () => {
      await Promise.all([
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
            {envelope ? "Edit envelope" : "Create envelope"}
          </DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            Set the allocation and the currently available balance for this category.
          </DialogDescription>
        </DialogHeader>
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit((values) => save.mutate(values))}
          noValidate
        >
          <FormField id="envelope-name" label="Name" error={form.formState.errors.name?.message}>
            <Input id="envelope-name" autoFocus {...form.register("name")} />
          </FormField>
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              id="envelope-target"
              label="Target amount (PHP)"
              error={form.formState.errors.target_amount_php?.message}
            >
              <Input
                id="envelope-target"
                type="number"
                min="0"
                step="0.01"
                {...form.register("target_amount_php")}
              />
            </FormField>
            <FormField
              id="envelope-balance"
              label="Current balance (PHP)"
              error={form.formState.errors.current_balance_php?.message}
            >
              <Input
                id="envelope-balance"
                type="number"
                min="0"
                step="0.01"
                {...form.register("current_balance_php")}
              />
            </FormField>
          </div>
          <FormField
            id="envelope-order"
            label="Display order"
            error={form.formState.errors.sort_order?.message}
          >
            <Input
              id="envelope-order"
              type="number"
              min="0"
              step="1"
              {...form.register("sort_order")}
            />
          </FormField>
          <FormError message={save.isError ? message(save.error) : undefined} />
          <DialogFooter>
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={save.isPending}>
              {save.isPending ? "Saving..." : envelope ? "Save changes" : "Create envelope"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function EnvelopesPage() {
  const { householdId } = useActiveHousehold();
  const query = useEnvelopes(householdId);
  const [editor, setEditor] = useState<Envelope | "new" | null>(null);
  const envelopes = query.data?.items ?? [];
  const remove = useOptimisticListDelete<Envelope>({
    queryKey: queryKeys.envelopes(householdId),
    mutationFn: (id) => api.deleteEnvelope(householdId, id),
    invalidate: [queryKeys.envelopes(householdId), queryKeys.dashboard(householdId)],
  });

  return (
    <div className="space-y-7">
      <PageHeader
        eyebrow="Budget planning"
        title="Envelopes"
        description="Organize household funds into clear, shared spending categories."
        actions={
          <Button size="sm" onClick={() => setEditor("new")}>
            <Plus className="size-3.5" aria-hidden="true" />
            New envelope
          </Button>
        }
      />
      {query.isLoading ? <ResourceSkeleton rows={4} /> : null}
      {query.isError ? (
        <ErrorState
          title="Envelopes could not be loaded"
          description="Check the API connection and try again."
          onRetry={() => query.refetch()}
        />
      ) : null}
      {!query.isLoading && !query.isError && envelopes.length === 0 ? (
        <EmptyState
          title="No budget envelopes"
          description="Create a category such as groceries, bills, or education to track its remaining funds."
          action={
            <Button size="sm" onClick={() => setEditor("new")}>
              <Plus className="size-3.5" aria-hidden="true" />
              Create envelope
            </Button>
          }
        />
      ) : null}
      {envelopes.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {envelopes.map((envelope) => (
            <EnvelopeCard
              key={envelope.id}
              envelope={envelope}
              actions={
                <div className="flex items-center">
                  <IconButton label={`Edit ${envelope.name}`} onClick={() => setEditor(envelope)}>
                    <Pencil className="size-4" aria-hidden="true" />
                  </IconButton>
                  <DeleteDialog
                    entityName={envelope.name}
                    isPending={remove.isPending}
                    onConfirm={() => remove.mutateAsync(envelope.id)}
                  />
                </div>
              }
            />
          ))}
        </div>
      ) : null}
      <EnvelopeDialog
        householdId={householdId}
        envelope={editor === "new" ? undefined : (editor ?? undefined)}
        open={editor !== null}
        onOpenChange={(open) => !open && setEditor(null)}
      />
    </div>
  );
}
