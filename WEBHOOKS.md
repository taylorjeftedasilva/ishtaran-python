# Webhooks

## Real protocol

```
signed_content = "{timestamp}.{raw_body_json}"
signature      = lowercase_hex(HMAC_SHA256(secret = endpoint_secret, message = signed_content))
```

Headers: `X-Webhook-Signature`, `X-Webhook-Timestamp`, `X-Webhook-Delivery-Id`.

## Verification (no HTTP call)

```python
from flask import Flask, request

@app.post("/webhooks/ishtaran")
def handle_webhook():
    raw_body = request.get_data(as_text=True)  # EXACT as received, never re-serialized
    valid = client.verify_webhook_signature(
        raw_body,
        request.headers["X-Webhook-Signature"],
        request.headers["X-Webhook-Timestamp"],
        endpoint_secret,
    )
    if not valid:
        return "", 401
    # process the event...
    return "", 200
```

Constant-time comparison (`hmac.compare_digest`), 5-minute replay tolerance (default), never
logs the secret.

## Endpoint management (Core, requires Member JWT)

```python
endpoint = client.webhook_endpoints.create(organization_id, "https://myapp.com/webhooks/ishtaran")
# endpoint.secret -- save it NOW, never retrievable afterward

client.webhook_endpoints.rotate_secret(endpoint.webhook_endpoint_id)
client.webhook_endpoints.deactivate(endpoint.webhook_endpoint_id)
```
