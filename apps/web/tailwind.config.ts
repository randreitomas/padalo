import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "../../packages/shared/src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#f4f7f6",
        surface: "#ffffff",
        ink: "#1d292a",
        muted: "#627072",
        line: "#dbe4e2",
        lagoon: "#0d766d",
        coral: "#c9573e",
        gold: "#aa7600",
        sky: "#2e6f9e",
        mist: "#e6f1ef",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(25, 41, 42, 0.05), 0 8px 24px rgba(25, 41, 42, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
