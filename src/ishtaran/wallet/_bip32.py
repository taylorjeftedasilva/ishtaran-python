"""
Minimal BIP32 implementation (hierarchical deterministic derivation) over real secp256k1
(coincurve, libsecp256k1/Bitcoin Core bindings) -- deliberately without a ready-made HD
wallet library (same rationale as TDR-017/bitcoinj/noble-scure): explicit control over the
exact derivation math, never an abstraction that hides the byte-order/format used.

Only implements what this SDK needs: master key from seed, hardened CKD (for
m/44'/195'/0'), non-hardened CKD (for change/index), and Base58Check xpub
serialization/parsing in the standard Bitcoin mainnet format (same version bytes as
NBitcoin/bitcoinj/@scure/bip32 use -- 0x0488B21E/0x0488ADE4 -- reused only as the
standard BIP32 serialization, never as a real association with the Bitcoin network).
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

import coincurve
from Crypto.Hash import RIPEMD160
from base58 import b58encode_check, b58decode_check

HARDENED_OFFSET = 0x80000000
SECP256K1_ORDER = 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_BAAEDCE6_AF48A03B_BFD25E8C_D0364141
XPUB_VERSION = bytes.fromhex("0488B21E")
XPRV_VERSION = bytes.fromhex("0488ADE4")


@dataclass(frozen=True)
class ExtendedKey:
    """BIP32 extended key -- `private_key` is `None` for a public-key-only key (parsed xpub)."""

    chain_code: bytes
    public_key: bytes  # always compressed, 33 bytes
    private_key: bytes | None  # 32 bytes, or None
    depth: int
    parent_fingerprint: bytes  # 4 bytes
    child_number: int  # includes HARDENED_OFFSET when hardened


def _hash160(data: bytes) -> bytes:
    sha = hashlib.sha256(data).digest()
    ripemd = RIPEMD160.new(sha).digest()
    return ripemd


def _fingerprint(public_key: bytes) -> bytes:
    return _hash160(public_key)[:4]


def _ser32(index: int) -> bytes:
    return index.to_bytes(4, "big")


def from_seed(seed: bytes) -> ExtendedKey:
    i = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    private_key, chain_code = i[:32], i[32:]
    public_key = coincurve.PublicKey.from_secret(private_key).format(compressed=True)
    return ExtendedKey(chain_code, public_key, private_key, depth=0, parent_fingerprint=b"\x00\x00\x00\x00", child_number=0)


def derive_child(parent: ExtendedKey, index: int) -> ExtendedKey:
    """CKD -- hardened if `index >= HARDENED_OFFSET` (requires `parent.private_key`), non-hardened otherwise (works with a public key only)."""
    hardened = index >= HARDENED_OFFSET

    if hardened:
        if parent.private_key is None:
            raise ValueError("Hardened derivation requires the parent's private key (impossible from an xpub).")
        data = b"\x00" + parent.private_key + _ser32(index)
    else:
        data = parent.public_key + _ser32(index)

    i = hmac.new(parent.chain_code, data, hashlib.sha512).digest()
    il, ir = i[:32], i[32:]
    il_int = int.from_bytes(il, "big")
    if il_int >= SECP256K1_ORDER:
        raise ValueError("Invalid derivation (IL >= curve order) -- negligible probability, an index should never produce this in practice.")

    parent_fingerprint = _fingerprint(parent.public_key)

    if parent.private_key is not None:
        child_private_key = coincurve.PrivateKey(parent.private_key).add(il, update=False).secret
        child_public_key = coincurve.PublicKey.from_secret(child_private_key).format(compressed=True)
        return ExtendedKey(ir, child_public_key, child_private_key, parent.depth + 1, parent_fingerprint, index)

    # CKDpub -- non-hardened only (already guaranteed above), never needs/touches the private key (INV-SC-01).
    parent_public_key_point = coincurve.PublicKey(parent.public_key)
    child_public_key = parent_public_key_point.add(il, update=False).format(compressed=True)
    return ExtendedKey(ir, child_public_key, None, parent.depth + 1, parent_fingerprint, index)


def serialize_public(key: ExtendedKey) -> str:
    payload = (
        XPUB_VERSION
        + key.depth.to_bytes(1, "big")
        + key.parent_fingerprint
        + key.child_number.to_bytes(4, "big")
        + key.chain_code
        + key.public_key
    )
    return b58encode_check(payload).decode("ascii")


def parse_extended_public_key(xpub: str) -> ExtendedKey:
    payload = b58decode_check(xpub)
    if len(payload) != 78:
        raise ValueError("Malformed xpub -- unexpected payload size.")
    version = payload[0:4]
    if version != XPUB_VERSION:
        raise ValueError("Malformed xpub -- version bytes do not match the standard BIP32 mainnet format.")
    depth = payload[4]
    parent_fingerprint = payload[5:9]
    child_number = int.from_bytes(payload[9:13], "big")
    chain_code = payload[13:45]
    public_key = payload[45:78]
    return ExtendedKey(chain_code, public_key, None, depth, parent_fingerprint, child_number)
