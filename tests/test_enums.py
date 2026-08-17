from ishtaran.model.enums import AccountStatus, WithdrawalStatus


def test_group_b_known_int_value_maps_to_named_constant() -> None:
    status = WithdrawalStatus.from_raw(8)
    assert status == WithdrawalStatus.COMPLETED  # type: ignore[attr-defined]
    assert not WithdrawalStatus.is_unknown(status)


def test_group_b_unknown_int_value_never_raises_falls_back_to_unknown() -> None:
    status = WithdrawalStatus.from_raw(99)
    assert WithdrawalStatus.is_unknown(status)
    assert status.raw_value == 99
    assert status.name == "UNKNOWN"


def test_group_a_known_string_value_maps_to_named_constant() -> None:
    status = AccountStatus.from_raw("Frozen")
    assert status == AccountStatus.FROZEN  # type: ignore[attr-defined]
    assert not AccountStatus.is_unknown(status)


def test_group_a_unknown_string_value_never_raises_falls_back_to_unknown() -> None:
    status = AccountStatus.from_raw("SomeFutureStatus")
    assert AccountStatus.is_unknown(status)
    assert status.raw_value == "SomeFutureStatus"


def test_equality_is_by_raw_value() -> None:
    assert WithdrawalStatus.from_raw(8) == WithdrawalStatus.from_raw(8)
