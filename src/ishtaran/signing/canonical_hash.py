"""
SPEC-019 -- reference reimplementation of the backend's canonical algorithm
(`CreateSigningRequestCommandHandler.ComputeCanonicalLegHash`, C#). Must reproduce it byte for
byte -- see `docs/specs/execution-custody/CANONICAL-HASH-TEST-VECTORS.md` for the complete
specification and the reference vectors this function is tested against
(`tests/test_canonical_hash_reference_vectors.py`). Never JSON (key order/whitespace/number
formatting vary across languages, the classic source of cross-language divergence) --
a fixed string joined by "|", SHA-256, uppercase hex.
"""

from __future__ import annotations

import hashlib
from decimal import Context, Decimal, Inexact

_EIGHTEEN_FRACTIONAL_DIGITS = Decimal("1.000000000000000000")
# Python has no RoundingMode.UNNECESSARY equivalent to Java -- the Context's own Inexact trap
# plays the same role (raises instead of silently rounding a value with more than 18
# fractional digits), same pattern as the Java SDK's `RoundingMode.UNNECESSARY`.
_EXACT_ONLY_CONTEXT = Context(prec=60, traps=[Inexact])


def compute_canonical_hash(
    protocol_version: int,
    environment_id: str,
    wallet_id: str,
    derivation_reference: int,
    origin_reference: str,
    asset_network_id: str,
    source_address: str,
    leg_role: str,
    destination_address: str,
    amount: Decimal,
    expires_at_unix_seconds: int,
) -> str:
    """
    amount: `Decimal` -- formatted to exactly 18 fractional digits, with no grouping
      (equivalent to the C#'s "F18"/CultureInfo.InvariantCulture). `ROUND_UNNECESSARY` -- never
      silently rounds a value with more than 18 digits (same pattern as the Java SDK's
      `RoundingMode.UNNECESSARY`).
    expires_at_unix_seconds: integer Unix seconds (never ISO-8601, eliminates
      timezone/format ambiguity across languages).
    """
    normalized = "|".join([
        str(protocol_version),
        environment_id,
        wallet_id,
        str(derivation_reference),
        origin_reference,
        asset_network_id,
        source_address,
        leg_role,
        destination_address,
        _format_amount(amount),
        str(int(expires_at_unix_seconds)),
    ])

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest().upper()


def _format_amount(amount: Decimal) -> str:
    quantized = amount.quantize(_EIGHTEEN_FRACTIONAL_DIGITS, context=_EXACT_ONLY_CONTEXT)
    return format(quantized, "f")
