# Installation Guide

This guide covers installation for all supported environments.

## System Requirements

- **OS:** Linux, macOS, or Windows (WSL2 recommended)
- **Memory:** 4GB RAM minimum, 8GB recommended
- **Disk:** 2GB free space
- **Network:** Internet access for initial setup

## Docker Installation (Recommended)

The easiest way to get started is with Docker:

```bash
# Pull the latest image
docker pull myproject/server:latest

# Run with default settings
docker run -d \
  -p 8080:8080 \
  -e API_KEY=your-key \
  myproject/server:latest
```

Using Docker Compose for a full stack:

```yaml
services:
  app:
    image: myproject/server:latest
    ports:
      - "8080:8080"
    environment:
      - API_KEY=${API_KEY}
      - DATABASE_URL=postgresql://db:5432/myproject
  db:
    image: postgres:16
    volumes:
      - pg_data:/var/lib/postgresql/data

volumes:
  pg_data:
```

## Manual Installation

### Python

```bash
pip install myproject-sdk
```

Verify:

```bash
python -c "import myproject; print(myproject.__version__)"
```

### Node.js

```bash
npm install @myproject/sdk
```

Verify:

```bash
node -e "const sdk = require('@myproject/sdk'); console.log(sdk.version)"
```

## From Source

```bash
git clone https://github.com/example/myproject.git
cd myproject
pip install -e ".[dev]"
```

## Verifying Installation

After installation, run the health check:

```bash
curl http://localhost:8080/health
# {"status": "ok", "version": "1.2.3"}
```

## Troubleshooting

**Port already in use:** Change the port with `-p 9090:8080`

**Permission denied:** Run with `sudo` or add your user to the `docker` group

**Cannot connect:** Check firewall rules allow traffic on port 8080
