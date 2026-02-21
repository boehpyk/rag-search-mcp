# API Overview

The REST API provides programmatic access to all project features.

## Base URL

```
https://api.example.com/v1
```

## Endpoints

| Method | Path              | Description                  |
|--------|-------------------|------------------------------|
| GET    | /health           | Health check                 |
| POST   | /query            | Submit a query               |
| GET    | /documents        | List all documents           |
| POST   | /documents        | Upload a document            |
| GET    | /documents/{id}   | Retrieve a specific document |
| DELETE | /documents/{id}   | Delete a document            |

## Request Format

All requests must include:
- `Content-Type: application/json`
- `Authorization: Bearer <api-key>` (see [Authentication](authentication.md))

## Response Format

All responses return JSON:

```json
{
  "status": "ok",
  "data": { 
    "user_id": "abc123",
    "documents": "mcp://abc123/documents.jsonl"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Rate Limits

- Free tier: 100 requests/minute
- Pro tier: 1000 requests/minute
- Enterprise: unlimited

## Error Codes

| Code | Meaning               |
|------|-----------------------|
| 400  | Bad request           |
| 401  | Unauthorized          |
| 404  | Not found             |
| 429  | Rate limit exceeded   |
| 500  | Internal server error |
