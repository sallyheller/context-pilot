Review the context-pilot codebase for clean architecture and potential issues.

Focus on:

1. **Boundary integrity** — TypeScript layer must not do work that belongs to Python (parsing, embedding, graph traversal). Python layer must not know about MCP protocol details.

2. **IPC protocol** — Verify Content-Length framing is consistent between `python-bridge.ts` and `main.py`. Check error handling and timeout logic in the bridge.

3. **Tool handlers** — Each tool in `mcp-server/src/tools/` should be a pure function receiving dependencies (bridge, db) as arguments. No global state in handlers.

4. **SQLite schema** — Check that migrations are versioned, foreign keys are enforced, and indices exist for all frequent queries.

5. **Python engine** — Verify `indexer.py` correctly handles unsupported file types and empty files. Check that `embedder.py` caches models and doesn't reload on every call.

6. **Security** — Confirm no user code paths are sent to external APIs. Check that `IGNORED_DIRS` and `IGNORED_FILES` in `indexer.py` cover sensitive files (.env, secrets).

For each issue found: show the file and line, explain the problem, and suggest the fix.
