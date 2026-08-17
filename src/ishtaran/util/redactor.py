"""
Mascaramento central de segredos para log/repr/mensagens de erro -- nunca o valor bruto. Formato
generico (4 primeiros + **** + 4 ultimos): a API Key real do Ishtaran nao tem prefixo de ambiente
(Base64 puro de 32 bytes -- ver SDK_CAPABILITY_SPEC.md secao 12.5), entao este SDK nunca assume um
prefixo tipo sk_live_ que nao existe de verdade.
"""

from __future__ import annotations

_SENSITIVE_HEADERS = {"authorization", "x-api-key"}


def mask(secret: str | None) -> str:
    if secret is None:
        return "None"
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}****{secret[-4:]}"


def is_sensitive_header(header_name: str) -> bool:
    return header_name.lower() in _SENSITIVE_HEADERS
