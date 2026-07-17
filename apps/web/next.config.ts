import type { NextConfig } from "next";
import { join } from "node:path";

const nextConfig: NextConfig = {
  distDir: process.env.NEXT_DIST_DIR ?? ".next",
  outputFileTracingRoot: join(process.cwd(), "../.."),
  reactStrictMode: true,
  transpilePackages: ["@padalo/shared"],
};

export default nextConfig;
