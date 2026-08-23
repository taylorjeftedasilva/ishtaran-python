from __future__ import annotations

import pytest

from ishtaran.wallet import generate, restore


def test_generate_produces_a_24_word_mnemonic_and_a_wallet_with_matching_public_material() -> None:
    generated = generate()

    assert len(generated.mnemonic.split()) == 24
    assert generated.wallet.scheme == "TRON_BIP44_HARDENED_ACCOUNT"
    assert generated.wallet.account_extended_public_key == generated.signer.account_extended_public_key()
    assert generated.wallet.account_extended_public_key.startswith("xpub")


def test_generate_twice_never_produces_the_same_mnemonic() -> None:
    first = generate()
    second = generate()

    assert first.mnemonic != second.mnemonic
    assert first.wallet.account_extended_public_key != second.wallet.account_extended_public_key


def test_restore_with_the_same_mnemonic_reproduces_the_same_account_extended_public_key() -> None:
    original = generate()

    restored = restore(original.mnemonic)

    assert restored.wallet.account_extended_public_key == original.wallet.account_extended_public_key


def test_restore_with_a_different_passphrase_produces_a_different_wallet() -> None:
    original = generate()

    restored_with_passphrase = restore(original.mnemonic, "extra-security-word")

    assert restored_with_passphrase.wallet.account_extended_public_key != original.wallet.account_extended_public_key


def test_restore_with_an_invalid_mnemonic_raises() -> None:
    with pytest.raises(ValueError):
        restore("not a valid bip39 mnemonic at all")


def test_restore_with_valid_words_but_an_invalid_checksum_raises() -> None:
    bogus_checksum = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    with pytest.raises(ValueError):
        restore(bogus_checksum)
