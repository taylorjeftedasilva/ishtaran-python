from ishtaran.util.redactor import is_sensitive_header, mask


def test_mask_long_secret_shows_only_first_last_4() -> None:
    assert mask("QUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVoxMjM0NTY3ODkw") == "QUJD****ODkw"


def test_mask_short_secret_never_partially_leaked() -> None:
    assert mask("short") == "****"


def test_mask_none_returns_placeholder() -> None:
    assert mask(None) == "None"


def test_is_sensitive_header_case_insensitive() -> None:
    assert is_sensitive_header("Authorization")
    assert is_sensitive_header("x-api-key")
    assert is_sensitive_header("X-API-KEY")
    assert not is_sensitive_header("User-Agent")
