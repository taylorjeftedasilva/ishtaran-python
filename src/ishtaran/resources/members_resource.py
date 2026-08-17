from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, delete_request, get_request, post_request
from ..model.control_plane import (
    InviteMemberResult,
    MemberResponse,
    TokenResult,
    map_invite_member_result,
    map_member_response,
    map_token_result,
)
from ..model.enum_factory import EnumValue


class MembersResource(ResourceSupport):
    """Control Plane -- Members (7 rotas reais, IdentityAccess)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def invite(self, organization_id: str, email: str, role: EnumValue[int]) -> InviteMemberResult:
        body = self._to_json({"email": email, "role": role.raw_value})
        return self._execute(post_request(f"/v1/organizations/{organization_id}/members", body, False), map_invite_member_result)

    def accept_invite(self, invite_token: str, password: str) -> TokenResult:
        """Devolve o token real de acesso -- mesmo mecanismo de auth.login() preenche a sessao do client."""
        body = self._to_json({"inviteToken": invite_token, "password": password})
        return self._execute(post_request("/v1/members/accept-invite", body, False), map_token_result)

    def list(self, organization_id: str) -> list[MemberResponse]:
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/members"), map_member_response)

    def assign_role(self, member_id: str, new_role: EnumValue[int]) -> None:
        body = self._to_json({"newRole": new_role.raw_value})
        self._execute_no_content(post_request(f"/v1/members/{member_id}/role", body, False))

    def suspend(self, member_id: str, reason: str | None = None) -> None:
        body = self._to_json({"reason": reason or ""})
        self._execute_no_content(post_request(f"/v1/members/{member_id}/suspend", body, False))

    def reactivate(self, member_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/members/{member_id}/reactivate", None, False))

    def remove(self, member_id: str) -> None:
        self._execute_no_content(delete_request(f"/v1/members/{member_id}"))
