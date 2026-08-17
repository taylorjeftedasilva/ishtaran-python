import pytest

from ishtaran.config.client_config import build_client_config
from ishtaran.config.endpoints import LOCAL_BASE_URL
from ishtaran.config.environment import Environment


def test_local_resolves_to_real_default_without_explicit_base_url() -> None:
    config = build_client_config(environment=Environment.LOCAL)
    assert config.base_url == LOCAL_BASE_URL


def test_sandbox_without_explicit_base_url_raises() -> None:
    with pytest.raises(ValueError):
        build_client_config(environment=Environment.SANDBOX)


def test_production_without_explicit_base_url_raises() -> None:
    with pytest.raises(ValueError):
        build_client_config(environment=Environment.PRODUCTION)


def test_explicit_base_url_always_wins() -> None:
    config = build_client_config(environment=Environment.SANDBOX, base_url="https://custom.example.com")
    assert config.base_url == "https://custom.example.com"


def test_insecure_tls_override_only_allowed_for_local() -> None:
    with pytest.raises(ValueError):
        build_client_config(
            environment=Environment.SANDBOX, base_url="https://custom.example.com",
            allow_insecure_tls_for_local_development=True,
        )


def test_insecure_tls_override_allowed_for_local() -> None:
    config = build_client_config(environment=Environment.LOCAL, allow_insecure_tls_for_local_development=True)
    assert config.allow_insecure_tls_for_local_development is True


def test_repr_never_leaks_api_key_in_plain_text() -> None:
    config = build_client_config(environment=Environment.LOCAL, api_key="supersecretapikeyvalue1234567890")
    described = repr(config)
    assert "****" in described
    assert "supersecretapikeyvalue1234567890" not in described


def test_defaults_are_sane_and_finite() -> None:
    config = build_client_config()
    assert config.connect_timeout_seconds > 0
    assert config.request_timeout_seconds > 0
    assert config.user_agent.startswith("ishtaran-python/")
