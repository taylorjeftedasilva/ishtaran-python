from decimal import Decimal

from ishtaran.util.json_util import field, money, parse_lossless, safe_int


def test_preserves_exact_precision_from_json_number_token() -> None:
    raw = parse_lossless(
        '{"requestedAmount": 100.123456789012345678, "estimatedNetworkFee": 0.4, '
        '"estimatedRecipientAmount": 99.723456789012345678}'
    )
    assert money(field(raw, "requestedAmount")) == Decimal("100.123456789012345678")
    assert money(field(raw, "estimatedNetworkFee")) == Decimal("0.4")
    assert money(field(raw, "estimatedRecipientAmount")) == Decimal("99.723456789012345678")


def test_confirms_native_float_would_have_lost_this_precision() -> None:
    # Prova que o problema e real, nao hipotetico -- json.loads padrao (sem parse_float=Decimal)
    # converteria para float e perderia digitos.
    lossy = float("100.123456789012345678")
    assert str(lossy) != "100.123456789012345678"


def test_safe_int_extracts_small_integers_as_real_int() -> None:
    raw = parse_lossless('{"decimals": 6, "confirmationCount": 12}')
    assert safe_int(field(raw, "decimals")) == 6
    assert safe_int(field(raw, "confirmationCount")) == 12


def test_matches_real_backend_small_payment_example() -> None:
    # Mesmo cenario do teste de backend ExecuteSettlement_SmallPayment_NoFloor (0,9% sem piso).
    raw = parse_lossless('{"grossAmount": 1, "platformFeeAmount": 0.009, "distributableAmount": 0.991}')
    assert money(field(raw, "platformFeeAmount")) == Decimal("0.009")
    assert money(field(raw, "distributableAmount")) == Decimal("0.991")


def test_int_valued_money_field_still_becomes_decimal_never_int() -> None:
    # amount sem parte fracionaria (ex.: 100, sem ".0") ainda deve virar Decimal consistente,
    # nunca int -- parse_int=Decimal cobre exatamente esse caso.
    raw = parse_lossless('{"amount": 100}')
    value = money(field(raw, "amount"))
    assert isinstance(value, Decimal)
    assert value == Decimal("100")
