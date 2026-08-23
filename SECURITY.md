# Security

See `SECURITY_REVIEW.md` for the full formal checklist.

## Secrets never leak

`api_key`/`endpoint_secret`/tokens never appear in logs, exceptions, or `repr()`.
`IshtaranClientConfig.__repr__` masks the API Key. Opt-in logging never logs
`Authorization`/`X-Api-Key` in plain text nor the raw body.

## TLS

Verified by default (native `httpx` behavior), with no disable switch exposed by this SDK.

## Webhook

`hmac.compare_digest` (real stdlib constant time), validates the timestamp against replay,
never logs the secret.

## Dependencies

Minimal: `httpx` (the only production dependency — mature, widely used synchronous HTTP
transport). Native stdlib `hashlib`/`hmac`/`json`/`decimal`, zero third-party dependency for
money precision (`json.loads(parse_float=Decimal, parse_int=Decimal)`) or HMAC.
