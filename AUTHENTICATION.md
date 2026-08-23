# Authentication

Two real mechanisms (see `SDK_CAPABILITY_SPEC.md` §3).

## `X-Api-Key` (recommended)

```python
client = IshtaranClient.create(api_key="<your API Key>", environment=Environment.LOCAL)
```

Works for read and write on the 8 Data Plane modules. Does not work today for Control Plane,
reading the AssetNetworkCatalog, or WebhookEndpoint management (real API gaps, §12.3/§12.4).

## Member JWT (human login)

```python
client.auth.login(email, password)
# the client now uses the token internally for every subsequent Control Plane call.
org = client.organizations.get(organization_id)
```

## Never mix them silently

The SDK never sends the API Key as a Bearer token nor the JWT as `X-Api-Key`. If both are
configured, both headers are sent on Data Plane routes — avoid configuring both at once
against different Organizations (precedence not verified live by this SDK).
