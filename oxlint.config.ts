import { defineConfig } from "oxlint";

export default defineConfig({
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["vue", "typescript", "unicorn"],
  "rules": {
    "no-console": "warn",
    "no-debugger": "error",
    "no-unused-vars": "error",
    "eqeqeq": ["error", "always"],
    "prefer-const": "error",
    "no-var": "error",
    "object-shorthand": "error",
    "typescript/no-explicit-any": "warn",
    "typescript/no-non-null-assertion": "warn",
    "unicorn/prefer-module": "warn"
  },
  "ignorePatterns": [
    "out/**",
    "node_modules/**",
    "coverage/**",
    "*.d.ts"
  ]
});
