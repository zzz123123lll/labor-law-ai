import { defineConfig } from "vitest/config";
import path from "path";

const ROOT = path.resolve(__dirname);

export default defineConfig({
  test: {
    root: ROOT,
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    include: ["__tests__/**/*.test.{ts,tsx}"],
    exclude: ["**/node_modules/**", "**/.next/**", "**/.bun/**", "**/.claude/**", "**/dist/**"],
  },
  resolve: {
    alias: {
      "@": ROOT,
    },
  },
});
