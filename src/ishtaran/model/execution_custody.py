from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import DerivationScheme, NetworkCostPayer, NetworkResourceSource
from ..util.json_util import array_field, field, money, money_or_none, safe_int, string_field, string_field_or_none


@dataclass(frozen=True)
class RegisterWalletResult:
    wallet_id: str


def map_register_wallet_result(raw: Any) -> RegisterWalletResult:
    return RegisterWalletResult(wallet_id=string_field(raw, "walletId"))


@dataclass(frozen=True)
class WalletResponse:
    """BR-WLT-002 -- never includes the derivation material (dedicated route, `WalletPublicMaterialResult`)."""

    wallet_id: str
    application_id: str
    network_id: str
    scheme: EnumValue[int]
    next_derivation_index: int
    registered_at: str


def map_wallet_response(raw: Any) -> WalletResponse:
    return WalletResponse(
        wallet_id=string_field(raw, "walletId"),
        application_id=string_field(raw, "applicationId"),
        network_id=string_field(raw, "networkId"),
        scheme=DerivationScheme.from_raw(safe_int(field(raw, "scheme"))),
        next_derivation_index=safe_int(field(raw, "nextDerivationIndex")),
        registered_at=string_field(raw, "registeredAt"),
    )


@dataclass(frozen=True)
class WalletPublicMaterialResult:
    """BR-WLT-002 -- the only legitimate point of exposure for the derivation material (Confidential, never Secret)."""

    public_derivation_material: str


def map_wallet_public_material_result(raw: Any) -> WalletPublicMaterialResult:
    return WalletPublicMaterialResult(public_derivation_material=string_field(raw, "publicDerivationMaterial"))


@dataclass(frozen=True)
class AllocatedDepositAddressResult:
    """BR-WLT-001 -- `derivation_reference` is never reused across calls."""

    wallet_id: str
    address: str
    derivation_reference: int


def map_allocated_deposit_address_result(raw: Any) -> AllocatedDepositAddressResult:
    return AllocatedDepositAddressResult(
        wallet_id=string_field(raw, "walletId"),
        address=string_field(raw, "address"),
        derivation_reference=safe_int(field(raw, "derivationReference")),
    )


@dataclass(frozen=True)
class RegisterExecutionDestinationResult:
    """
    DEC-037, CUSTODY-EXECUTION-MODES.md -- a beneficiary's valid on-chain receiving address for a
    given AssetNetwork, consumed by SelfCustodySettlementExecutionStrategy when building an
    execution leg. Deliberately NOT a withdrawal destination -- no whitelist/cooldown policy,
    first-registration-wins (a second registration for the same account_id+asset_network_id is
    rejected, never silently overwritten).
    """

    execution_destination_id: str


def map_register_execution_destination_result(raw: Any) -> RegisterExecutionDestinationResult:
    return RegisterExecutionDestinationResult(execution_destination_id=string_field(raw, "executionDestinationId"))


@dataclass(frozen=True)
class ExecutionLegInput:
    """A leg already computed by the caller (Settlement/Withdrawal, DEC-025) -- never recomputed by the SDK."""

    role: str
    destination_address: str
    amount: Decimal


@dataclass(frozen=True)
class CreateSigningRequestResult:
    signing_request_id: str


def map_create_signing_request_result(raw: Any) -> CreateSigningRequestResult:
    return CreateSigningRequestResult(signing_request_id=string_field(raw, "signingRequestId"))


@dataclass(frozen=True)
class ExecutionLegResponse:
    """
    `status`/`mismatch_reason`/`broadcast_reference` are raw strings in the real JSON (Group A) --
    the possible values (PendingSignature/Verified/MismatchDetected/Broadcast/...) do not yet have
    a closed catalog documented outside the backend's source code.
    """

    execution_leg_id: str
    role: str
    destination_address: str
    amount: Decimal
    canonical_hash: str
    status: str
    mismatch_reason: str | None
    broadcast_reference: str | None


def map_execution_leg_response(raw: Any) -> ExecutionLegResponse:
    return ExecutionLegResponse(
        execution_leg_id=string_field(raw, "executionLegId"),
        role=string_field(raw, "role"),
        destination_address=string_field(raw, "destinationAddress"),
        amount=money(field(raw, "amount")),
        canonical_hash=string_field(raw, "canonicalHash"),
        status=string_field(raw, "status"),
        mismatch_reason=string_field_or_none(raw, "mismatchReason"),
        broadcast_reference=string_field_or_none(raw, "broadcastReference"),
    )


