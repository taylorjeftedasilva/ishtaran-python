# SECURITY_REVIEW.md — Ishtaran Python SDK

Checklist from §57 of the SDK Program brief. Same discipline as Java/TypeScript: every item
backed by real evidence (test or code reading), never assumed.

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Secrets never logged | ✅ PASS | `test_logging_transport.py` -- `redacted_headers` never exposes API Key/Authorization in plain text |
| 2 | API Key never in URL/querystring | ✅ PASS | `AuthenticatingTransport` only attaches it via header; no resource builds a URL with the key |
| 3 | TLS verified by default | ✅ PASS | `httpx.Client` verifies the certificate by default; no disable switch exposed by this SDK |
| 4 | Constant-time webhook signature comparison | ✅ PASS | Real `hmac.compare_digest` (stdlib) -- `test_webhook_signature_verifier.py` (7 tests, including a vector computed independently via `hmac`/`hashlib` directly, the same vector used across all 3 languages) |
| 5 | Safe retries (never blind on a non-idempotent mutation) | ✅ PASS | `test_retrying_transport.py` -- never retries on 400/401/403/404/409/422; 5xx only with idempotency/GET |
| 6 | Mandatory timeout, never infinite | ✅ PASS | `httpx.Timeout(connect=..., read=..., write=..., pool=...)` always applied; finite defaults (`test_client_config.py`) |
| 7 | Central redaction in opt-in logging | ✅ PASS | `LoggingTransport` never logs the raw body, only method/path/status/duration |
| 8 | Minimal, scanned dependencies | ✅ PASS | 1 production dependency (`httpx`, mature/widely used, actively maintained). No third-party dependency for money precision (stdlib `decimal`/`json`) or HMAC (stdlib `hmac`/`hashlib`) |
| 9 | Money never loses precision | ✅ PASS | `test_json_util.py` -- `json.loads(parse_float=Decimal, parse_int=Decimal)` preserves the exact text; explicit test confirming that native `float()` WOULD have lost that precision |
| 10 | Malicious/malformed response never crashes the client | ✅ PASS | `test_error_mapper.py` -- a malformed body never raises a parsing exception; unknown enums never raise (`test_enums.py`) |
| 11 | Unbounded response body size | ⚠️ **REAL LIMITATION, NOT FIXED** | `httpx.Client.request()` buffers the entire response in memory with no configurable limit in this version. Same limitation documented in the Java/TypeScript SDKs |
| 12 | Safe deserialization | ✅ PASS | `json.loads` never does polymorphic/reflection-based deserialization -- it always produces plain structural data, manually mapped to known `dataclasses` |
| 13 | User-controlled URL / SSRF | ✅ PASS | `base_url` is always explicit and fixed at client construction -- no business method accepts a URL override (verified: no method in `resources/*.py` takes a URL parameter) |
| 14 | HTTP redirect behavior | ✅ PASS | `httpx.Client(follow_redirects=False)` since this SDK's first version -- any 3xx is treated as a `NetworkError`, never followed automatically. Applied **proactively** in this language, learning from the real finding fixed in the TypeScript SDK (never reintroduced here) |
| 15 | Header injection | ✅ PASS | `httpx`/`h11` validate header names/values (reject CR/LF) -- never built via raw string concatenation |
| 16 | Query string injection | ✅ PASS (real finding fixed in this review) | See "Finding fixed" below |
| 17 | Proxy behavior | N/A | Not applicable -- no custom proxy configuration exposed; `httpx` uses the environment's default behavior |

## Finding fixed during this review

**`date_from`/`date_to` concatenated raw into the query string** of `WithdrawalsResource.list`
and `LedgerResource.list_entries` -- the same risk class already found and fixed in the Java SDK
(`eventType` in `WebhookEndpointsResource`) and prevented from the start in the TypeScript SDK
(via `URLSearchParams`). A malicious value in `date_from` (e.g. `"2026-01-01&take=99999"`) could
inject an unintended query parameter. Fixed with `urllib.parse.urlencode` in both methods --
`WebhookEndpointsResource.list_deliveries` already used this pattern since the initial
implementation (it never had the bug). Covered by `test_query_encoding_safety.py`.

## Additional static verification (beyond the brief's checklist)

`mypy --strict` clean across all 63 modules of the SDK (`python -m mypy src/ishtaran` ->
`Success: no issues found`) -- reduces the surface of type bugs that could manifest as unsafe
runtime behavior (e.g. an unhandled `None`, the wrong type passed into serialization).

## Known limitations (documented, never hidden)

1. **Unbounded response body size** (item 11) -- same limitation as the Java/TypeScript SDKs,
   same justification (the risk only exists if `base_url` points to a compromised host).
2. **`EnumRegistry` uses dynamic `setattr`** -- `WithdrawalStatus.COMPLETED` etc. are not
   statically known to mypy without `# type: ignore[attr-defined]` at the call site; not a
   security risk (the runtime value is always correct, only static checking doesn't cover this
   specific case), but it is a documented typing limitation.
3. **Sync only** -- not a security item, but it affects the consumer's concurrency model (see
   `CHANGELOG.md`).

## Verdict

**PASS**, with 3 explicitly documented limitations -- no critical or high-severity finding
remains unfixed or unjustified; the one real behavioral finding (query string injection) was
fixed, not just noted.
