from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import TransferStatus
from ..util.json_util import field, money, string_field, string_field_or_none


@dataclass(frozen=True)
class TransferResponse:
    """PROMPT 7 (SPEC-TRANSFER-001) -- first-class Transfer: Account/Wallet -> asset -> another
    internal Account or an arbitrary external address, never a Payment/PaymentIntent/Settlement in
    disguise. Platform Fee (platform_fee_amount) is always ON_TOP -- amount is exactly what the
    recipient receives, the fee is charged separately from the sender."""

    transfer_id: str
    organization_id: str
    application_id: str
    environment_id: str
    source_account_id: str
    asset_network_id: str
    amount: Decimal
    destination_address: str
    destination_account_id: str | None
    platform_fee_amount: Decimal
    platform_fee_percentage: Decimal
    status: EnumValue[int]
    # BR-TRF-008 -- the real SigningRequest (ExecutionCustody). Use it with
    # signing_requests.get(...) to fetch the Legs/canonical_hash to sign locally, then
    # signing_requests.submit_signed_transaction(...) per Leg. None only if the Transfer failed
    # before a SigningRequest could be created.
    signing_request_id: str | None
    created_at: str
    confirmed_at: str | None
    failure_reason: str | None


def map_transfer_response(raw: Any) -> TransferResponse:
    return TransferResponse(
        transfer_id=string_field(raw, "transferId"),
        organization_id=string_field(raw, "organizationId"),
        application_id=string_field(raw, "applicationId"),
        environment_id=string_field(raw, "environmentId"),
        source_account_id=string_field(raw, "sourceAccountId"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        amount=money(field(raw, "amount")),
        destination_address=string_field(raw, "destinationAddress"),
        destination_account_id=string_field_or_none(raw, "destinationAccountId"),
        platform_fee_amount=money(field(raw, "platformFeeAmount")),
        platform_fee_percentage=money(field(raw, "platformFeePercentage")),
        status=TransferStatus.from_raw(int(field(raw, "status"))),
        signing_request_id=string_field_or_none(raw, "signingRequestId"),
        created_at=string_field(raw, "createdAt"),
        confirmed_at=string_field_or_none(raw, "confirmedAt"),
        failure_reason=string_field_or_none(raw, "failureReason"),
    )
