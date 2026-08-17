"""06 -- Liquidar uma Transaction financiada (Settlement) e consultar o resumo."""

import os

from ishtaran import Environment, IshtaranClient

client = IshtaranClient.create(api_key=os.environ.get("ISHTARAN_API_KEY"), environment=Environment.LOCAL)
transaction_id = os.environ["ISHTARAN_TRANSACTION_ID"]

result = client.settlements.execute_settlement(transaction_id)
print("settlement_id=", result.settlement_id)

settlement = client.settlements.get(result.settlement_id)
print(f"grossAmount={settlement.gross_amount}, platformFeeAmount={settlement.platform_fee_amount}, distributableAmount={settlement.distributable_amount}")

summary = client.settlements.get_summary(transaction_id)
print(f"settledAmount={summary.settled_amount}, retainedAmount={summary.retained_amount}")
