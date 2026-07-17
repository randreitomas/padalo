# Three-Minute Judge Walkthrough

## Before The Judge Arrives

1. Open the landing page and the dashboard in separate tabs.
2. Confirm `GET /health` returns `{"status":"ok","service":"padalo-api"}`.
3. Confirm the Santos Family data is present and the OpenAI key is configured.
4. Use **Reset demo** once, then reload the dashboard. This clears the browser conversation and
   restores the deterministic seeded household.

## The Story

Padalo helps an OFW family make a shared decision from a neutral record. Maria sends money from
Dubai; Ana and Jose need a clear view of available envelopes, bills, and savings in Quezon City.
The product deliberately avoids surveillance and blame. It gives everyone the same planning context.

## Click Sequence

| Time      | Action                                                      | Talking point                                                          | Expected result                                                                                 |
| --------- | ----------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 0:00-0:20 | Start on `/`                                                | "Padalo is shared household finance for OFW families."                 | Landing page explains the product, AI boundary, and FXPilot.                                    |
| 0:20-0:40 | Scroll to the dashboard capture                             | "The demo begins with a real household picture, not an empty app."     | Santos Family envelopes, bills, assistant, and FXPilot are visible.                             |
| 0:40-1:05 | Click **Open demo**                                         | "Maria, Ana, and Jose see the same commitments."                       | Dashboard loads the deterministic Santos Family ledger.                                         |
| 1:05-1:35 | Point to envelopes, recent transactions, and upcoming bills | "This turns remittances into shared planning context."                 | Groceries, Education, Bills, Savings, Meralco, Converge, and Tuition are visible.               |
| 1:35-2:05 | Click **Can we still afford tuition?**                      | "The assistant uses typed household tools and shows what it checks."   | Visible SSE progress and a grounded household answer.                                           |
| 2:05-2:40 | Click **When should I send money?**                         | "FXPilot is a provider-behavior forecast, not FX speculation."         | `forecast_remittance` runs, FXPilot updates with Thursday, savings, confidence, and disclaimer. |
| 2:40-3:00 | Open **Reset demo**                                         | "We can reset the full judge state without touching other households." | Confirmation explains seeded-data reset and conversation clearing.                              |

## Prompts And Expected Outputs

| Prompt                             | Tool emphasis                    | Expected outcome                                                                             |
| ---------------------------------- | -------------------------------- | -------------------------------------------------------------------------------------------- |
| Can we still afford tuition?       | Budget status and upcoming bills | A calm explanation of the Education envelope and near-term commitments.                      |
| When should I send money?          | `forecast_remittance`            | Thursday, modeled savings, historical-pattern confidence, and synthetic-data disclaimer.     |
| Where did our money go this month? | Transaction search               | A neutral summary of recent groceries, medicine, education, utilities, and savings movement. |
| Show upcoming bills.               | Upcoming bills                   | Meralco, Converge, Tuition, and Water District with their dates and total due.               |
| Log a grocery expense.             | Expense logging                  | The assistant asks only for missing details, then confirms a successful ledger record.       |
| Summarize our budget.              | Budget status                    | A shared household summary without blame or surveillance language.                           |

## Contingency Plan

| Situation                      | Do this                                                                                    | Keep saying                                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| OpenAI is unavailable          | Use the landing page, seeded dashboard, FXPilot card, and `docs/fxpilot.md`.               | "The model boundary is typed and the forecast runs independently of the chat provider."      |
| API is waking or unavailable   | Show the landing capture first, then check `/health` and retry the dashboard.              | "The product has a friendly retry state and no household change occurs on a failed request." |
| Demo data was changed          | Use **Reset demo**. If reset is intentionally disabled locally, run `npm run db:seed:win`. | "The reset touches only the fixed Santos Family demo household."                             |
| Network is unreliable          | Use the committed screenshots, Mermaid diagrams, backtest artifact, and documentation.     | "The demo dataset and forecast report are deterministic and versioned in the repository."    |
| Forecast question takes longer | Point to the SSE progress items.                                                           | "The interface tells the family which household context is being reviewed."                  |

## Close

End on the shared decision, not the prediction: Padalo helps a family discuss what is available,
what is due, and when to send money from one trusted household record.
