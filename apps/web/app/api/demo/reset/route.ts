import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST() {
  const enabled = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
  const resetUrl = process.env.DEMO_RESET_API_URL;
  const resetToken = process.env.DEMO_RESET_TOKEN;

  if (!enabled || !resetUrl || !resetToken) {
    return NextResponse.json(
      { detail: "Demo reset is not configured for this deployment." },
      { status: 503 },
    );
  }

  try {
    const response = await fetch(resetUrl, {
      method: "POST",
      cache: "no-store",
      headers: { "X-Padalo-Demo-Reset-Token": resetToken },
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      return NextResponse.json(
        { detail: body?.detail ?? "The demo household could not be reset. Try again." },
        { status: response.status >= 500 ? 503 : response.status },
      );
    }
  } catch {
    return NextResponse.json(
      { detail: "The demo household could not be reached. Try again in a moment." },
      { status: 503 },
    );
  }

  return new NextResponse(null, { status: 204 });
}
