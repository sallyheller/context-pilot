import { z } from "zod";

export const indexProjectSchema = z.object({
  project_path: z.string().optional().describe("Path to project root (defaults to cwd)"),
  force: z.boolean().optional().default(false).describe("Force full re-index"),
  paths: z.array(z.string()).optional().describe("Specific paths to index"),
});

export type IndexProjectInput = z.infer<typeof indexProjectSchema>;

export async function handleIndexProject(input: IndexProjectInput): Promise<string> {
  // TODO Phase 2: spawn Python engine and trigger indexing
  const target = input.project_path ?? process.cwd();
  return JSON.stringify({
    success: false,
    project_path: target,
    message: "Indexing engine not yet available. Coming in Phase 2.",
  });
}