@dataclass(frozen=True)
class SigningRequestResponse:
    signing_request_id: str
    application_id: str
    environment_id: str
    network_id: str
    wallet_id: str
    derivation_reference: int
    origin_reference: str
    asset_network_id: str
    source_address: str
    protocol_version: int
    legs: list[ExecutionLegResponse]
    created_at: str
    expires_at: str
    is_expired: bool


def map_signing_request_response(raw: Any) -> SigningRequestResponse:
    return SigningRequestResponse(
        signing_request_id=string_field(raw, "signingRequestId"),
        application_id=string_field(raw, "applicationId"),
        environment_id=string_field(raw, "environmentId"),
        network_id=string_field(raw, "networkId"),
        wallet_id=string_field(raw, "walletId"),
        derivation_reference=safe_int(field(raw, "derivationReference")),
        origin_reference=string_field(raw, "originReference"),
        asset_network_id=string_field(raw, "assetNetworkId"),
        source_address=string_field(raw, "sourceAddress"),
        protocol_version=safe_int(field(raw, "protocolVersion")),
        legs=array_field(raw, "legs", map_execution_leg_response),
        created_at=string_field(raw, "createdAt"),
        expires_at=string_field(raw, "expiresAt"),
        is_expired=bool(field(raw, "isExpired")),
    )


@dataclass(frozen=True)
class SubmitSignedTransactionResult:
    """
    `verified=False` corresponds to the public code SIGNED_TRANSACTION_MISMATCH (backend SPEC-020
    Errors) -- never broadcast (INV-SC-03). `all_legs_verified=True` means the broadcast of
    ALL Legs has already been triggered in the same Command (all-signatures gate).
    """

    execution_leg_id: str
    verified: bool
    mismatch_reason: str | None
    all_legs_verified: bool


def map_submit_signed_transaction_result(raw: Any) -> SubmitSignedTransactionResult:
    return SubmitSignedTransactionResult(
        execution_leg_id=string_field(raw, "executionLegId"),
        verified=bool(field(raw, "verified")),
        mismatch_reason=string_field_or_none(raw, "mismatchReason"),
        all_legs_verified=bool(field(raw, "allLegsVerified")),
    )


@dataclass(frozen=True)
class RegisterExecutionSourceResult:
    """
    SPEC-ADDRESSPOOL-001, CUSTODY-EXECUTION-MODES.md -- the outbound-only counterpart of a Wallet
    derivation: the address ExecutionCustody signs FROM to pay network cost (Energy/Bandwidth/gas),
    never confused with an ExecutionDestination (a beneficiary's inbound address). Must be
    registered before the first self-custody Withdrawal/Payout on a given AssetNetwork -- see
    docs/specs/execution-custody/README.md "Bootstrap obrigatório" for the required order
    (Wallet -> ExecutionSource -> NetworkCostPayerAccount).
    """

    execution_source_id: str


def map_register_execution_source_result(raw: Any) -> RegisterExecutionSourceResult:
    return RegisterExecutionSourceResult(execution_source_id=string_field(raw, "executionSourceId"))


@dataclass(frozen=True)
class RegisterNetworkCostPayerAccountResult:
    """
    SPEC-NETEXEC-001 -- the Account debited for the *charged* network cost (total_charged, in
    quote_currency) once a NetworkExecutionQuote is authorized. First-registration-wins per
    (organization_id, asset_network_id), same as ExecutionDestination -- never silently
    overwritten. Must belong to the same Organization as the caller (a cross-tenant account_id is
    rejected).
    """

    network_cost_payer_account_id: str


def map_register_network_cost_payer_account_result(raw: Any) -> RegisterNetworkCostPayerAccountResult:
    return RegisterNetworkCostPayerAccountResult(network_cost_payer_account_id=string_field(raw, "networkCostPayerAccountId"))


@dataclass(frozen=True)
class NetworkExecutionOperationInput:
    """A single physical operation to be priced -- input to NetworkExecutionResource.quote(), never interpreted by the caller."""

    destination_address: str | None
    amount: Decimal
    kind: EnumValue[int]
    reference: str | None


@dataclass(frozen=True)
class NetworkExecutionTransferResponse:
    """SPEC-NETEXEC-001 Descoberta 2 -- the physical unit (what will be one real on-chain transaction), grouping 1..N transfers."""

    destination_address: str
    amount: Decimal
    source_operation_reference: str | None


def _map_network_execution_transfer_response(raw: Any) -> NetworkExecutionTransferResponse:
    return NetworkExecutionTransferResponse(
        destination_address=string_field(raw, "destinationAddress"),
        amount=money(field(raw, "amount")),
        source_operation_reference=string_field_or_none(raw, "sourceOperationReference"),
    )


