"""
11 -- Fluxo completo de Sandbox: credita saldo de teste via Faucet e confirma. Nunca funciona
contra Production real (o backend rejeita simulacoes fora de um Environment do tipo Sandbox).
"""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

environment_id = os.environ["ISHTARAN_SANDBOX_ENVIRONMENT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

observed_address = client.sandbox.faucet(environment_id, "TDepositAddressReal", asset_network_id, Decimal("100"))
print("sandbox_observed_address_id=", observed_address.sandbox_observed_address_id)

client.sandbox.simulate_confirmation(environment_id, observed_address.sandbox_observed_address_id, 3, True)
print("Confirmacao simulada -- o Deposit real sera processado via Outbox (assincrono).")

treasury_balance = client.sandbox.get_treasury_balance(environment_id, asset_network_id)
print("Treasury observada:", treasury_balance.balance)
