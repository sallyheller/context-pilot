import { z } from "zod";

export const getGraphSchema = z.object({
  target: z.string().describe("File path or function name"),
  depth: z.number().optional().default(2).describe("Graph traversal depth"),
  direction: z.enum(["incoming", "outgoing", "both"]).optional().default("both"),
});

export type GetGraphInput = z.infer<typeof getGraphSchema>;

export async function handleGetGraph(input: GetGraphInput): Promise<string> {
  // TODO Phase 3: query knowledge graph from Python engine
  return JSON.stringify({
    target: input.target,
    nodes: [],
    edges: [],
    message: "Knowledge graph not yet available. Coming in Phase 3.",
  });
}
