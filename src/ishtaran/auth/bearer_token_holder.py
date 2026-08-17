"""Guarda o access token de Member (apos auth.login(...)) -- mutavel dentro de uma instancia de IshtaranClient."""

from __future__ import annotations


class BearerTokenHolder:
    def __init__(self) -> None:
        self._token: str | None = None

    def set(self, token: str) -> None:
        self._token = token

    def current(self) -> str | None:
        return self._token

    def clear(self) -> None:
        self._token = None
