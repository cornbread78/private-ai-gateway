# Rosie AI Gateway - API Authentication & Security

Rosie AI Gateway enforces strict header checks and Bearer token authentication to prevent unauthorized inference and ensure zero-leakage payload routing inside TEE memory.

---

## 🔑 Authentication Credentials

By default, the gateway checks incoming requests against the `ROSIE_API_KEY` environment variable.

* **Default Local Key**: `rosie-secret-key-123`
* **Production Override**: Pass `ROSIE_API_KEY="your-custom-secure-key"` in `compose.yaml` or container environment variables.

---

## 📋 Required HTTP Headers

All POST requests to `/v1/chat/completions` or `/v1/messages` must include:

| Header | Value | Description |
| :--- | :--- | :--- |
| `Authorization` | `Bearer <ROSIE_API_KEY>` | Bearer token authorization |
| `Content-Type` | `application/json` | JSON payload specification |

---

## 💻 Code Examples

### 1. cURL Example

```bash
curl -X POST http://localhost:8080/v1/chat/completions   -H "Authorization: Bearer rosie-secret-key-123"   -H "Content-Type: application/json"   -d '{
    "model": "rosie-private",
  }'
```

---

## 🚨 Error Handling

* **401 Unauthorized**: Missing or invalid `Authorization` header.
* **400 Bad Request**: Missing `Content-Type: application/json` header.
