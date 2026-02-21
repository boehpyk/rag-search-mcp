# Getting Started

This guide helps you get up and running quickly.

## Prerequisites

- Node.js 18+ or Python 3.10+
- Docker (optional, recommended)
- An API key (see [Authentication](api/authentication.md))

## Installation

Install the SDK using your package manager:

```bash
# Node.js
npm install @myproject/sdk

# Python
pip install myproject-sdk
```

## Your First Request

```python
from myproject import Client

client = Client(api_key="your-api-key")
result = client.query("Hello, world!")
print(result)
```

## Next Steps

- Read the [API Overview](api/overview.md) to understand available endpoints
- Follow the [Configuration Guide](guides/configuration.md) to customize behavior
- Check [Installation](guides/installation.md) for detailed setup instructions
