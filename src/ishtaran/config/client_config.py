"""
Fabrica unica de configuracao -- fonte de verdade de defaults (base_url/api_key/timeout/
environment/user_agent/retry_policy), nunca dispersa entre resources individuais.
"""

from __future__ import annotations

from dataclasses import dataclass

from .endpoints import resolve_base_url
from .environment import Environment
from .retry_policy import RetryPolicy, default_retry_policy
from ..util.redactor import mask
from ..util.user_agent import DEFAULT_USER_AGENT


@dataclass(frozen=True)
class IshtaranClientConfig:
    base_url: str
    environment: Environment
    api_key: str | None
    connect_timeout_seconds: float
    request_timeout_seconds: float
    retry_policy: RetryPolicy
    user_agent: str
    logging_enabled: bool
    allow_insecure_tls_for_local_development: bool

    def __repr__(self) -> str:
        return (
            f"IshtaranClientConfig(base_url={self.base_url!r}, environment={self.environment!r}, "
            f"api_key={mask(self.api_key)!r}, connect_timeout_seconds={self.connect_timeout_seconds}, "
            f"request_timeout_seconds={self.request_timeout_seconds}, user_agent={self.user_agent!r})"
        )


def build_client_config(
    *,
    api_key: str | None = None,
    environment: Environment = Environment.LOCAL,
    base_url: str | None = None,
    connect_timeout_seconds: float = 5.0,
    request_timeout_seconds: float = 30.0,
    retry_policy: RetryPolicy | None = None,
    user_agent: str | None = None,
    enable_logging: bool = False,
    allow_insecure_tls_for_local_development: bool = False,
) -> IshtaranClientConfig:
    resolved_base_url = resolve_base_url(environment, base_url)

    if allow_insecure_tls_for_local_development and environment != Environment.LOCAL:
        raise ValueError(
            "allow_insecure_tls_for_local_development so pode ser usado com Environment.LOCAL -- "
            "nunca contra Sandbox/Production."
        )

    return IshtaranClientConfig(
        base_url=resolved_base_url,
        environment=environment,
        api_key=api_key,
        connect_timeout_seconds=connect_timeout_seconds,
        request_timeout_seconds=request_timeout_seconds,
        retry_policy=retry_policy or default_retry_policy(),
        user_agent=user_agent or DEFAULT_USER_AGENT,
        logging_enabled=enable_logging,
        allow_insecure_tls_for_local_development=allow_insecure_tls_for_local_development,
    )
