import os
import requests
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

NGINX_BASE_URL = os.environ.get("NGINX_BASE_URL", "http://nginx")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "docs"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Connecting to Qdrant...")
qdrant = QdrantClient(url=QDRANT_URL)

mcp = FastMCP("rag-docs", host="0.0.0.0", port=8000)


@mcp.tool()
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Semantic search over indexed documentation chunks.

    Args:
        query: The search query in natural language.
        limit: Maximum number of results to return (default 5).

    Returns:
        List of matching chunks with path, score, content, and chunk_index.
    """
    vector = model.encode(query).tolist()
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )
    return [
        {
            "path": hit.payload["path"],
            "score": round(hit.score, 4),
            "content": hit.payload["content"],
            "chunk_index": hit.payload["chunk_index"],
        }
        for hit in results
    ]


@mcp.tool()
def get_document(path: str) -> dict:
    """Retrieve the full content of a documentation file.

    Args:
        path: Relative path to the document, e.g. 'api/authentication.md'.

    Returns:
        Dict with path, url, content, and size in bytes.
    """
    # Sanitize: strip leading slashes and reject path traversal
    clean = path.lstrip("/")
    if ".." in clean:
        raise ValueError("Path traversal not allowed")

    url = f"{NGINX_BASE_URL}/docs/{clean}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    content = resp.text

    return {
        "path": clean,
        "url": url,
        "content": content,
        "size": len(content.encode("utf-8")),
    }


@mcp.tool()
def list_documents() -> dict:
    """List all indexed documentation files and their structure.

    Returns:
        Dict with total_documents, total_chunks, a nested tree, and flat_list of paths.
    """
    all_paths = set()
    offset = None

    while True:
        result, next_offset = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=None,
            limit=256,
            offset=offset,
            with_payload=["path"],
            with_vectors=False,
        )
        for point in result:
            all_paths.add(point.payload["path"])

        if next_offset is None:
            break
        offset = next_offset

    # Count total chunks (separate scroll would be needed for exact count;
    # use collection info instead)
    info = qdrant.get_collection(COLLECTION_NAME)
    total_chunks = info.points_count

    flat_list = sorted(all_paths)

    # Build nested tree
    tree: dict = {}
    for path in flat_list:
        parts = path.split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None  # leaf

    return {
        "total_documents": len(flat_list),
        "total_chunks": total_chunks,
        "tree": tree,
        "flat_list": flat_list,
    }


if __name__ == "__main__":
    print("Starting MCP SSE server on 0.0.0.0:8000")
    mcp.run(transport="sse")
