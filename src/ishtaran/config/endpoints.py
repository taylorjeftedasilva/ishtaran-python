"""
Centralized base URLs -- never URL strings scattered across the SDK. LOCAL_BASE_URL is the only
known real default today (local docker-compose). Sandbox/Production do not have real DNS
provisioned yet (terraform apply has never run -- see SDK_CAPABILITY_SPEC.md section 2): resolving
either of these without an explicit base_url is a configuration error, never a silent fallback.
"""

from __future__ import annotations

from .environment import Environment

LOCAL_BASE_URL = "http://localhost:8080"


def resolve_base_url(environment: Environment, explicit_base_url: str | None) -> str:
    if explicit_base_url:
        return explicit_base_url
    if environment == Environment.LOCAL:
        return LOCAL_BASE_URL
    raise ValueError(
        f"An explicit base_url is required for Environment.{environment.name} -- no real "
        "Sandbox/Production URL has been provisioned yet (see SDK_CAPABILITY_SPEC.md section 2). "
        "Configure IshtaranClientConfig.base_url explicitly."
    )
