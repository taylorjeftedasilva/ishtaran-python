"""09 -- Consultar saldo e historico de Ledger Entries (com paginacao real via generator lazy)."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

balance = client.get_balance(account_id, asset_network_id)
print(f"Available={balance.available} Pending={balance.pending} Reserved={balance.reserved}")

print("Ultimas entradas do Ledger:")
count = 0
for entry in client.ledger.list_all_entries(account_id, asset_network_id, page_size=20):
    print(f"  {entry.nature.name} {entry.amount} ({entry.origin_reference})")
    count += 1
    if count >= 50:
        break  # generator e lazy -- nunca carrega tudo de uma vez, seguro interromper cedo
