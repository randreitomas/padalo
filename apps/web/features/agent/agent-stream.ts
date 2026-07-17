import { z } from "zod";

const forecastRecommendationSchema = z
  .object({
    recommended_day: z.string(),
    expected_savings_php: z.string(),
    confidence: z.string(),
    provider: z.string(),
    amount_php: z.string(),
    is_mock: z.boolean(),
    disclaimer: z.string(),
  })
  .strict();

const finalResponseSchema = z
  .object({
    message: z.string(),
    recommendation: forecastRecommendationSchema.nullable(),
    records_changed: z.array(z.enum(["transaction", "remittance"])),
  })
  .strict();

const conversationSchema = z.object({ conversation_id: z.string().uuid() }).strict();
const statusSchema = z.object({ message: z.string() }).strict();
const toolCallSchema = z.object({ name: z.string() }).strict();
const toolResultSchema = z
  .object({
    call_id: z.string(),
    name: z.string(),
    ok: z.boolean(),
    data: z.record(z.string(), z.unknown()).nullable(),
    error: z.object({ code: z.string(), message: z.string() }).nullable(),
  })
  .strict();
const assistantDeltaSchema = z.object({ delta: z.string() }).strict();
const errorSchema = z.object({ code: z.string(), message: z.string() }).strict();
const doneSchema = z.object({ conversation_id: z.string().uuid().optional() }).strict();

export type ForecastRecommendation = z.infer<typeof forecastRecommendationSchema>;

export type AgentStreamEvent =
  | { event: "conversation"; data: z.infer<typeof conversationSchema> }
  | { event: "status"; data: z.infer<typeof statusSchema> }
  | { event: "tool_call"; data: z.infer<typeof toolCallSchema> }
  | { event: "tool_result"; data: z.infer<typeof toolResultSchema> }
  | { event: "assistant_delta"; data: z.infer<typeof assistantDeltaSchema> }
  | { event: "final"; data: { response: z.infer<typeof finalResponseSchema> } }
  | { event: "error"; data: z.infer<typeof errorSchema> }
  | { event: "done"; data: z.infer<typeof doneSchema> };

export async function consumeAgentStream(
  response: Response,
  onEvent: (event: AgentStreamEvent) => void,
) {
  if (!response.body) throw new Error("The assistant stream did not include a response body.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value, { stream: !done }).replaceAll("\r\n", "\n");

      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const block = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const event = parseEventBlock(block);
        if (event) onEvent(event);
        boundary = buffer.indexOf("\n\n");
      }

      if (done) break;
    }
  } finally {
    reader.releaseLock();
  }
}

function parseEventBlock(block: string): AgentStreamEvent | null {
  if (!block.trim()) return null;

  let eventName = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) eventName = line.slice("event:".length).trim();
    if (line.startsWith("data:")) dataLines.push(line.slice("data:".length).trimStart());
  }
  if (dataLines.length === 0) return null;

  const data = JSON.parse(dataLines.join("\n")) as unknown;
  switch (eventName) {
    case "conversation":
      return { event: "conversation", data: conversationSchema.parse(data) };
    case "status":
      return { event: "status", data: statusSchema.parse(data) };
    case "tool_call":
      return { event: "tool_call", data: toolCallSchema.parse(data) };
    case "tool_result":
      return { event: "tool_result", data: toolResultSchema.parse(data) };
    case "assistant_delta":
      return { event: "assistant_delta", data: assistantDeltaSchema.parse(data) };
    case "final":
      return {
        event: "final",
        data: z.object({ response: finalResponseSchema }).strict().parse(data),
      };
    case "error":
      return { event: "error", data: errorSchema.parse(data) };
    case "done":
      return { event: "done", data: doneSchema.parse(data) };
    default:
      return null;
  }
}
