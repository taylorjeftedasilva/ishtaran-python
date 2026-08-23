"""
10 -- Webhook signature verification. The only example 100% runnable without a real API running
(local computation, no HTTP call) -- simulates a real delivery from the platform.
"""

import time

from ishtaran import Environment, IshtaranClient
from ishtaran.webhook.webhook_signature_verifier import compute_webhook_signature

client = IshtaranClient.create(api_key="example-key-not-a-real-network-call", environment=Environment.LOCAL)

endpoint_secret = "whsec_example_secret_do_not_use_in_production"
raw_body = '{"eventType":"payment.received","amount":100}'
timestamp = int(time.time())

# Platform side: the signature is computed and sent in the X-Webhook-Signature/
# X-Webhook-Timestamp headers along with raw_body as the real HTTP delivery's body.
signature = compute_webhook_signature(timestamp, raw_body, endpoint_secret)
print("Computed signature (simulating the platform):", signature)

# Integrator side: real verification using the SDK, no network call.
valid = client.verify_webhook_signature(raw_body, signature, str(timestamp), endpoint_secret)
print("Signature valid?", valid)

# Payload tampered with after sending -- verification must reject it.
tampered_body = '{"eventType":"payment.received","amount":999999}'
tampered_valid = client.verify_webhook_signature(tampered_body, signature, str(timestamp), endpoint_secret)
print("Tampered payload still valid?", tampered_valid, "(expected: False)")
