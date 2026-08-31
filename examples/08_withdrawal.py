"""08 -- Execute a withdrawal via Easy Mode and wait (with timeout) until a terminal state."""

import os
from decimal import Decimal

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)

organization_id = os.environ["ISHTARAN_ORGANIZATION_ID"]
environment_id = os.environ["ISHTARAN_ENVIRONMENT_ID"]
account_id = os.environ["ISHTARAN_PAYER_ACCOUNT_ID"]
asset_network_id = os.environ["ISHTARAN_ASSET_NETWORK_ID"]

withdrawal = client.withdraw(organization_id, environment_id, account_id, asset_network_id, Decimal("50"), "TDestinationAddressReal")
print("withdrawal_id=", withdrawal.withdrawal_id)
# Under SelfCustody the beneficiary receives the full requested amount -- network_execution_cost is
# the real network cost, charged separately to the registered NetworkCostPayerAccount.
print(f"You receive {withdrawal.estimated_recipient_amount} (network execution cost: {withdrawal.network_execution_cost})")

final_state = client.withdrawals.wait_for(withdrawal.withdrawal_id, timeout_seconds=900, poll_interval_seconds=10)
print("Final status:", final_state.status.name)
