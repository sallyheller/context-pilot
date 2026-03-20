import BetterSqlite3 from "better-sqlite3";
import { mkdirSync } from "fs";
import { dirname } from "path";
import { applySchema } from "./schema.js";

export function openDatabase(dbPath: string): BetterSqlite3.Database {
  mkdirSync(dirname(dbPath), { recursive: true });
  const db = new BetterSqlite3(dbPath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  applySchema(db);
  return db;
}
