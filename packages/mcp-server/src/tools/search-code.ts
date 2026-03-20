import { z } from "zod";
import type { PythonBridge } from "../bridge/python-bridge.js";

export const searchCodeSchema = z.object({
  query: z.string().describe("Semantic search query"),
  k: z.number().optional().default(10).describe("Number of results"),
  filter_type: z.enum(["function", "class", "module", "any"]).optional().default("any"),
});

export type SearchCodeInput = z.infer<typeof searchCodeSchema>;

export async function handleSearchCode(
  input: SearchCodeInput,
  bridge: PythonBridge,
  projectPath: string
): Promise<string> {
  const result = await bridge.call("search", {
    query: input.query,
    project_path: projectPath,
    k: input.k ?? 10,
    filter_type: input.filter_type ?? "any",
  });
  return JSON.stringify(result);
}
