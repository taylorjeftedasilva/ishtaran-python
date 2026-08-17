# Ishtaran Python SDK — Exemplos

11 exemplos numerados, código real (nunca pseudocódigo), verificados com `python -m py_compile` +
`mypy --strict` contra o SDK real (`ishtaran`, instalado via `pip install -e .`).

| # | Arquivo | Demonstra |
|---|---|---|
| 01 | `01_auth.py` | Quickstart mínimo |
| 02 | `02_create_account.py` | Criar Account (Core) |
| 03 | `03_receive_payment_easy.py` | Receber pagamento (Easy Mode) + `wait_for_payment` |
| 04 | `04_create_transaction_core.py` | Criar Transaction com participantes (Core) |
| 05 | `05_payment_intent_core.py` | Payment Intent + `deposit_address` real (Core) |
| 06 | `06_settlement.py` | Liquidar Transaction + resumo (Core) |
| 07 | `07_withdrawal_quote.py` | Cotar saque, Network Fee sempre visível (Core) |
| 08 | `08_withdrawal.py` | Executar saque (Easy Mode) + `wait_for` |
| 09 | `09_ledger.py` | Saldo + Ledger Entries com paginação real (generator) |
| 10 | `10_webhook_verification.py` | Verificação de assinatura — **único 100% executável sem API real** |
| 11 | `11_sandbox.py` | Faucet + confirmação simulada (Sandbox) |

## Rodando

```bash
cd sdks/python
source .venv/bin/activate  # ver README.md principal para setup
export ISHTARAN_API_KEY=...
export ISHTARAN_ORGANIZATION_ID=...
# ... demais variáveis por exemplo, ver o topo de cada arquivo

python examples/01_auth.py
```

O `10_webhook_verification.py` roda sem nenhuma variável de ambiente real:

```bash
python examples/10_webhook_verification.py
```
