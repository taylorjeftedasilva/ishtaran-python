import json
from decimal import Decimal

from ishtaran.resources.wallet_balance_resource import WalletBalanceResource
from .fake_transport import FakeHttpTransport


def test_get_balance_gets_the_cached_snapshot_and_parses_freshness_fields() -> None:
    body = json.dumps(
        {
            "accountId": "acc-1",
            "assetNetworkId": "an-1",
            "address": "TWallet1",
            "balance": 100.5,
            "observedAt": "2026-09-11T12:00:00Z",
            "blockReference": "block-1",
            "source": "sandbox",
            "stale": False,
            "nextRefreshAllowedAt": None,
            "refreshSuppressed": False,
            "refreshFailureReason": None,
        }
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = WalletBalanceResource(fake)

    result = resource.get_balance("acc-1", "env-1", "an-1")

    assert result.balance == Decimal("100.5")
    assert result.address == "TWallet1"
    assert result.stale is False
    assert fake.received[0].method == "GET"
    assert fake.received[0].path == "/v1/accounts/acc-1/wallet-balances?environmentId=env-1&assetNetworkId=an-1"


def test_get_balance_never_observed_yet_reports_zero_balance_never_a_lie() -> None:
    body = json.dumps(
        {
            "accountId": "acc-1", "assetNetworkId": "an-1", "address": "TWallet1", "balance": 0,
            "observedAt": None, "blockReference": None, "source": None, "stale": True,
            "nextRefreshAllowedAt": None, "refreshSuppressed": False, "refreshFailureReason": None,
        }
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = WalletBalanceResource(fake)

    result = resource.get_balance("acc-1", "env-1", "an-1")

    assert result.observed_at is None
    assert result.balance == Decimal("0")
    assert result.stale is True


def test_refresh_balance_posts_with_no_body_never_tells_the_platform_what_the_balance_should_be() -> None:
    body = json.dumps(
        {
            "accountId": "acc-1", "assetNetworkId": "an-1", "address": "TWallet1", "balance": 50,
            "observedAt": "2026-09-11T12:00:00Z", "blockReference": None, "source": "trongrid",
            "stale": False, "nextRefreshAllowedAt": "2026-09-11T12:00:30Z", "refreshSuppressed": False,
            "refreshFailureReason": None,
        }
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = WalletBalanceResource(fake)

    result = resource.refresh_balance("acc-1", "env-1", "an-1")

    assert fake.received[0].method == "POST"
    assert fake.received[0].path == "/v1/accounts/acc-1/wallet-balances/refresh?environmentId=env-1&assetNetworkId=an-1"
    assert fake.received[0].body is None
    assert result.source == "trongrid"


def test_get_asset_balances_aggregates_across_networks_grouped_by_asset() -> None:
    body = json.dumps(
        [
            {
                "assetId": "usdt", "assetSymbol": "USDT", "aggregateBalance": 150,
                "networkBalances": [
                    {"assetNetworkId": "an-tron", "networkCode": "tron", "balance": 100, "observedAt": None, "stale": False},
                    {"assetNetworkId": "an-eth", "networkCode": "ethereum", "balance": 50, "observedAt": None, "stale": False},
                ],
            }
        ]
    )
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(200, body))
    resource = WalletBalanceResource(fake)

    results = resource.get_asset_balances("acc-1", "env-1", ["an-tron", "an-eth"])

    assert len(results) == 1
    assert results[0].asset_symbol == "USDT"
    assert results[0].aggregate_balance == Decimal("150")
    assert len(results[0].network_balances) == 2
    assert results[0].network_balances[0].network_code == "tron"
    assert fake.received[0].path == "/v1/accounts/acc-1/wallet-balances/aggregate?environmentId=env-1&assetNetworkIds=an-tron%2Can-eth"
