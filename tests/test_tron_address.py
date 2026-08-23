from __future__ import annotations

import pytest

from ishtaran.wallet import derive_tron_address, generate


def test_produces_a_34_character_address_starting_with_t() -> None:
    generated = generate()

    address = derive_tron_address(generated.wallet.account_extended_public_key, 0)

    assert len(address) == 34
    assert address.startswith("T")


def test_is_deterministic_same_xpub_and_index_always_produce_the_same_address() -> None:
    generated = generate()

    first = derive_tron_address(generated.wallet.account_extended_public_key, 7)
    second = derive_tron_address(generated.wallet.account_extended_public_key, 7)

    assert first == second


def test_different_indices_produce_different_addresses() -> None:
    generated = generate()

    address_at_zero = derive_tron_address(generated.wallet.account_extended_public_key, 0)
    address_at_one = derive_tron_address(generated.wallet.account_extended_public_key, 1)

    assert address_at_zero != address_at_one


def test_different_wallets_produce_different_addresses_at_the_same_index() -> None:
    wallet_a = generate()
    wallet_b = generate()

    address_a = derive_tron_address(wallet_a.wallet.account_extended_public_key, 0)
    address_b = derive_tron_address(wallet_b.wallet.account_extended_public_key, 0)

    assert address_a != address_b


def test_rejects_a_negative_index() -> None:
    generated = generate()

    with pytest.raises(ValueError):
        derive_tron_address(generated.wallet.account_extended_public_key, -1)