@dataclass(frozen=True)
class NetworkExecutionTransactionResponse:
    transfers: list[NetworkExecutionTransferResponse]


def _map_network_execution_transaction_response(raw: Any) -> NetworkExecutionTransactionResponse:
    return NetworkExecutionTransactionResponse(transfers=array_field(raw, "transfers", _map_network_execution_transfer_response))


@dataclass(frozen=True)
class NetworkExecutionPlanResponse:
    """SPEC-NETEXEC-001 BL-NET-002 -- structured result of INetworkExecutionPlanner.Plan(...), never flattened into loose fields."""

    asset_network_id: str
    transactions: list[NetworkExecutionTransactionResponse]


def _map_network_execution_plan_response(raw: Any) -> NetworkExecutionPlanResponse:
    return NetworkExecutionPlanResponse(
        asset_network_id=string_field(raw, "assetNetworkId"),
        transactions=array_field(raw, "transactions", _map_network_execution_transaction_response),
    )


@dataclass(frozen=True)
class NetworkResourceLineResponse:
    """SPEC-NETEXEC-001 Descoberta 6/BR-NET-008 -- resource_code is opaque (string), never interpreted by the generic caller."""

    resource_code: str
    quantity: Decimal
    unit: str | None


def _map_network_resource_line_response(raw: Any) -> NetworkResourceLineResponse:
    return NetworkResourceLineResponse(
        resource_code=string_field(raw, "resourceCode"),
        quantity=money(field(raw, "quantity")),
        unit=string_field_or_none(raw, "unit"),
    )


@dataclass(frozen=True)
class NetworkResourceEstimateResponse:
    lines: list[NetworkResourceLineResponse]


def _map_network_resource_estimate_response(raw: Any) -> NetworkResourceEstimateResponse:
    return NetworkResourceEstimateResponse(lines=array_field(raw, "lines", _map_network_resource_line_response))


@dataclass(frozen=True)
class NetworkExecutionQuoteResponse:
    """
    SPEC-NETEXEC-001 (brief section 13) -- mirror of
    ExecutionCustody.Domain.ValueObjects.NetworkExecutionQuote. native_execution_cost/
    authorized_native_cost are always in the RESOURCE asset's native units
    (resource_asset_network_id or asset_network_id); total_charged is always in quote_currency
    (the CHARGED asset) -- total_charged = (native_execution_cost * fx) + safety_buffer +
    replenishment_requirement + conversion_overhead. authorized_native_cost is the number
    actually reserved for execution (>= the sum of every physical operation's cost, INC-18) --
    never compare a caller-supplied estimate directly against native_execution_cost alone.
    """

    network: str | None
    plan: NetworkExecutionPlanResponse
    estimated_resources: NetworkResourceEstimateResponse
    native_execution_cost: Decimal
    resource_asset_network_id: str | None
    quote_currency: str | None
    fx: Decimal
    safety_buffer: Decimal
    resource_source: EnumValue[int]
    replenishment_requirement: Decimal | None
    conversion_overhead: Decimal
    expires_at: str
    total_charged: Decimal
    network_cost_payer: EnumValue[int]
    authorized_native_cost: Decimal


def map_network_execution_quote_response(raw: Any) -> NetworkExecutionQuoteResponse:
    return NetworkExecutionQuoteResponse(
        network=string_field_or_none(raw, "network"),
        plan=_map_network_execution_plan_response(field(raw, "plan")),
        estimated_resources=_map_network_resource_estimate_response(field(raw, "estimatedResources")),
        native_execution_cost=money(field(raw, "nativeExecutionCost")),
        resource_asset_network_id=string_field_or_none(raw, "resourceAssetNetworkId"),
        quote_currency=string_field_or_none(raw, "quoteCurrency"),
        fx=money(field(raw, "fx")),
        safety_buffer=money(field(raw, "safetyBuffer")),
        resource_source=NetworkResourceSource.from_raw(safe_int(field(raw, "resourceSource"))),
        replenishment_requirement=money_or_none(field(raw, "replenishmentRequirement")),
        conversion_overhead=money(field(raw, "conversionOverhead")),
        expires_at=string_field(raw, "expiresAt"),
        total_charged=money(field(raw, "totalCharged")),
        network_cost_payer=NetworkCostPayer.from_raw(safe_int(field(raw, "networkCostPayer"))),
        authorized_native_cost=money(field(raw, "authorizedNativeCost")),
    )
