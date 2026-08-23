"""
See SDK_CAPABILITY_SPEC.md section 11.3 for the complete name-value table extracted literally from
the real C# enums. Group B = raw integer in JSON; Group A = human-readable string.

Typing note: EnumRegistry uses dynamic setattr to expose STATUS.COMPLETED etc.; this is not
100% friendly to mypy --strict static checking (dynamic attributes are not statically
inferred) -- known and documented limitation, see PYTHON_SDK_CHECKPOINT.md.
"""

from __future__ import annotations

from .enum_factory import create_enum

# ---- Group B (integer) ----
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
# Used only in REQUEST (CreateEnvironmentRequest.type) -- no real EnvironmentResponse in the API.
EnvironmentType = create_enum({"SANDBOX": 1, "PRODUCTION": 2})
# ExecutionCustody.Contracts.Enums.DerivationScheme (SPEC-021, checkpoint 10) -- wire-format only, Group B.
DerivationScheme = create_enum({"TRON_BIP44_HARDENED_ACCOUNT": 1})
# Used only in REQUEST (InviteMemberRequest.role/AssignRoleRequest.newRole) -- response is Group A.
# NOTE: FINANCE/READ_ONLY are local Python identifiers only; only the integer raw_value travels
# over the wire (see enum_factory.py), so translating these symbol names is safe. The backend's
# MemberRole enum (IdentityAccess.Domain.Enums.MemberRole) serializes the RESPONSE-side role by
# name as the literal "Financeiro"/"Leitura" strings, but this SDK models the response `role`
# field as a plain `str` (see model/control_plane.py, model/data_plane.py,
# model/execution_custody.py) with no mirroring enum symbol, so there is no wire-value gap here.
MemberRoleRequest = create_enum({"OWNER": 1, "ADMIN": 2, "FINANCE": 3, "READ_ONLY": 4})

# ---- Group A (string) ----
AccountStatus = create_enum({"ACTIVE": "Active", "FROZEN": "Frozen", "CLOSED": "Closed"})
ApplicationStatus = create_enum({"ACTIVE": "Active", "SUSPENDED": "Suspended", "ARCHIVED": "Archived"})
OrganizationStatus = create_enum({"ACTIVE": "Active", "SUSPENDED": "Suspended", "CLOSED": "Closed"})
MemberStatus = create_enum({"INVITED": "Invited", "ACTIVE": "Active", "SUSPENDED": "Suspended", "REMOVED": "Removed"})
WorkflowStatus = create_enum({"DRAFT": "Draft", "PUBLISHED": "Published", "DEPRECATED": "Deprecated"})
CatalogEntryStatus = create_enum({"ENABLED": "Enabled", "DISABLED": "Disabled"})
AssetNetworkStatus = create_enum({"ENABLED": "Enabled", "PAUSED": "Paused", "DISABLED": "Disabled"})
AssetKind = create_enum({"FIAT": "Fiat", "CRYPTO": "Crypto"})
