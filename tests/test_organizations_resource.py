from ishtaran.resources.organizations_resource import OrganizationsResource
from .fake_transport import FakeHttpTransport


def test_create_without_explicit_key_auto_generates_header_never_body_field() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, '{"id":"11111111-1111-1111-1111-111111111111"}'))
    resource = OrganizationsResource(fake)

    resource.create("Acme Inc")

    sent = fake.received[0]
    assert sent.headers.get("Idempotency-Key")
    assert not (sent.body and "idempotencyKey" in sent.body)


def test_create_explicit_key_never_overwritten() -> None:
    fake = FakeHttpTransport().enqueue(FakeHttpTransport.json(201, '{"id":"11111111-1111-1111-1111-111111111111"}'))
    resource = OrganizationsResource(fake)

    resource.create("Acme Inc", idempotency_key="my-explicit-key")

    assert fake.received[0].headers.get("Idempotency-Key") == "my-explicit-key"
