from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ..util.json_util import field, money_or_none, safe_int, string_field, string_field_or_none


@dataclass(frozen=True)
class TokenResult:
    success: bool
    access_token: str | None
    refresh_token: str | None
    expires_at: str | None
    error_code: str | None


def map_token_result(raw: Any) -> TokenResult:
    return TokenResult(
        success=bool(field(raw, "success")),
        access_token=string_field_or_none(raw, "accessToken"),
        refresh_token=string_field_or_none(raw, "refreshToken"),
        expires_at=string_field_or_none(raw, "expiresAt"),
        error_code=string_field_or_none(raw, "errorCode"),
    )


@dataclass(frozen=True)
class SignUpResponse:
    organization_id: str
    member_id: str
    token: TokenResult
    application_id: str
    environment_id: str
    api_key_plain_text: str | None


def map_sign_up_response(raw: Any) -> SignUpResponse:
    return SignUpResponse(
        organization_id=string_field(raw, "organizationId"),
        member_id=string_field(raw, "memberId"),
        token=map_token_result(field(raw, "token")),
        application_id=string_field(raw, "applicationId"),
        environment_id=string_field(raw, "environmentId"),
        api_key_plain_text=string_field_or_none(raw, "apiKeyPlainText"),
    )


@dataclass(frozen=True)
class MemberResponse:
    member_id: str
    organization_id: str
    email: str | None
    role: str | None
    status: str | None
    created_at: str
    activated_at: str | None
    last_login_at: str | None


def map_member_response(raw: Any) -> MemberResponse:
    return MemberResponse(
        member_id=string_field(raw, "memberId"),
        organization_id=string_field(raw, "organizationId"),
        email=string_field_or_none(raw, "email"),
        role=string_field_or_none(raw, "role"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
        activated_at=string_field_or_none(raw, "activatedAt"),
        last_login_at=string_field_or_none(raw, "lastLoginAt"),
    )


@dataclass(frozen=True)
class InviteMemberResult:
    member_id: str
    plain_text_invite_token: str | None


def map_invite_member_result(raw: Any) -> InviteMemberResult:
    return InviteMemberResult(
        member_id=string_field(raw, "memberId"),
        plain_text_invite_token=string_field_or_none(raw, "plainTextInviteToken"),
    )


@dataclass(frozen=True)
class CreatedResourceResponse:
    id: str


def map_created_resource_response(raw: Any) -> CreatedResourceResponse:
    return CreatedResourceResponse(id=string_field(raw, "id"))


@dataclass(frozen=True)
class OrganizationResponse:
    organization_id: str
    name: str | None
    status: str | None
    created_at: str


def map_organization_response(raw: Any) -> OrganizationResponse:
    return OrganizationResponse(
        organization_id=string_field(raw, "organizationId"),
        name=string_field_or_none(raw, "name"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class ApplicationResponse:
    application_id: str
    organization_id: str
    name: str | None
    status: str | None


def map_application_response(raw: Any) -> ApplicationResponse:
    return ApplicationResponse(
        application_id=string_field(raw, "applicationId"),
        organization_id=string_field(raw, "organizationId"),
        name=string_field_or_none(raw, "name"),
        status=string_field_or_none(raw, "status"),
    )


@dataclass(frozen=True)
class ApiKeyMetadataResponse:
    api_key_id: str
    created_at: str
    last_used_at: str | None


def map_api_key_metadata_response(raw: Any) -> ApiKeyMetadataResponse:
    return ApiKeyMetadataResponse(
        api_key_id=string_field(raw, "apiKeyId"),
        created_at=string_field(raw, "createdAt"),
        last_used_at=string_field_or_none(raw, "lastUsedAt"),
    )


@dataclass(frozen=True)
class GenerateApiKeyResult:
    api_key_id: str
    plain_text_key: str | None


def map_generate_api_key_result(raw: Any) -> GenerateApiKeyResult:
    return GenerateApiKeyResult(
        api_key_id=string_field(raw, "apiKeyId"),
        plain_text_key=string_field_or_none(raw, "plainTextKey"),
    )


@dataclass(frozen=True)
class RotateApiKeyResult:
    new_api_key_id: str
    plain_text_key: str | None


def map_rotate_api_key_result(raw: Any) -> RotateApiKeyResult:
    return RotateApiKeyResult(
        new_api_key_id=string_field(raw, "newApiKeyId"),
        plain_text_key=string_field_or_none(raw, "plainTextKey"),
    )


@dataclass(frozen=True)
class AssetResponse:
    asset_id: str
    symbol: str | None
    name: str | None
    decimals: int
    kind: str | None
    status: str | None
    created_at: str


def map_asset_response(raw: Any) -> AssetResponse:
    return AssetResponse(
        asset_id=string_field(raw, "assetId"),
        symbol=string_field_or_none(raw, "symbol"),
        name=string_field_or_none(raw, "name"),
        decimals=safe_int(field(raw, "decimals")),
        kind=string_field_or_none(raw, "kind"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class NetworkResponse:
    network_id: str
    code: str | None
    name: str | None
    chain_id: int | None
    is_testnet: bool
    status: str | None
    created_at: str


def map_network_response(raw: Any) -> NetworkResponse:
    chain_id_raw = field(raw, "chainId")
    return NetworkResponse(
        network_id=string_field(raw, "networkId"),
        code=string_field_or_none(raw, "code"),
        name=string_field_or_none(raw, "name"),
        chain_id=None if chain_id_raw is None else safe_int(chain_id_raw),
        is_testnet=bool(field(raw, "isTestnet")),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class AssetNetworkResponse:
    asset_network_id: str
    asset_id: str
    network_id: str
    min_confirmations: int
    min_amount: Decimal | None
    max_amount: Decimal | None
    estimated_fee: Decimal | None
    contract_address: str | None
    status: str | None
    created_at: str


def map_asset_network_response(raw: Any) -> AssetNetworkResponse:
    return AssetNetworkResponse(
        asset_network_id=string_field(raw, "assetNetworkId"),
        asset_id=string_field(raw, "assetId"),
        network_id=string_field(raw, "networkId"),
        min_confirmations=safe_int(field(raw, "minConfirmations")),
        min_amount=money_or_none(field(raw, "minAmount")),
        max_amount=money_or_none(field(raw, "maxAmount")),
        estimated_fee=money_or_none(field(raw, "estimatedFee")),
        contract_address=string_field_or_none(raw, "contractAddress"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
    )
