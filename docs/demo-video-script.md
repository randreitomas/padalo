# Padalo Demo Video Script (under 3:00)

Spoken length target: **~2:45**. Leave ~15 seconds of buffer for UI load and pauses.
Pace: calm, clear, about 140 words per minute. Do not rush the assistant answers.

## Prep (off camera)

1. Reset the demo once, then reload `/dashboard`.
2. Confirm `GET /health` is ok and the Santos Family data is seeded.
3. Open `/` in the recording tab. Keep `/dashboard` ready if needed.
4. Hide desktop notifications. Use a 16:9 browser window.

## Shot Plan And Narration

| Time | On screen | Say this |
| ---- | --------- | -------- |
| **0:00–0:18** | Landing hero: “Send with care. Plan with clarity.” | “This is Padalo: shared household finance for OFW families. Maria sends money from Dubai. Ana and Jose coordinate at home. The hard part is not the transfer. It is keeping one calm, shared picture of what arrived, what is due, and what is still available.” |
| **0:18–0:32** | Scroll briefly through Product / Architecture, then click **Start demo** | “Padalo is a household ledger, a typed AI assistant, and FXPilot, a timing companion based on provider behavior, not FX trading.” |
| **0:32–0:55** | Dashboard overview. Slow pan across KPIs, envelopes, recent transactions, upcoming bills | “Here is the Santos Family demo. Everyone sees the same envelopes: groceries, education, bills, savings. Recent spending is visible. Upcoming commitments like Meralco, Converge, and tuition sit in one place. No surveillance. Just shared planning context.” |
| **0:55–1:10** | Click into **Remittances** (or highlight remittance history on dashboard if already visible), then return to dashboard chat | “Maria’s remittances are already part of the record, so the family is not reconstructing the story from chat threads.” |
| **1:10–1:45** | Open PadaloAssist. Click **Can we still afford tuition?** Watch the tool-progress timeline, then the answer | “Ask a practical question. PadaloAssist uses typed household tools only. The model never touches the database directly. You can see what it checks: balances, bills, recent activity. Then it answers in language the family can use together.” |
| **1:45–2:20** | Click **When should I send money?** Show FXPilot card updating | “Next: when should Maria send? FXPilot forecasts provider behavior patterns from deterministic synthetic history. It recommends a day, shows modeled savings and confidence, and keeps the synthetic-data disclaimer visible. It is a timing signal, never a live quote or a guarantee.” |
| **2:20–2:40** | Optional quick click: **Show upcoming bills** or **Log a grocery expense** if time allows; otherwise stay on FXPilot + dashboard | “The same assistant can summarize the budget, list bills, or log an expense into the shared ledger. Every action stays household-scoped and reviewable.” |
| **2:40–2:55** | Hover or open **Reset demo**, then end on the dashboard composition | “And for a live demo, Reset demo restores only the Santos Family household and clears the browser conversation. Padalo helps a family decide from one trusted record: what is available, what is due, and when to send care home.” |

**Hard stop at 3:00.** Prefer ending early on the close line rather than cramming another click.

## Full Voiceover (read-through)

Use this if you prefer a continuous teleprompter script. Total: about **390 words**.

---

This is Padalo: shared household finance for OFW families.

Maria sends money from Dubai. Ana and Jose coordinate at home. The hard part is not the transfer. It is keeping one calm, shared picture of what arrived, what is due, and what is still available.

Padalo combines a household ledger, a typed AI assistant, and FXPilot, a timing companion based on provider behavior, not foreign-exchange trading.

Here is the Santos Family demo. Everyone sees the same envelopes: groceries, education, bills, and savings. Recent spending is visible. Upcoming commitments like Meralco, Converge, and tuition sit in one place. No surveillance. Just shared planning context.

Maria’s remittances are already part of the record, so the family is not reconstructing the story from chat threads.

Ask a practical question: can we still afford tuition? PadaloAssist uses typed household tools only. The model never touches the database directly. You can see what it checks: balances, bills, recent activity. Then it answers in language the family can use together.

Next: when should Maria send? FXPilot forecasts provider behavior patterns from deterministic synthetic history. It recommends a day, shows modeled savings and confidence, and keeps the synthetic-data disclaimer visible. It is a timing signal, never a live quote or a guarantee.

The same assistant can summarize the budget, list bills, or log an expense into the shared ledger. Every action stays household-scoped and reviewable.

And for a live demo, Reset demo restores only the Santos Family household and clears the browser conversation.

Padalo helps a family decide from one trusted record: what is available, what is due, and when to send care home.

---

## Feature Coverage Checklist

| Feature | Covered in |
| ------- | ---------- |
| Landing / product story | 0:00–0:32 |
| Shared ledger / envelopes | 0:32–0:55 |
| Transactions and bills | 0:32–0:55, 2:20–2:40 |
| Remittances | 0:55–1:10 |
| PadaloAssist + typed tools + SSE progress | 1:10–1:45 |
| FXPilot forecast + disclaimer | 1:45–2:20 |
| Expense logging / budget / bills prompts | 2:20–2:40 |
| Demo Mode reset | 2:40–2:55 |
| Trust framing (no surveillance, no direct DB access) | throughout |

## If Something Fails Mid-Take

| Problem | Cut to | Keep saying |
| ------- | ------ | ----------- |
| Assistant is slow | Progress timeline | “The interface shows which household context is being reviewed.” |
| OpenAI unavailable | Seeded dashboard + FXPilot card | “The forecast and ledger still stand on their own.” |
| Data drifted | Reset demo, then continue | “Reset restores only the fixed Santos Family demo.” |

## Recording Tips

- Click once, pause half a second, then speak over the result.
- Zoom 110–125% so KPIs and the FXPilot card read on mobile playback.
- Prefer natural mouse movement over rapid scrubbing.
- End on the dashboard, not the landing page.
