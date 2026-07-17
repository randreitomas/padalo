import { expect, test } from "@playwright/test";

test("Santos Family demo loads through the local FastAPI service", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page.getByRole("heading", { name: "Santos Family" })).toBeVisible();
  await expect(page.getByText("Groceries", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Meralco", { exact: true }).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Upcoming bills" })).toBeVisible();
  await expect(page.getByText("Available balance", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("navigation", { name: "Primary navigation" }).first().getByRole("link"),
  ).toHaveText(["Dashboard", "Remittances", "Envelopes", "Transactions", "Bills", "Households"]);

  const hideSidebar = page.getByRole("button", { name: "Hide sidebar" });
  await expect(hideSidebar).toBeVisible();
  await hideSidebar.click();
  const showSidebar = page.getByRole("button", { name: "Show sidebar" });
  await expect(showSidebar).toBeVisible();
  await showSidebar.click();
  await expect(hideSidebar).toBeVisible();

  const assistantLauncher = page.getByRole("button", { name: "Ask PadaloAssist" });
  await expect(assistantLauncher).toBeVisible();
  await assistantLauncher.click();
  await expect(page.getByRole("dialog", { name: "PadaloAssist" })).toBeVisible();
  const assistantComposer = page.getByPlaceholder("Ask about a bill, envelope, or remittance");
  await expect(assistantComposer).toBeVisible();
  await expect(assistantComposer).toBeFocused();
  await page.getByRole("button", { name: "Close PadaloAssist" }).click();
  await expect(page.getByRole("dialog", { name: "PadaloAssist" })).toBeHidden();
  await expect(assistantLauncher).toBeFocused();
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBe(0);

  await page.getByRole("button", { name: "See more" }).click();
  await expect(page.getByText("FXPilot model view", { exact: true })).toBeVisible();
  await expect(page.getByAltText(/FXPilot deterministic backtest/i)).toBeVisible();
});
