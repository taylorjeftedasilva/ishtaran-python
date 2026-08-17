"""
Base de toda excecao lancada pelo SDK -- ver SDK_CAPABILITY_SPEC.md secao 6.4. http_status/code sao
None para NetworkError/TimeoutError (nenhuma resposta HTTP existiu); code/details sao sempre None
para AuthenticationError/AuthorizationError (401/403 nunca tem corpo -- ver secao 6.3).
"""

from __future__ import annotations

from typing import Any


class IshtaranError(Exception):
    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        code: str | None = None,
        request_id: str | None = None,
        details: Any = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.code = code
        # Sempre None hoje -- a API real nao implementa nenhum mecanismo de request/correlation ID
        # (busca exaustiva em src/CompositionRoot/, zero ocorrencia -- ver secao 12.1).
        self.request_id = request_id
        self.details = details
        self.retryable = retryable


class AuthenticationError(IshtaranError):
    """401 -- sem corpo JSON (ver secao 6.3). code/details sao sempre None."""

    def __init__(self, message: str) -> None:
        super().__init__(message, http_status=401, retryable=False)


class AuthorizationError(IshtaranError):
    """403 -- sem corpo JSON (ver secao 6.3)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, http_status=403, retryable=False)


class ValidationError(IshtaranError):
    """400, code=VALIDATION_ERROR. message e UMA string com todos os erros unidos por '; '."""

    def __init__(self, message: str, request_id: str | None, details: Any) -> None:
        super().__init__(message, http_status=400, code="VALIDATION_ERROR", request_id=request_id, details=details)


class NotFoundError(IshtaranError):
    """404, code=NOT_FOUND."""

    def __init__(self, message: str, request_id: str | None, details: Any) -> None:
        super().__init__(message, http_status=404, code="NOT_FOUND", request_id=request_id, details=details)


class ConflictError(IshtaranError):
    """409, qualquer code de conflito exceto IDEMPOTENCY_KEY_CONFLICT."""

    def __init__(self, message: str, code: str | None, request_id: str | None, details: Any) -> None:
        super().__init__(message, http_status=409, code=code, request_id=request_id, details=details)


class IdempotencyConflictError(ConflictError):
    """409, code=IDEMPOTENCY_KEY_CONFLICT -- mesma chave reenviada com payload diferente."""

    def __init__(self, message: str, request_id: str | None, details: Any) -> None:
        super().__init__(message, "IDEMPOTENCY_KEY_CONFLICT", request_id, details)


class RateLimitError(IshtaranError):
    """429, code=RATE_LIMITED. Sempre retryable -- expoe retry_after_seconds do header real."""

    def __init__(self, message: str, request_id: str | None, details: Any, retry_after_seconds: int | None) -> None:
        super().__init__(message, http_status=429, code="RATE_LIMITED", request_id=request_id, details=details, retryable=True)
        self.retry_after_seconds = retry_after_seconds


class NetworkError(IshtaranError):
    """Falha de transporte -- sem nenhuma resposta HTTP. Sempre retryable."""

    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message, retryable=True)
        if cause is not None:
            self.__cause__ = cause


class TimeoutError(IshtaranError):  # noqa: A001 -- sombreia builtins.TimeoutError de proposito,
    # para manter paridade exata de nome com Java/TypeScript (regra do brief) -- codigo interno do
    # SDK que precisa do timeout de rede real do httpx usa httpx.TimeoutException, nao o builtin,
    # entao nao ha colisao pratica dentro deste pacote.
    """Connect/request timeout excedido, ou waitFor excedendo o prazo. Sempre retryable."""

    def __init__(self, message: str, cause: BaseException | None = None) -> None:
        super().__init__(message, retryable=True)
        if cause is not None:
            self.__cause__ = cause


class ApiError(IshtaranError):
    """Fallback -- qualquer 4xx/5xx cujo code nao e reconhecido."""

    def __init__(self, message: str, http_status: int, code: str | None, request_id: str | None, details: Any, retryable: bool) -> None:
        super().__init__(message, http_status=http_status, code=code, request_id=request_id, details=details, retryable=retryable)
