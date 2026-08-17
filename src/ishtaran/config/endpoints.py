"""
Base URLs centralizadas -- nunca strings de URL espalhadas pelo SDK. LOCAL_BASE_URL e o unico
default real conhecido hoje (docker-compose local). Sandbox/Production nao tem DNS real
provisionado ainda (terraform apply nunca rodou -- ver SDK_CAPABILITY_SPEC.md secao 2): resolver
essas duas sem base_url explicito e um erro de configuracao, nunca um fallback silencioso.
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
        f"base_url explicito e obrigatorio para Environment.{environment.name} -- nenhuma URL "
        "real de Sandbox/Production foi provisionada ainda (ver SDK_CAPABILITY_SPEC.md secao 2). "
        "Configure IshtaranClientConfig.base_url explicitamente."
    )
