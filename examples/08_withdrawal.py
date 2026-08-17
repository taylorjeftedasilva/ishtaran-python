"""08 -- Executar um saque via Easy Mode e esperar (com timeout) ate um estado terminal."""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

withdrawal = client.withdraw(organization_id, account_id, asset_network_id, Decimal("50"), "TDestinationAddressReal")
print("withdrawal_id=", withdrawal.withdrawal_id)
print(f"Voce recebe {withdrawal.estimated_recipient_amount} (taxa de rede: {withdrawal.estimated_network_fee})")

final_state = client.withdrawals.wait_for(withdrawal.withdrawal_id, timeout_seconds=900, poll_interval_seconds=10)
print("Status final:", final_state.status.name)
