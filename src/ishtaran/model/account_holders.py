"""DEC-032 -- AccountHolder (global financial identity), Relationship (explicit link between
Organization<->AccountHolder/Account, never ownership) and AccountHolderInvitation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..util.json_util import bool_field, field, string_field, string_field_or_none


@dataclass(frozen=True)
class OrganizationAccountResponse:
    """This Organization's link to an Account -- returned by accounts.list(). authorized_application_ids
    is scoped to THIS Relationship, never leaking into another Organization related to the same AccountHolder."""

    relationship_id: str
    account_id: str
    account_holder_id: str
    external_id: str | None
    relationship_status: str | None
    account_status: str | None
    created_at: str
    authorized_application_ids: list[str]


def map_organization_account_response(raw: Any) -> OrganizationAccountResponse:
    ids = field(raw, "authorizedApplicationIds")
    return OrganizationAccountResponse(
        relationship_id=string_field(raw, "relationshipId"),
        account_id=string_field(raw, "accountId"),
        account_holder_id=string_field(raw, "accountHolderId"),
        external_id=string_field_or_none(raw, "externalId"),
        relationship_status=string_field_or_none(raw, "relationshipStatus"),
        account_status=string_field_or_none(raw, "accountStatus"),
        created_at=string_field(raw, "createdAt"),
        authorized_application_ids=[] if ids is None else [str(x) for x in ids],
    )


@dataclass(frozen=True)
class CreateAccountHolderInvitationResult:
    invitation_id: str
    """Plain text -- exists only in this response, exactly once. Never persisted/logged by the SDK."""
    plain_text_token: str
    expires_at: str


def map_create_account_holder_invitation_result(raw: Any) -> CreateAccountHolderInvitationResult:
    return CreateAccountHolderInvitationResult(
        invitation_id=string_field(raw, "invitationId"),
        plain_text_token=string_field(raw, "plainTextToken"),
        expires_at=string_field(raw, "expiresAt"),
    )


@dataclass(frozen=True)
class AccountHolderTokenResult:
    """Result of accountHolders.sign_up()/.login(). Its own type (never TokenResult from
    model/control_plane.py): the AccountHolder has no Refresh Token in this version (MVP, scope
    deliberately reduced by the backend) and never carries organizationId/Role."""

    success: bool
    access_token: str | None
    expires_at: str | None
    error_code: str | None


def map_account_holder_token_result(raw: Any) -> AccountHolderTokenResult:
    return AccountHolderTokenResult(
        success=bool_field(raw, "success"),
        access_token=string_field_or_none(raw, "accessToken"),
        expires_at=string_field_or_none(raw, "expiresAt"),
        error_code=string_field_or_none(raw, "errorCode"),
    )


@dataclass(frozen=True)
class AccountHolderResponse:
    account_holder_id: str
    account_id: str
    email: str | None
    has_credentials: bool
    status: str | None
    created_at: str
    last_login_at: str | None


def map_account_holder_response(raw: Any) -> AccountHolderResponse:
    return AccountHolderResponse(
        account_holder_id=string_field(raw, "accountHolderId"),
        account_id=string_field(raw, "accountId"),
        email=string_field_or_none(raw, "email"),
        has_credentials=bool_field(raw, "hasCredentials"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
        last_login_at=string_field_or_none(raw, "lastLoginAt"),
    )


@dataclass(frozen=True)
class ClaimAccountHolderInvitationResult:
    success: bool
    relationship_id: str | None
    error_code: str | None


def map_claim_account_holder_invitation_result(raw: Any) -> ClaimAccountHolderInvitationResult:
    return ClaimAccountHolderInvitationResult(
        success=bool_field(raw, "success"),
        relationship_id=string_field_or_none(raw, "relationshipId"),
        error_code=string_field_or_none(raw, "errorCode"),
    )


@dataclass(frozen=True)
class SignUpAndClaimAccountHolderInvitationResult:
    success: bool
    relationship_id: str | None
    token: AccountHolderTokenResult | None
    error_code: str | None


def map_sign_up_and_claim_account_holder_invitation_result(raw: Any) -> SignUpAndClaimAccountHolderInvitationResult:
    token_raw = field(raw, "token")
    return SignUpAndClaimAccountHolderInvitationResult(
        success=bool_field(raw, "success"),
        relationship_id=string_field_or_none(raw, "relationshipId"),
        token=None if token_raw is None else map_account_holder_token_result(token_raw),
        error_code=string_field_or_none(raw, "errorCode"),
    )
