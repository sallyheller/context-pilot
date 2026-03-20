# context-pilot 🧠

> Intelligent context middleware for AI coding agents. MCP-compatible, 100% local, privacy-first.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-blue)](https://modelcontextprotocol.io)
[![Status: WIP](https://img.shields.io/badge/status-work--in--progress-orange)]()

---

## The Problem

When using Claude Code, Cursor, or any AI coding agent with local LLMs (Ollama, LM Studio), context fills up fast. The agent "forgets" important parts of your codebase, injects irrelevant snippets, and loses architectural decisions across sessions.

There's no universal layer that manages **what context to inject, when, and in what format**.

## The Solution

**context-pilot** is a middleware [MCP server](https://modelcontextprotocol.io) that sits between your AI client and your codebase:

- Builds a **local knowledge graph** of your project (files, functions, dependencies, architectural decisions)
- **Dynamically selects** the most relevant context fragments for each prompt using local embeddings
- Works as a **universal MCP server** — connects to any compatible client (Claude Code, Cursor, Continue.dev...)
- **Persistent memory** across sessions with local embeddings — nothing leaves your machine

```
┌─────────────┐     MCP      ┌──────────────────┐     IPC      ┌─────────────────┐
│  AI Client  │◄────────────►│  context-pilot   │◄────────────►│ Embedding Engine│
│(Claude Code)│              │   MCP Server     │              │    (Python)     │
└─────────────┘              └──────────────────┘              └─────────────────┘
                                      │                                  │
                                      └──────────┬───────────────────────┘
                                                 ▼
                                        ┌────────────────┐
                                        │  SQLite DB     │
                                        │  (local only)  │
                                        └────────────────┘
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `query_context` | Get the most relevant context for your current task |
| `index_project` | Index or re-index your codebase |
| `remember` | Persist architectural decisions across sessions |
| `get_graph` | Explore dependency graphs around a file or function |
| `search_code` | Semantic search across your codebase |

## Quick Start

> ⚠️ Work in progress. Installation instructions coming soon.

```bash
# Install
npm install -g @context-pilot/cli

# Initialize in your project
cd my-project
context-pilot init

# Add to Claude Code
claude mcp add context-pilot -- context-pilot serve
```

## Stack

- **TypeScript/Node.js** — MCP server, CLI, protocol handling
- **Python** — Embeddings (`sentence-transformers/all-MiniLM-L6-v2`), knowledge graph (`networkx`), code parsing (`tree-sitter`)
- **SQLite** — Local persistence, no external databases

## Supported Languages

- TypeScript / JavaScript
- Python
- Go *(planned)*
- Rust *(planned)*

## Roadmap

- [x] Project architecture
- [ ] MCP server scaffold
- [ ] Embedding engine (indexing + semantic search)
- [ ] Knowledge graph construction
- [ ] Intelligent context ranking
- [ ] CLI (`init`, `status`, `serve`)
- [ ] Incremental indexing + file watcher
- [ ] FAISS support for large projects

## Contributing

This project is in early development. Contributions, ideas, and feedback are welcome — open an issue!

## License

MIT
