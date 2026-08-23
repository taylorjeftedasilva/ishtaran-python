"""SPEC-021 -- signs the canonical hash of an ExecutionLeg at the given derivation index. The private key never leaves the implementation."""

from __future__ import annotations

from typing import Protocol

import coincurve

from . import _bip32


class Signer(Protocol):
    def sign(self, derivation_index: int, canonical_hash: bytes) -> bytes: ...


class InMemorySigner:
    """
    Reference implementation -- keeps the account's private key in plain memory for the
    lifetime of the process. **Documented as unsafe for Production** (no encryption at rest, no
    OS protection). Integrators who need real security should implement `Signer` against a
    Vault/KMS/HSM/Secret Manager/Keychain -- this SDK never requires a specific backend (SPEC-018
    brief section 8). The private key never leaves this class (never serialized, never logged,
    never sent to the Ishtaran API -- INV-SC-01).
    """

    def __init__(self, account_key: _bip32.ExtendedKey) -> None:
        self._account_key = account_key

    @staticmethod
    def from_account_key(account_key: _bip32.ExtendedKey) -> "InMemorySigner":
        return InMemorySigner(account_key)

    def account_extended_public_key(self) -> str:
        """Account-level xpub (Base58Check, mainnet -- reused purely as the standard BIP32 serialization, see the equivalent TDR-017)."""
        return _bip32.serialize_public(self._account_key)

    def sign(self, derivation_index: int, canonical_hash: bytes) -> bytes:
        if len(canonical_hash) != 32:
            raise ValueError("canonical_hash must be exactly 32 bytes (SHA-256 digest).")
        if not (0 <= derivation_index <= 0xFFFFFFFF):
            raise ValueError("derivation_index is outside the range of a non-hardened BIP32 index.")

        change_key = _bip32.derive_child(self._account_key, 0)
        address_key = _bip32.derive_child(change_key, derivation_index)
        if address_key.private_key is None:
            raise ValueError("Private key unavailable for this index -- account_key does not contain private material.")

        # coincurve (real libsecp256k1) signs the 32-byte digest directly (hasher=None --
        # never re-hashes) and already returns DER natively -- same format that
        # `IAddressDerivationProvider.VerifySignature` (backend, `ECDSASignature.FromDER`) expects.
        private_key = coincurve.PrivateKey(address_key.private_key)
        return private_key.sign(canonical_hash, hasher=None)
