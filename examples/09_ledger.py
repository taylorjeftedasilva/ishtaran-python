"""09 -- Query balance and Ledger Entry history (with real pagination via a lazy generator)."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

balance = client.get_balance(account_id, asset_network_id)
print(f"Available={balance.available} Pending={balance.pending} Reserved={balance.reserved}")

print("Latest Ledger entries:")
count = 0
for entry in client.ledger.list_all_entries(account_id, asset_network_id, page_size=20):
    print(f"  {entry.nature.name} {entry.amount} ({entry.origin_reference})")
    count += 1
    if count >= 50:
        break  # the generator is lazy -- never loads everything at once, safe to break early
