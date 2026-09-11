import json

from ishtaran.model.enums import ExecutionStatus
from ishtaran.resources.transactions_resource import TransactionsResource
from .fake_transport import FakeHttpTransport


def test_search_executions_scopes_by_organization_id_and_forwards_query_params() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, "[]"))
    resource = TransactionsResource(fake)

    resource.search_executions(
        "org-1",
        status=ExecutionStatus.OVERDUE,  # type: ignore[attr-defined]
        transaction_id="tx-1",
        settlement_id="stl-1",
        skip=10,
        take=25,
    )

    assert fake.received[0].method == "GET"
    path = fake.received[0].path
    assert path.startswith("/v1/organizations/org-1/executions?")
    assert "status=5" in path
    assert "transactionId=tx-1" in path
    assert "settlementId=stl-1" in path
    assert "skip=10" in path
    assert "take=25" in path


def test_search_executions_maps_nullable_executed_at_and_settlement_id() -> None:
    body = json.dumps([
        {
            "executionId": "ex-1", "transactionId": "tx-1", "organizationId": "org-1",
            "status": 5, "preparedAt": "2026-08-01T12:00:00Z", "gracePeriodExpiresAt": "2026-08-01T13:00:00Z",
            "executedAt": None, "settlementId": None,
        },
    ])
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = TransactionsResource(fake)

    executions = resource.search_executions("org-1")

    assert len(executions) == 1
    assert executions[0].execution_id == "ex-1"
    assert executions[0].status.name == "OVERDUE"  # type: ignore[attr-defined]
    assert executions[0].executed_at is None
    assert executions[0].settlement_id is None
