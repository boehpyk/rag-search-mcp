# Configuration Guide

Configure the application using environment variables or a config file.

## Environment Variables

| Variable          | Default       | Description                          |
|-------------------|---------------|--------------------------------------|
| `API_KEY`         | required      | Your API authentication key          |
| `PORT`            | `8080`        | Server listening port                |
| `LOG_LEVEL`       | `info`        | Logging level (debug/info/warn/error)|
| `DATABASE_URL`    | —             | PostgreSQL connection string         |
| `CACHE_TTL`       | `3600`        | Cache time-to-live in seconds        |
| `MAX_CONNECTIONS` | `100`         | Maximum concurrent connections       |
| `TIMEOUT`         | `30`          | Request timeout in seconds           |

## Configuration File

Create `config.yaml` in the working directory:

```yaml
server:
  port: 8080
  timeout: 30
  max_connections: 100

logging:
  level: info
  format: json

cache:
  ttl: 3600
  max_size: 1000

database:
  url: postgresql://localhost:5432/myproject
  pool_size: 10
  max_overflow: 20
```

Environment variables take precedence over the config file.

## Logging Configuration

Set structured JSON logging for production:

```yaml
logging:
  level: info
  format: json
  output: stdout
```

For development, use human-readable format:

```yaml
logging:
  level: debug
  format: text
```

## Database Configuration

Supported databases:
- PostgreSQL 14+ (recommended)
- SQLite (development only)

PostgreSQL connection string format:
```
postgresql://user:password@host:port/database?sslmode=require
```

## Caching

The application supports in-memory and Redis caching:

```yaml
cache:
  backend: redis
  url: redis://localhost:6379/0
  ttl: 3600
```

## TLS/SSL

Enable HTTPS:

```yaml
server:
  tls:
    enabled: true
    cert: /path/to/cert.pem
    key: /path/to/key.pem
```

Or use a reverse proxy (nginx, Caddy) for TLS termination.

## Production Recommendations

1. Set `LOG_LEVEL=warn` to reduce noise
2. Use a connection pool for the database
3. Enable Redis caching for high traffic
4. Set appropriate `TIMEOUT` values
5. Use TLS in production
