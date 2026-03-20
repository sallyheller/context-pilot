Show the current development status of context-pilot and start the next pending task.

Steps:
1. Read `CLAUDE.md` to get the current phase
2. Read the relevant source files to understand what's already implemented
3. Identify the next concrete task to implement based on the roadmap:
   - Phase 3: knowledge graph (networkx) + intelligent ranking in `get-graph.ts` / `graph.py`
   - Phase 4: CLI commands (`init`, `status`, `serve`) in `packages/cli/`
   - Phase 5: incremental indexing (file hashes), chokidar file watcher, FAISS for large projects
4. Show a one-paragraph summary of what's done and what's next
5. Ask the user if they want to proceed, then implement the next task

Always update `CLAUDE.md` current phase when a phase is completed.
