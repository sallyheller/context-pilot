import { z } from "zod";

export const searchCodeSchema = z.object({
  query: z.string().describe("Semantic search query"),
  k: z.number().optional().default(10).describe("Number of results"),
  filter_type: z.enum(["function", "class", "module", "any"]).optional().default("any"),
});

export type SearchCodeInput = z.infer<typeof searchCodeSchema>;

export async function handleSearchCode(input: SearchCodeInput): Promise<string> {
  // TODO Phase 2: semantic search via Python embedding engine
  return JSON.stringify({
    query: input.query,
    results: [],
    message: "Search engine not yet available. Coming in Phase 2.",
  });
}
