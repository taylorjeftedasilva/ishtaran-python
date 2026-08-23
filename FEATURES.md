# Features

Derived from [`SDK_FEATURE_MATRIX.md`](../../SDK_FEATURE_MATRIX.md). Core API: 93/93 real
operations (16/16 modules). Easy Mode: 100%. Cross-cutting: 100% (config, auth, errors, retry,
idempotency, pagination, forward-compatible enums, security/redaction, opt-in logging, safe
wait_for, validated wheel+sdist packaging).

100% functional parity with the Java SDK (reference implementation) — same business-concept
names, same defaults, same retry/idempotency/timeout policy, differing only in the language's
idiom (`client.withdrawals.quote(...)` identical in Python and TypeScript; Java uses
`client.withdrawals().quote(...)`).

## Extra compared to Java/TypeScript

- `mypy --strict` clean (full static verification).
- Money as a native `decimal.Decimal` — more idiomatic than TypeScript's `string`, with no
  third-party dependency for precision (the stdlib `json`/`decimal` already solve the problem).
