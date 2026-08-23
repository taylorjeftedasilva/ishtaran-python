"""
SPEC-019/brief section 10 ("Create deterministic test vectors shared across the 4 languages")
-- proves that this implementation reproduces the backend C# reference hashes byte-for-byte.
Inputs and expected hashes come from
docs/specs/execution-custody/CANONICAL-HASH-TEST-VECTORS.md -- the single source of truth. If
any of these fail, it's a real cross-language parity bug -- never adjust the expected value to
make the test pass, fix the algorithm.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from ishtaran.signing.canonical_hash import compute_canonical_hash

ENVIRONMENT_ID = "11111111-1111-1111-1111-111111111111"
WALLET_ID = "22222222-2222-2222-2222-222222222222"
ASSET_NETWORK_ID = "33333333-3333-3333-3333-333333333333"
SOURCE_ADDRESS = "TSourceAddress1234567890123456"
EXPIRES_AT = int(datetime(2026, 8, 22, 12, 15, 0, tzinfo=timezone.utc).timestamp())


def test_vector1_seller_leg() -> None:
    result = compute_canonical_hash(
        1, ENVIRONMENT_ID, WALLET_ID, 5, "settlement:44444444-4444-4444-4444-444444444444",
        ASSET_NETWORK_ID, SOURCE_ADDRESS, "Seller", "TSellerDestinationAddress123456", Decimal("90"), EXPIRES_AT,
    )
    assert result == "4623D19A6CFA8B7D7EA9D53F2E09DD5D98C0B237F980182CE3D74B3D9385CEA7"


def test_vector2_platform_fee_leg() -> None:
    result = compute_canonical_hash(
        1, ENVIRONMENT_ID, WALLET_ID, 5, "settlement:44444444-4444-4444-4444-444444444444",
        ASSET_NETWORK_ID, SOURCE_ADDRESS, "PlatformFee", "TIshtaranFeeDestinationAddr123", Decimal("1"), EXPIRES_AT,
    )
    assert result == "B11A474993D19ED9D0F97B657134A76931626BD52F6082879395AC54EEF8063B"


def test_vector3_withdrawal_leg() -> None:
    result = compute_canonical_hash(
        1, ENVIRONMENT_ID, WALLET_ID, 12, "withdrawal:55555555-5555-5555-5555-555555555555",
        ASSET_NETWORK_ID, SOURCE_ADDRESS, "Withdrawal", "TWithdrawalDestinationAddr1234", Decimal("250.5"), EXPIRES_AT,
    )
    assert result == "F297DBED71AA6646D93F489D9B4C2891779D440BC43A39D1820074358AE4F9EA"


def test_vector4_tampered_amount_produces_different_hash_never_the_original() -> None:
    result = compute_canonical_hash(
        1, ENVIRONMENT_ID, WALLET_ID, 5, "settlement:44444444-4444-4444-4444-444444444444",
        ASSET_NETWORK_ID, SOURCE_ADDRESS, "Seller", "TSellerDestinationAddress123456",
        Decimal("90.000000000000000001"), EXPIRES_AT,
    )
    assert result == "4FFA1C26FC90EAFEE081822F4E21AF2DEEA7235F07091DB7CD4C805446770792"
