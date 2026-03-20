import { z } from "zod";
import type { PythonBridge } from "../bridge/python-bridge.js";

export const indexProjectSchema = z.object({
  project_path: z.string().optional().describe("Path to project root (defaults to cwd)"),
  force: z.boolean().optional().default(false).describe("Force full re-index"),
  paths: z.array(z.string()).optional().describe("Specific paths to index"),
});

export type IndexProjectInput = z.infer<typeof indexProjectSchema>;

export async function handleIndexProject(
  input: IndexProjectInput,
  bridge: PythonBridge
): Promise<string> {
  const result = await bridge.call("index", {
    project_path: input.project_path ?? process.cwd(),
    force: input.force ?? false,
  });
  return JSON.stringify(result);
}
