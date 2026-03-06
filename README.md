# MCP search tool with RAG indexer for the given URL

## What This Is

A Dockerized RAG (Retrieval-Augmented Generation) POC. Markdown files in `docs/` are indexed into a Qdrant vector database and exposed via an MCP server with three tools: semantic search, full document retrieval, and directory listing.

## Common Commands

```bash
# Build and start all services (indexer runs once then exits)
docker compose up --build

# Watch indexer complete (ends with "=== Indexer done. Exiting. ===")
docker compose logs -f indexer

# Re-index after adding/changing docs (always wipes and recreates the collection)
docker compose restart indexer

# Check Qdrant has indexed points
curl http://localhost:6333/collections/docs

# Verify MCP SSE endpoint is live
curl -N http://localhost:8989/sse
# Expected: event: endpoint

# Test tools interactively
npx @modelcontextprotocol/inspector --cli http://localhost:8989/sse --method tools/list
```

## Local Setup: npx vs pnpm

Use whichever tool is available on your machine:

```bash
# Option A: npm/npx available
npx @modelcontextprotocol/inspector --cli http://localhost:8989/sse --method tools/list

# Option B: npx unavailable/broken, but pnpm is installed
pnpm dlx @modelcontextprotocol/inspector --cli http://localhost:8989/sse --method tools/list
```

Quick checks:

```bash
command -v npx
command -v pnpm
```

## Troubleshooting Healthchecks

If `docker compose up` fails with `dependency failed to start: container ... is unhealthy`, check the healthchecks in `docker-compose.yml`:

- `nginx` must probe IPv4 loopback:
  - `http://127.0.0.1/docs/`
  - Using `localhost` may fail in some containers due to IPv6 loopback resolution.
- `qdrant` image may not include `wget`:
  - Prefer a shell/TCP probe like `bash -c "</dev/tcp/127.0.0.1/6333"`
  - Do not assume `wget` exists in minimal images.

After updating healthchecks, recreate services:

```bash
docker compose down
docker compose up -d
docker compose ps
```

## Architecture

Five Docker Compose services:

```
docs/ → nginx:8080 → indexer → qdrant:6333
                         ↓           ↓
           mcp:8989 ←──────┘
```

**nginx** (`nginx:alpine`): Serves `docs/` as static files with `autoindex_format json` enabled. The indexer discovers files by crawling the JSON directory listing recursively — no manifest needed. Exposed on host port 8080.

**qdrant** (`qdrant/qdrant`): Vector DB storing 384-dim cosine embeddings. Persisted in named volume `qdrant_storage`. The collection is named `docs`. Exposed on host port 6333.

**indexer** (`./indexer/main.py`): One-shot Python job. Loads `all-MiniLM-L6-v2` from HuggingFace, crawls nginx JSON autoindex, fetches each `.md` file, splits into ~500-char overlapping chunks (50-char overlap), embeds them, and batch-upserts to Qdrant. Each point payload has `{path, chunk_index, content, source_url}`. `path` is a clean relative path (e.g. `api/authentication.md`, no leading `/docs/`). Runs after nginx and qdrant pass healthchecks.

**mcp** (`./mcp/server.py`): FastMCP server over SSE transport on port 8989. Loads the same embedding model at startup. Exposes three tools:
- `search_docs(query, limit=5)` — embeds query, searches Qdrant, returns scored chunks
- `get_document(path)` — fetches full doc from nginx; rejects `..` path traversal
- `list_documents()` — scrolls all Qdrant points to build unique path list + nested tree + chunk count

**hf_cache** (named volume): Shared HuggingFace model cache mounted into both `indexer` and `mcp` at `/root/.cache/huggingface`, so the model is only downloaded once.

## Adding Documentation

Drop `.md` files anywhere under `docs/`, then `docker compose restart indexer`. Subdirectory structure is auto-discovered.

## MCP Client Configuration

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "rag-docs": { "url": "http://localhost:8989/sse" }
  }
}
```

## VS Code MCP Quick Check

1. Start services and keep them running:

```bash
docker compose up -d
```

2. Ensure your workspace has an MCP config like this in `.mcp.json`:

```json
{
  "mcpServers": {
    "rag-docs": {
      "type": "sse",
      "url": "http://127.0.0.1:8989/sse"
    }
  }
}
```

3. Reload VS Code window (`Developer: Reload Window`).
4. Open Copilot Chat and run a prompt that should use docs search.
5. If needed, verify endpoint manually:

```bash
curl -N http://127.0.0.1:8989/sse
```

Troubleshooting (Inspector command):

- If `npx` works:

```bash
npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8989/sse --method tools/list
```

- If `npx` is unavailable/broken, use `pnpm`:

```bash
pnpm dlx @modelcontextprotocol/inspector --cli http://127.0.0.1:8989/sse --method tools/list
```
