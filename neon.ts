import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  buckets: {
    "tenderguard-documents": {},
  },
  branch: (branch) => {
    if (branch.isDefault) {
      return {};
    }
    if (!branch.exists) {
      return { ttl: "7d" };
    }
    return {};
  },
});
