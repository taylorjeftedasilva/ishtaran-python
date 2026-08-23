from __future__ import annotations

from .resource_support import ResourceSupport
from ..auth.bearer_token_holder import BearerTokenHolder
from ..http.types import HttpTransport, get_request, post_request
from ..model.account_holders import (
    AccountHolderResponse,
    AccountHolderTokenResult,
    ClaimAccountHolderInvitationResult,
    SignUpAndClaimAccountHolderInvitationResult,
    map_account_holder_response,
    map_account_holder_token_result,
    map_claim_account_holder_invitation_result,
    map_sign_up_and_claim_account_holder_invitation_result,
)


class AccountHoldersResource(ResourceSupport):
    """DEC-032 -- self-service, global AccountHolder identity (/v1/account-holders/*),
    authenticated by AccountHolderJwtScheme -- its own key/token, never shared with the
    BearerTokenHolder of AuthResource (Member) or with the Organization's API Key. Built on its
    own transport (see client.py) precisely so the two tokens never mix within
    the same client instance."""

    def __init__(self, transport: HttpTransport, account_holder_token_holder: BearerTokenHolder) -> None:
        super().__init__(transport)
        self._account_holder_token_holder = account_holder_token_holder

    def sign_up(self, email: str, password: str) -> AccountHolderTokenResult:
        body = self._to_json({"email": email, "password": password})
        result = self._execute(post_request("/v1/account-holders/signup", body, False), map_account_holder_token_result)
        if result.success and result.access_token:
            self._account_holder_token_holder.set(result.access_token)
        return result

    def login(self, email: str, password: str) -> AccountHolderTokenResult:
        body = self._to_json({"email": email, "password": password})
        result = self._execute(post_request("/v1/account-holders/login", body, False), map_account_holder_token_result)
        if result.success and result.access_token:
            self._account_holder_token_holder.set(result.access_token)
        return result

    def me(self) -> AccountHolderResponse:
        """Requires an active AccountHolder session (sign_up/login already called on this client instance, or set_access_token)."""
        return self._execute(get_request("/v1/account-holders/me"), map_account_holder_response)

    def claim_invitation(self, plain_text_token: str) -> ClaimAccountHolderInvitationResult:
        """Requires an active AccountHolder session -- claims an invitation from a NEW Organization
        for the already-authenticated identity (BR-HLD-006, reuses the existing Account, never duplicates it)."""
        body = self._to_json({"plainTextToken": plain_text_token})
        return self._execute(post_request("/v1/account-holders/invitations/claim", body, False), map_claim_account_holder_invitation_result)

    def sign_up_and_claim_invitation(self, plain_text_token: str, email: str, password: str) -> SignUpAndClaimAccountHolderInvitationResult:
        """No prior authentication -- creates the identity and claims the invitation atomically (holder never seen before)."""
        body = self._to_json({"plainTextToken": plain_text_token, "email": email, "password": password})
        result = self._execute(
            post_request("/v1/account-holders/invitations/signup-and-claim", body, False),
            map_sign_up_and_claim_account_holder_invitation_result,
        )
        if result.success and result.token and result.token.access_token:
            self._account_holder_token_holder.set(result.token.access_token)
        return result

    def set_access_token(self, access_token: str) -> None:
        """Fills the session manually (e.g. a token obtained in a previous process)."""
        self._account_holder_token_holder.set(access_token)

    def logout(self) -> None:
        """No HTTP call -- clears the local AccountHolder session (never affects the Member session/Organization API Key)."""
        self._account_holder_token_holder.clear()
