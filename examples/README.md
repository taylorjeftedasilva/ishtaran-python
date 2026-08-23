# Ishtaran Python SDK -- Examples

13 numbered examples, real code (never pseudocode), verified with `python -m py_compile` +
`mypy --strict` against the real SDK (`ishtaran`, installed via `pip install -e .`).

| # | File | Demonstrates |
|---|---|---|
| 01 | `01_auth.py` | Minimal quickstart |
| 02 | `02_create_account.py` | Create an Account (Core) |
| 03 | `03_receive_payment_easy.py` | Receive a payment (Easy Mode) + `wait_for_payment` |
| 04 | `04_create_transaction_core.py` | Create a Transaction with participants (Core) |
| 05 | `05_payment_intent_core.py` | Payment Intent + real `deposit_address` (Core) |
| 06 | `06_settlement.py` | Settle a Transaction + summary (Core) |
| 07 | `07_withdrawal_quote.py` | Quote a withdrawal, Network Fee always visible (Core) |
| 08 | `08_withdrawal.py` | Execute a withdrawal (Easy Mode) + `wait_for` |
| 09 | `09_ledger.py` | Balance + Ledger Entries with real pagination (generator) |
| 10 | `10_webhook_verification.py` | Signature verification -- **the only one 100% runnable without a real API** |
| 11 | `11_sandbox.py` | Faucet + simulated confirmation (Sandbox) |
| 12 | `12_account_holder_invitation.py` | AccountHolder invitation + signup-and-claim (DEC-032) |
| 13 | `13_self_custody_signing.py` | Self-custody end to end: generates a local wallet, registers it, allocates an address, creates/signs/submits a `SigningRequest`, confirms the broadcast (SPEC-017-021) |

## Running

```bash
cd sdks/python
source .venv/bin/activate  # see the main README.md for setup
export ISHTARAN_API_KEY=...
export ISHTARAN_ORGANIZATION_ID=...
# ... other variables per example, see the top of each file

python examples/01_auth.py
```

`10_webhook_verification.py` runs with no real environment variables at all:

```bash
python examples/10_webhook_verification.py
```
