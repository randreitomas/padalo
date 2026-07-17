"use client";

import { Trash2 } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { IconButton } from "@/components/ui/icon-button";
import { FormError } from "@/components/ui/form-error";

export function DeleteDialog({
  entityName,
  onConfirm,
  isPending,
}: {
  entityName: string;
  onConfirm: () => Promise<unknown> | void;
  isPending?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string>();

  async function confirm() {
    try {
      setError(undefined);
      await onConfirm();
      setOpen(false);
    } catch {
      setError("The record could not be deleted. Try again.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <IconButton label={`Delete ${entityName}`} onClick={() => setOpen(true)}>
        <Trash2 className="size-4 text-coral" aria-hidden="true" />
      </IconButton>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-lg font-semibold text-ink">Delete {entityName}?</DialogTitle>
          <DialogDescription className="text-sm leading-6 text-muted">
            This removes the record from the active household view. Deleting a transaction also
            reverses its impact on the related envelope balance.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <FormError message={error} />
          <Button variant="secondary" onClick={() => setOpen(false)} disabled={isPending}>
            Cancel
          </Button>
          <Button variant="danger" onClick={confirm} disabled={isPending}>
            {isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
