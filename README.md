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
curl -N http://localhost:8000/sse
# Expected: event: endpoint

# Test tools interactively
npx @modelcontextprotocol/inspector http://localhost:8000/sse
```

## Architecture

Five Docker Compose services:

```
docs/ → nginx:8080 → indexer → qdrant:6333
                         ↓           ↓
                     mcp:8000 ←──────┘
```

**nginx** (`nginx:alpine`): Serves `docs/` as static files with `autoindex_format json` enabled. The indexer discovers files by crawling the JSON directory listing recursively — no manifest needed. Exposed on host port 8080.

**qdrant** (`qdrant/qdrant`): Vector DB storing 384-dim cosine embeddings. Persisted in named volume `qdrant_storage`. The collection is named `docs`. Exposed on host port 6333.

**indexer** (`./indexer/main.py`): One-shot Python job. Loads `all-MiniLM-L6-v2` from HuggingFace, crawls nginx JSON autoindex, fetches each `.md` file, splits into ~500-char overlapping chunks (50-char overlap), embeds them, and batch-upserts to Qdrant. Each point payload has `{path, chunk_index, content, source_url}`. `path` is a clean relative path (e.g. `api/authentication.md`, no leading `/docs/`). Runs after nginx and qdrant pass healthchecks.

**mcp** (`./mcp/server.py`): FastMCP server over SSE transport on port 8000. Loads the same embedding model at startup. Exposes three tools:
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
    "rag-docs": { "url": "http://localhost:8000/sse" }
  }
}
```
