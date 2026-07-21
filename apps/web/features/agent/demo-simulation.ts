import type { AgentStreamEvent, ForecastRecommendation } from "@/features/agent/agent-stream";

/** Deterministic FXPilot card used for the Santos Family demo and See more dialog. */
export const DEMO_FXPILOT_RECOMMENDATION: ForecastRecommendation = {
  recommended_day: "Thursday",
  expected_savings_php: "112.50",
  confidence: "85% historical-pattern confidence",
  provider: "Wise",
  amount_php: "15000.00",
  is_mock: true,
  disclaimer:
    "FXPilot models provider behavior patterns from deterministic synthetic history. It is not a live rate quote, fee guarantee, or financial advice.",
};

type DemoScript = {
  match: (message: string) => boolean;
  tools: string[];
  answer: string;
  recommendation?: ForecastRecommendation;
};

const normalize = (message: string) => message.trim().toLowerCase().replace(/\s+/g, " ");

const DEMO_SCRIPTS: DemoScript[] = [
  {
    match: (message) => {
      const value = normalize(message);
      return value.includes("afford tuition") || value.includes("still afford tuition");
    },
    tools: ["get_budget_status", "upcoming_bills"],
    answer:
      "Yes, tuition is still workable this month if Education stays protected. The Education envelope currently holds ₱6,250 against a ₱12,000 target, and the Tuition bill due July 24 is ₱7,500. Nearby bills total about ₱4,969 (Meralco, Converge, and Water District). A small top-up into Education before the 24th keeps the plan clear without pulling from Savings.",
  },
  {
    match: (message) => {
      const value = normalize(message);
      return (
        value.includes("when should i send") ||
        value.includes("best time to send") ||
        value === "when should i send money?"
      );
    },
    tools: ["forecast_remittance"],
    answer:
      "FXPilot recommends sending through Wise on Thursday for about ₱15,000. Based on the synthetic provider-behavior history, that timing shows roughly ₱113 in modeled savings with 85% historical-pattern confidence. This is a timing signal from demo data, not a live rate quote or guarantee.",
    recommendation: DEMO_FXPILOT_RECOMMENDATION,
  },
  {
    match: (message) => normalize(message).includes("upcoming bills"),
    tools: ["upcoming_bills"],
    answer:
      "Here are the upcoming Santos Family bills within the next two weeks: Meralco ₱2,450 due July 19, Converge ₱1,899 due July 21, Tuition ₱7,500 due July 24, and Water District ₱620 due July 26. Combined, that is ₱12,469 still committed.",
  },
  {
    match: (message) => {
      const value = normalize(message);
      return value.includes("where did our money go") || value.includes("money go this month");
    },
    tools: ["search_transactions"],
    answer:
      "This month’s activity includes groceries at SM Supermarket, medicine at Mercury Drug, school supplies at National Book Store, utility payments, a partial tuition payment, transportation, and a savings reserve adjustment. The ledger stays neutral so the family can review the picture together.",
  },
  {
    match: (message) => {
      const value = normalize(message);
      return value.includes("summarize our budget") || value.includes("budget status");
    },
    tools: ["get_budget_status"],
    answer:
      "Across envelopes, the household currently holds about ₱24,381 available against allocated targets. Education has ₱6,250, Groceries ₱5,350, Bills ₱2,481, Savings ₱8,000, and Transportation ₱2,300. The clearest near-term pressure is tuition on July 24.",
  },
  {
    match: (message) => {
      const value = normalize(message);
      return value.includes("log a grocery") || value.includes("grocery expense");
    },
    tools: ["log_expense"],
    answer:
      "I can log a grocery expense into the shared ledger. For this demo, use a recent amount such as ₱850 at SM Supermarket under Groceries, and I will confirm the entry once the details are set.",
  },
];

export function findDemoScript(message: string): DemoScript | null {
  return DEMO_SCRIPTS.find((script) => script.match(message)) ?? null;
}

export async function playDemoScript(
  script: DemoScript,
  onEvent: (event: AgentStreamEvent) => void,
) {
  const conversationId = "dddddddd-dddd-4ddd-8ddd-dddddddddddd";

  onEvent({ event: "conversation", data: { conversation_id: conversationId } });
  await wait(280);
  onEvent({ event: "status", data: { message: "Reviewing your request." } });
  await wait(420);

  for (const toolName of script.tools) {
    onEvent({ event: "tool_call", data: { name: toolName } });
    await wait(520);
    onEvent({
      event: "tool_result",
      data: {
        call_id: `demo-${toolName}`,
        name: toolName,
        ok: true,
        data:
          toolName === "forecast_remittance"
            ? { ...DEMO_FXPILOT_RECOMMENDATION }
            : { demo: true },
        error: null,
      },
    });
    await wait(240);
  }

  onEvent({
    event: "status",
    data: { message: "Using the household result to finish the answer." },
  });
  await wait(300);

  for (const delta of chunkText(script.answer)) {
    onEvent({ event: "assistant_delta", data: { delta } });
    await wait(18);
  }

  onEvent({
    event: "final",
    data: {
      response: {
        message: script.answer,
        recommendation: script.recommendation ?? null,
        records_changed: [],
      },
    },
  });
  onEvent({ event: "done", data: { conversation_id: conversationId } });
}

function chunkText(text: string): string[] {
  const chunks: string[] = [];
  const words = text.split(" ");
  for (let index = 0; index < words.length; index += 3) {
    const slice = words.slice(index, index + 3).join(" ");
    chunks.push(index === 0 ? slice : ` ${slice}`);
  }
  return chunks;
}

function wait(ms: number) {
  return new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms);
  });
}
