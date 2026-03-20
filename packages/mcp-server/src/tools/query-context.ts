import { z } from "zod";

export const queryContextSchema = z.object({
  prompt: z.string().describe("The task or question to find context for"),
  active_file: z.string().optional().describe("Current file being edited (relative to project root)"),
  token_budget: z.number().optional().default(8000).describe("Max tokens to return"),
  context_types: z
    .array(z.enum(["code", "decisions", "patterns", "all"]))
    .optional()
    .default(["all"]),
});

export type QueryContextInput = z.infer<typeof queryContextSchema>;

export async function handleQueryContext(input: QueryContextInput): Promise<string> {
  // TODO Phase 2: call Python embedding engine for semantic search
  // TODO Phase 3: rank results and assemble context within token budget
  return JSON.stringify({
    context: "<!-- context-pilot: embedding engine not yet initialized -->",
    sources: [],
    token_count: 0,
    message: "Indexing not yet available. Run `context-pilot index` first.",
  });
}
