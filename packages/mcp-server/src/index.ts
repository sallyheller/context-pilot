import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { join } from "path";
import { homedir } from "os";
import { openDatabase } from "./storage/sqlite.js";
import { createServer } from "./server.js";

const DB_PATH = join(homedir(), ".context-pilot", "db.sqlite");

async function main(): Promise<void> {
  const db = openDatabase(DB_PATH);
  const server = createServer(db);
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("context-pilot: fatal error", err);
  process.exit(1);
});
