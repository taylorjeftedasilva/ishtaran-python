"""
10 -- Verificacao de assinatura de webhook. Unico exemplo 100% executavel sem uma API real
rodando (calculo local, sem chamada HTTP) -- simula uma entrega real da plataforma.
"""

import time

from ishtaran import Environment, IshtaranClient
from ishtaran.webhook.webhook_signature_verifier import compute_webhook_signature

client = IshtaranClient.create(api_key="example-key-not-a-real-network-call", environment=Environment.LOCAL)

endpoint_secret = "whsec_example_secret_do_not_use_in_production"
raw_body = '{"eventType":"payment.received","amount":100}'
timestamp = int(time.time())

# Do lado da plataforma: assinatura calculada e enviada nos headers X-Webhook-Signature/
# X-Webhook-Timestamp junto com o raw_body como corpo da entrega HTTP real.
signature = compute_webhook_signature(timestamp, raw_body, endpoint_secret)
print("Assinatura calculada (simulando a plataforma):", signature)

# Do lado do integrador: verificacao real usando o SDK, sem chamada de rede.
valid = client.verify_webhook_signature(raw_body, signature, str(timestamp), endpoint_secret)
print("Assinatura valida?", valid)

# Payload adulterado depois do envio -- a verificacao deve rejeitar.
tampered_body = '{"eventType":"payment.received","amount":999999}'
tampered_valid = client.verify_webhook_signature(tampered_body, signature, str(timestamp), endpoint_secret)
print("Payload adulterado ainda valido?", tampered_valid, "(esperado: False)")
