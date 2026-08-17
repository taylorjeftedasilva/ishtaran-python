# Authentication

Dois mecanismos reais (ver `SDK_CAPABILITY_SPEC.md` §3).

## `X-Api-Key` (recomendado)

```python
client = IshtaranClient.create(api_key="<sua API Key>", environment=Environment.LOCAL)
```

Funciona em leitura e escrita nos 8 módulos Data Plane. Não funciona hoje para Control Plane,
leitura de AssetNetworkCatalog, ou gestão de WebhookEndpoint (lacunas reais da API, §12.3/§12.4).

## Member JWT (login humano)

```python
client.auth.login(email, password)
# client agora usa o token internamente em toda chamada de Control Plane subsequente.
org = client.organizations.get(organization_id)
```

## Nunca misture disfarçadamente

O SDK nunca envia a API Key como Bearer nem o JWT como `X-Api-Key`. Se ambos estiverem
configurados, ambos os headers são enviados nas rotas Data Plane — evite configurá-los
simultaneamente contra Organizations diferentes (precedência não verificada ao vivo por este SDK).
