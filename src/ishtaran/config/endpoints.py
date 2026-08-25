"""
Centralized base URLs -- never URL strings scattered across the SDK. LOCAL_BASE_URL and
SANDBOX_BASE_URL are real known defaults today. SANDBOX_BASE_URL points at the canonical
sandbox-api.ishtaran.com domain (Cloud Run Domain Mapping, live since 2026-08-25 -- the raw Cloud
Run URL from the 2026-08-24 deploy still works but is no longer advertised). Production does not
have real infrastructure provisioned yet (terraform apply has never run against it): resolving it
without an explicit base_url is a configuration error, never a silent fallback.
"""

from __future__ import annotations

from .environment import Environment

LOCAL_BASE_URL = "http://localhost:8080"
SANDBOX_BASE_URL = "https://sandbox-api.ishtaran.com"


def resolve_base_url(environment: Environment, explicit_base_url: str | None) -> str:
    if explicit_base_url:
        return explicit_base_url
    if environment == Environment.LOCAL:
        return LOCAL_BASE_URL
    if environment == Environment.SANDBOX:
        return SANDBOX_BASE_URL
    raise ValueError(
        f"An explicit base_url is required for Environment.{environment.name} -- no real "
        "Production URL has been provisioned yet (see SDK_CAPABILITY_SPEC.md section 2). "
        "Configure IshtaranClientConfig.base_url explicitly."
    )
