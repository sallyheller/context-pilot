import { z } from "zod";
import { randomUUID } from "crypto";
import type Database from "better-sqlite3";

export const rememberSchema = z.object({
  content: z.string().describe("The decision or note to remember"),
  memory_type: z.enum(["decision", "pattern", "todo", "context_note"]),
  related_files: z.array(z.string()).optional(),
});

export type RememberInput = z.infer<typeof rememberSchema>;

export function handleRemember(
  db: Database.Database,
  projectId: string,
  sessionId: string,
  input: RememberInput
): string {
  const id = randomUUID();
  const now = Date.now();

  db.prepare(`
    INSERT INTO memories (id, project_id, session_id, memory_type, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(id, projectId, sessionId, input.memory_type, input.content, now);

  return JSON.stringify({ success: true, id, memory_type: input.memory_type });
}
