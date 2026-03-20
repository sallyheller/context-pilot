import { Command } from "commander";
import { resolve, join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";
import chalk from "chalk";
import { openDatabase } from "@context-pilot/mcp-server/storage/sqlite.js";
import { createServer } from "@context-pilot/mcp-server/server.js";
import { PythonBridge } from "@context-pilot/mcp-server/bridge/python-bridge.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { startWatcher } from "../watcher.js";

export const serveCommand = new Command("serve")
  .description("Start the context-pilot MCP server")
  .argument("[path]", "Project root path", ".")
  .option("--db <path>", "Custom database path")
  .option("--watch", "Auto re-index on file changes", false)
  .action(async (projectPath: string, options: { db?: string; watch: boolean }) => {
    const root = resolve(projectPath);
    const configFile = join(root, ".context-pilot", "config.json");

    if (!existsSync(configFile)) {
      console.error(
        chalk.red("Not initialized.") +
          chalk.dim(` Run ${chalk.white("context-pilot init")} first.`)
      );
      process.exit(1);
    }

    const dbPath = options.db ?? join(homedir(), ".context-pilot", "db.sqlite");
    const db = openDatabase(dbPath);
    const server = createServer(db, root);
    const transport = new StdioServerTransport();

    process.stderr.write(`[context-pilot] serving ${root}\n`);

    if (options.watch) {
      // Re-use the bridge from inside createServer isn't exposed,
      // so we create a lightweight bridge just for the watcher
      const watcherBridge = new PythonBridge();
      watcherBridge.start();
      startWatcher(root, watcherBridge);
      process.stderr.write("[context-pilot] file watcher active\n");
    }

    await server.connect(transport);
  });
