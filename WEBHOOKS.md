# Webhooks

## Protocolo real

```
signed_content = "{timestamp}.{raw_body_json}"
signature      = lowercase_hex(HMAC_SHA256(secret = endpoint_secret, message = signed_content))
```

Headers: `X-Webhook-Signature`, `X-Webhook-Timestamp`, `X-Webhook-Delivery-Id`.

## Verificação (sem chamada HTTP)

```python
from flask import Flask, request

@app.post("/webhooks/ishtaran")
def handle_webhook():
    raw_body = request.get_data(as_text=True)  # EXATO como recebido, nunca re-serializado
    valid = client.verify_webhook_signature(
        raw_body,
        request.headers["X-Webhook-Signature"],
        request.headers["X-Webhook-Timestamp"],
        endpoint_secret,
    )
    if not valid:
        return "", 401
    # processar o evento...
    return "", 200
```

Comparação em tempo constante (`hmac.compare_digest`), tolerância de replay de 5 minutos (padrão),
nunca loga o secret.

## Gestão de endpoints (Core, requer Member JWT)

```python
endpoint = client.webhook_endpoints.create(organization_id, "https://myapp.com/webhooks/ishtaran")
# endpoint.secret -- guarde AGORA, nunca recuperável depois

client.webhook_endpoints.rotate_secret(endpoint.webhook_endpoint_id)
client.webhook_endpoints.deactivate(endpoint.webhook_endpoint_id)
```
