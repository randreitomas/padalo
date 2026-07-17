import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main
      id="main-content"
      className="flex min-h-screen items-center justify-center bg-canvas px-5 text-center"
    >
      <div className="max-w-md">
        <p className="text-sm font-semibold text-lagoon">Padalo</p>
        <h1 className="mt-3 text-3xl font-semibold text-ink">This page is not available.</h1>
        <p className="mt-3 text-sm leading-7 text-muted">
          Return to the product overview or continue with the Santos Family demo.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Button asChild variant="secondary">
            <Link href="/">Product overview</Link>
          </Button>
          <Button asChild>
            <Link href="/dashboard">Open demo</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
