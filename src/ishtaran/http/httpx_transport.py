"""
Unica implementacao real de HttpTransport -- sobre httpx (unica dependencia de producao alem de
lossless-json-equivalente-nativo do stdlib -- ver util/json_util.py). TLS verificado por padrao;
nunca desabilitado por este SDK. Redirects NUNCA seguidos automaticamente (paridade com Java
Redirect.NEVER e com a correcao de seguranca aplicada no SDK TypeScript, ver SECURITY_REVIEW.md).
"""

from __future__ import annotations

import httpx

from .types import HttpTransport, IshtaranHttpRequest, IshtaranHttpResponse
from ..config.client_config import IshtaranClientConfig
from ..error.errors import NetworkError, TimeoutError


class HttpxTransport(HttpTransport):
    def __init__(self, config: IshtaranClientConfig, transport: httpx.BaseTransport | None = None) -> None:
        """
        `transport` e um hook so para teste (injeta httpx.MockTransport para exercitar a politica
        de redirect real sem rede) -- producao nunca passa esse argumento.
        """
        self._base_url = config.base_url
        self._user_agent = config.user_agent
        self._client = httpx.Client(
            timeout=httpx.Timeout(connect=config.connect_timeout_seconds, read=config.request_timeout_seconds,
                                   write=config.request_timeout_seconds, pool=config.request_timeout_seconds),
            follow_redirects=False,
            transport=transport,
        )

    def send(self, request: IshtaranHttpRequest) -> IshtaranHttpResponse:
        headers = {"User-Agent": self._user_agent, "Accept": "application/json", **request.headers}
        if request.body is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = self._client.request(
                request.method, f"{self._base_url}{request.path}", headers=headers, content=request.body,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Timeout ao chamar {request.method} {request.path}", exc) from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Falha de rede ao chamar {request.method} {request.path}", exc) from exc

        if 300 <= response.status_code < 400:
            raise NetworkError(
                f"Redirect ({response.status_code}) recebido ao chamar {request.method} {request.path} -- "
                "este SDK nunca segue redirects automaticamente (mesma politica do SDK Java/TypeScript)."
            )

        return IshtaranHttpResponse(status=response.status_code, headers=dict(response.headers), body=response.text)

    def close(self) -> None:
        self._client.close()
