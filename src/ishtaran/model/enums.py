"""
Ver SDK_CAPABILITY_SPEC.md secao 11.3 para a tabela completa nome-valor extraida literalmente dos
enums C# reais. Grupo B = inteiro bruto no JSON; Grupo A = string legivel.

Nota de tipagem: EnumRegistry usa setattr dinamico para expor STATUS.COMPLETED etc.; isso nao e
100% amigavel a checagem estatica mypy --strict (atributos dinamicos nao sao inferidos
estaticamente) -- limitacao conhecida e documentada, ver PYTHON_SDK_CHECKPOINT.md.
"""

from __future__ import annotations

from .enum_factory import create_enum

# ---- Grupo B (inteiro) ----
DepositStatus = create_enum({
    "DETECTED": 0, "CONFIRMING": 1, "CONFIRMED": 2, "UNDER_REVIEW": 3, "REORG_DETECTED": 4, "REJECTED": 5,
})
PaymentIntentStatus = create_enum({
    "PENDING": 0, "PARTIALLY_PAID": 1, "PAID": 2, "EXPIRED": 3, "CANCELLED": 4,
})
TransactionStatus = create_enum({
    "CREATED": 0, "AWAITING_FUNDS": 1, "FUNDED": 2, "RESERVED": 3, "SETTLED": 4,
    "PARTIALLY_REFUNDED": 5, "REFUNDED": 6, "FROZEN": 7, "CANCELLED": 8, "PARTIALLY_SETTLED": 9,
})
WithdrawalStatus = create_enum({
    "REQUESTED": 0, "VALIDATING": 1, "PENDING_APPROVAL": 2, "APPROVED": 3, "REJECTED": 4,
    "BROADCASTING": 5, "BROADCAST_FAILED": 6, "CONFIRMING": 7, "COMPLETED": 8, "CANCELLED": 9,
})
SettlementStatus = create_enum({"PENDING": 0, "EXECUTING": 1, "COMPLETED": 2, "FAILED": 3})
RefundStatus = create_enum({"REQUESTED": 0, "APPROVED": 1, "EXECUTED": 2, "REJECTED": 3})
SplitAllocationStatus = create_enum({"EXECUTED": 0, "RETAINED": 1, "RELEASED": 2})
SplitRetentionReason = create_enum({
    "ACCOUNT_NOT_FOUND": 0, "ACCOUNT_NOT_ACTIVE": 1, "ACCOUNT_NOT_AUTHORIZED_FOR_APPLICATION": 2,
})
WebhookEndpointStatus = create_enum({"ACTIVE": 0, "INACTIVE": 1})
WebhookDeliveryStatus = create_enum({
    "PENDING": 0, "DELIVERING": 1, "DELIVERED": 2, "RETRYING": 3, "DEAD_LETTER": 4, "CANCELLED": 5,
})
EntryNature = create_enum({"AVAILABLE": 0, "PENDING": 1, "RESERVED": 2})
ConditionOperator = create_enum({"EQUALS": 1, "GREATER_THAN_OR_EQUAL": 2, "LESS_THAN_OR_EQUAL": 3})
EventSource = create_enum({"APPLICATION": 1, "PLATFORM_TIMER": 2, "MANUAL_REVIEW": 3})
SimulatedBroadcastOutcome = create_enum({"ACCEPTED": 1, "FAILED": 2})
# So usado em REQUEST (CreateEnvironmentRequest.type) -- sem EnvironmentResponse real na API.
EnvironmentType = create_enum({"SANDBOX": 1, "PRODUCTION": 2})
# So usado em REQUEST (InviteMemberRequest.role/AssignRoleRequest.newRole) -- resposta e Grupo A.
MemberRoleRequest = create_enum({"OWNER": 1, "ADMIN": 2, "FINANCEIRO": 3, "LEITURA": 4})

# ---- Grupo A (string) ----
AccountStatus = create_enum({"ACTIVE": "Active", "FROZEN": "Frozen", "CLOSED": "Closed"})
ApplicationStatus = create_enum({"ACTIVE": "Active", "SUSPENDED": "Suspended", "ARCHIVED": "Archived"})
OrganizationStatus = create_enum({"ACTIVE": "Active", "SUSPENDED": "Suspended", "CLOSED": "Closed"})
MemberStatus = create_enum({"INVITED": "Invited", "ACTIVE": "Active", "SUSPENDED": "Suspended", "REMOVED": "Removed"})
WorkflowStatus = create_enum({"DRAFT": "Draft", "PUBLISHED": "Published", "DEPRECATED": "Deprecated"})
CatalogEntryStatus = create_enum({"ENABLED": "Enabled", "DISABLED": "Disabled"})
AssetNetworkStatus = create_enum({"ENABLED": "Enabled", "PAUSED": "Paused", "DISABLED": "Disabled"})
AssetKind = create_enum({"FIAT": "Fiat", "CRYPTO": "Crypto"})
