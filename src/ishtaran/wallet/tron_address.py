"""
Tron mainnet address derivation from an extended public key (xpub) -- CKDpub only
(non-hardened BIP32), never needs/touches the private key (INV-SC-01). Mirrors
`TronAddressDerivationProvider` (backend) field for field -- used by the SDK to independently
verify `sourceAddress`/`destinationAddress` before signing (defense in depth).

Algorithm: uncompressed secp256k1 public key (65 bytes: 0x04||X(32)||Y(32)) -> strip the 0x04
prefix -> Keccak-256 (64-byte input) -> last 20 bytes -> mainnet prefix 0x41 -> Base58Check.
"""

from __future__ import annotations

import coincurve
from Crypto.Hash import keccak
from base58 import b58encode_check

from . import _bip32

_MAINNET_PREFIX = b"\x41"


def derive_tron_address(account_extended_public_key: str, index: int) -> str:
    if not (0 <= index <= 0xFFFFFFFF):
        raise ValueError("index is outside the range of a non-hardened BIP32 index.")

    account_key = _bip32.parse_extended_public_key(account_extended_public_key)
    change_key = _bip32.derive_child(account_key, 0)
    address_key = _bip32.derive_child(change_key, index)

    uncompressed = coincurve.PublicKey(address_key.public_key).format(compressed=False)  # 65 bytes: 0x04||X||Y
    hash_input = uncompressed[1:]  # strip the 0x04 prefix -> 64 bytes

    digest = keccak.new(data=hash_input, digest_bits=256).digest()
    last_20 = digest[12:32]

    payload = _MAINNET_PREFIX + last_20
    return b58encode_check(payload).decode("ascii")
