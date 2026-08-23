from __future__ import annotations

import hashlib

import coincurve
import pytest

from ishtaran.wallet import generate
from ishtaran.wallet import _bip32


def _sha256_of(value: str) -> bytes:
    return hashlib.sha256(value.encode("utf-8")).digest()


def _address_public_key_for(account_extended_public_key: str, index: int) -> bytes:
    """Derives the same address PUBLIC key that InMemorySigner.sign uses PRIVATELY, but only from the xpub -- proves verification never needs the private key."""
    account_key = _bip32.parse_extended_public_key(account_extended_public_key)
    change_key = _bip32.derive_child(account_key, 0)
    address_key = _bip32.derive_child(change_key, index)
    return address_key.public_key


def _verify_der(digest: bytes, der_signature: bytes, public_key: bytes) -> bool:
    return coincurve.verify_signature(der_signature, digest, public_key, hasher=None)


def test_sign_produces_a_signature_that_verifies_against_the_corresponding_public_key() -> None:
    generated = generate()
    digest = _sha256_of("canonical-hash-placeholder")

    der_signature = generated.signer.sign(3, digest)

    public_key = _address_public_key_for(generated.wallet.account_extended_public_key, 3)
    assert _verify_der(digest, der_signature, public_key) is True


def test_signature_does_not_verify_against_a_different_derivation_index() -> None:
    generated = generate()
    digest = _sha256_of("canonical-hash-placeholder")

    der_signature = generated.signer.sign(3, digest)

    wrong_public_key = _address_public_key_for(generated.wallet.account_extended_public_key, 4)
    assert _verify_der(digest, der_signature, wrong_public_key) is False


def test_signature_does_not_verify_against_a_tampered_hash() -> None:
    generated = generate()
    digest = _sha256_of("canonical-hash-placeholder")
    tampered_digest = _sha256_of("canonical-hash-placeholder-tampered")

    der_signature = generated.signer.sign(3, digest)

    public_key = _address_public_key_for(generated.wallet.account_extended_public_key, 3)
    assert _verify_der(tampered_digest, der_signature, public_key) is False


def test_rejects_a_hash_that_is_not_32_bytes() -> None:
    generated = generate()
    with pytest.raises(ValueError):
        generated.signer.sign(0, b"\x01\x02\x03")


def test_rejects_a_negative_derivation_index() -> None:
    generated = generate()
    digest = _sha256_of("canonical-hash-placeholder")
    with pytest.raises(ValueError):
        generated.signer.sign(-1, digest)


def test_account_extended_public_key_never_contains_private_key_material() -> None:
    generated = generate()

    assert generated.wallet.account_extended_public_key.startswith("xpub")
    assert "xprv" not in generated.wallet.account_extended_public_key
