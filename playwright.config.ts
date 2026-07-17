import { defineConfig, devices } from "@playwright/test";

const localChrome =
  process.platform === "win32"
    ? "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    : undefined;

const devCommand =
  process.platform === "win32"
    ? "npm.cmd run dev --workspace @padalo/web"
    : "npm run dev --workspace @padalo/web";

const apiCommand = process.platform === "win32" ? "npm.cmd run dev:api:win" : "npm run dev:api";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: process.env.PADALO_E2E_BASE_URL ?? "http://localhost:3000",
    ...devices["Desktop Chrome"],
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ?? localChrome,
    },
  },
  webServer: [
    {
      command: devCommand,
      url: "http://localhost:3000",
      reuseExistingServer: !process.env.CI,
    },
    {
      command: apiCommand,
      url: "http://localhost:8000/health",
      reuseExistingServer: !process.env.CI,
    },
  ],
});
