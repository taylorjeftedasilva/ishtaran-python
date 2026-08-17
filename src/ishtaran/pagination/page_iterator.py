"""
Generator lazy sobre um endpoint com paginacao real skip/take -- busca a proxima pagina sob
demanda, nunca carrega a colecao inteira de uma vez (regra do brief: "nunca bulk-loading
unbounded"). Usado so nos 2 endpoints do SDK com paginacao real de verdade (Withdrawals.list,
Ledger.list_entries -- ver SDK_CAPABILITY_SPEC.md secao 12.7); todo outro endpoint de listagem
devolve uma list simples (ja iteravel), sem fingir paginacao que a API nao tem.
"""

from __future__ import annotations

from typing import Callable, Iterator, TypeVar

T = TypeVar("T")


def paginate(page_size: int, fetch_page: Callable[[int, int], list[T]]) -> Iterator[T]:
    if page_size <= 0:
        raise ValueError("page_size deve ser positivo")
    skip = 0
    while True:
        page = fetch_page(skip, page_size)
        yield from page
        if len(page) < page_size:
            return
        skip += page_size
