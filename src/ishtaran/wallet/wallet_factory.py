from __future__ import annotations

from dataclasses import dataclass

from mnemonic import Mnemonic

from . import _bip32
from .derivation_scheme import TRON_BIP44_HARDENED_ACCOUNT
from .signer import InMemorySigner

_ENTROPY_BITS = 256  # 24 words (BIP39)
_PURPOSE_44H = 44 + _bip32.HARDENED_OFFSET
_TRON_COIN_TYPE_195H = 195 + _bip32.HARDENED_OFFSET
_ACCOUNT_0H = 0 + _bip32.HARDENED_OFFSET
_MNEMO = Mnemonic("english")


@dataclass(frozen=True)
class Wallet:
    scheme: str
    account_extended_public_key: str


@dataclass(frozen=True)
class GeneratedWallet:
    """
    Result of `generate`/`restore` -- bundles the PUBLIC `Wallet` (safe to register via the API), the
    `InMemorySigner` ready to use, and the recovery mnemonic.

    The mnemonic is NEVER persisted or transmitted by this SDK on its own -- exporting it is always
    an explicit, local, opt-in action by the integrator (SPEC-018 brief section 9: "Secret export: explicit,
    local, opt-in. Never automatic. Never sent to the API.").
    """

    wallet: Wallet
    signer: InMemorySigner
    mnemonic: str


def generate() -> GeneratedWallet:
    words = _MNEMO.generate(strength=_ENTROPY_BITS)
    return _from_words(words, "")


def restore(mnemonic: str, passphrase: str = "") -> GeneratedWallet:
    if not _MNEMO.check(mnemonic):
        raise ValueError("Invalid mnemonic -- BIP39 checksum does not match.")
    return _from_words(mnemonic, passphrase)


def _from_words(mnemonic: str, passphrase: str) -> GeneratedWallet:
    seed = _MNEMO.to_seed(mnemonic, passphrase=passphrase)
    master = _bip32.from_seed(seed)
    purpose = _bip32.derive_child(master, _PURPOSE_44H)
    coin_type = _bip32.derive_child(purpose, _TRON_COIN_TYPE_195H)
    account = _bip32.derive_child(coin_type, _ACCOUNT_0H)

    signer = InMemorySigner.from_account_key(account)
    wallet = Wallet(scheme=TRON_BIP44_HARDENED_ACCOUNT, account_extended_public_key=signer.account_extended_public_key())

    return GeneratedWallet(wallet=wallet, signer=signer, mnemonic=mnemonic)
