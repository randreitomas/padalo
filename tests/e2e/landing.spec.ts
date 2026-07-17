import { expect, test } from "@playwright/test";

test("landing page presents the product story and opens the demo route", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("banner")).toHaveCount(0);
  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Send with care. Plan with clarity.",
    }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: "Start demo" })).toHaveCount(1);
  await expect(page.getByRole("link", { name: "Start demo" })).toHaveAttribute(
    "href",
    "/dashboard",
  );
  await expect(page.getByLabel("Padalo · Santos household")).toBeVisible();
  await expect(page.getByText("The problem", { exact: true })).toBeVisible();
  await expect(page.getByText("The solution", { exact: true })).toBeVisible();
  await expect(page.getByText("The product", { exact: true })).toBeVisible();
  await expect(
    page.getByText(
      "Every preview below is a focused part of Padalo, not a static image of the live app.",
    ),
  ).toHaveCount(0);
  await expect(page.getByRole("link", { name: "LinkedIn" })).toHaveAttribute(
    "href",
    "https://www.linkedin.com/in/randreitomas",
  );
});
