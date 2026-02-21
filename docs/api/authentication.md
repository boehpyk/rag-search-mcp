# Authentication

All API requests require authentication using an API key.

## Getting an API Key

1. Sign up at https://example.com/signup
2. Navigate to **Settings → API Keys**
3. Click **Create New Key**
4. Copy and store the key securely — it won't be shown again

## Using Your API Key

Pass the key in the `Authorization` header:

```http
GET /v1/documents HTTP/1.1
Host: api.example.com
Authorization: Bearer sk-your-api-key-here
```

Or as an SDK parameter:

```python
client = Client(api_key="sk-your-api-key-here")
```

```javascript
const client = new Client({ apiKey: "sk-your-api-key-here" });
```

## Environment Variables

Store your key in an environment variable to avoid hardcoding it:

```bash
export API_KEY="sk-your-api-key-here"
```

```python
import os
client = Client(api_key=os.environ["API_KEY"])
```

## Key Scopes

Keys can be scoped to limit access:

| Scope       | Permissions                        |
|-------------|------------------------------------|
| `read`      | Read documents and query           |
| `write`     | Upload and delete documents        |
| `admin`     | Manage keys and billing            |

## Security Best Practices

- Never commit API keys to version control
- Rotate keys regularly
- Use scoped keys with minimum required permissions
- Store keys in a secrets manager in production

## Token Expiry

API keys do not expire by default. You can set an expiry date in the dashboard
or rotate them manually at any time.

## OAuth 2.0

For server-to-server integrations, we also support OAuth 2.0 client credentials flow.
See the OAuth documentation for details.
