from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .enum_factory import EnumValue
from .enums import DerivationScheme
from ..util.json_util import array_field, field, money, safe_int, string_field, string_field_or_none


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
