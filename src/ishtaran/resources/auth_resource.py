from __future__ import annotations

from .resource_support import ResourceSupport
from ..auth.bearer_token_holder import BearerTokenHolder
from ..http.types import HttpTransport, post_request
from ..model.control_plane import SignUpResponse, TokenResult, map_sign_up_response, map_token_result


class AuthResource(ResourceSupport):
    """Control Plane -- /v1/auth/* (5 rotas reais). login() preenche o BearerTokenHolder do client."""

    def __init__(self, transport: HttpTransport, bearer_token_holder: BearerTokenHolder) -> None:
        super().__init__(transport)
        self._bearer_token_holder = bearer_token_holder

    def login(self, email: str, password: str) -> TokenResult:
        body = self._to_json({"email": email, "password": password})
        result = self._execute(post_request("/v1/auth/login", body, False), map_token_result)
        if result.success and result.access_token:
            self._bearer_token_holder.set(result.access_token)
        return result

    def sign_up(self, organization_name: str, email: str, password: str) -> SignUpResponse:
        body = self._to_json({"organizationName": organization_name, "email": email, "password": password})
        result = self._execute(post_request("/v1/auth/signup", body, False), map_sign_up_response)
        if result.token.success and result.token.access_token:
            self._bearer_token_holder.set(result.token.access_token)
        return result

    def refresh(self, refresh_token: str) -> TokenResult:
        body = self._to_json({"refreshToken": refresh_token})
        result = self._execute(post_request("/v1/auth/refresh", body, False), map_token_result)
        if result.success and result.access_token:
            self._bearer_token_holder.set(result.access_token)
        return result

    def request_password_reset(self, email: str) -> None:
        self._execute_no_content(post_request("/v1/auth/password-reset/request", self._to_json({"email": email}), False))

    def confirm_password_reset(self, reset_token: str, new_password: str) -> None:
        body = self._to_json({"resetToken": reset_token, "newPassword": new_password})
        self._execute_no_content(post_request("/v1/auth/password-reset/confirm", body, False))

    def logout(self) -> None:
        """Sem chamada HTTP -- permite limpar a sessao local do client."""
        self._bearer_token_holder.clear()
