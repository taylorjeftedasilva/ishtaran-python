from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .auth.bearer_token_holder import BearerTokenHolder
from .config.client_config import IshtaranClientConfig, build_client_config
from .config.environment import Environment
from .config.retry_policy import RetryPolicy, disabled_retry_policy
from .http.authenticating_transport import AuthenticatingTransport
from .http.httpx_transport import HttpxTransport
from .http.logging_transport import LoggingTransport
from .http.retrying_transport import RetryingTransport
from .http.types import HttpTransport
from .model.data_plane import BalanceResponse, ParticipantInput, WithdrawalResponse
from .model.enum_factory import EnumValue
from .model.enums import PaymentIntentStatus
from .resources.accounts_resource import AccountsResource
from .resources.account_holders_resource import AccountHoldersResource
from .resources.api_keys_resource import ApiKeysResource
from .resources.applications_resource import ApplicationsResource
from .resources.asset_network_catalog_resource import AssetNetworkCatalogResource
from .resources.auth_resource import AuthResource
from .resources.deposits_resource import DepositsResource
from .resources.environments_resource import EnvironmentsResource
from .resources.event_types_resource import EventTypesResource
from .resources.events_resource import EventsResource
from .resources.execution_destinations_resource import ExecutionDestinationsResource
from .resources.execution_sources_resource import ExecutionSourcesResource
from .resources.ledger_resource import LedgerResource
from .resources.members_resource import MembersResource
from .resources.network_cost_payer_accounts_resource import NetworkCostPayerAccountsResource
from .resources.network_execution_resource import NetworkExecutionResource
from .resources.organizations_resource import OrganizationsResource
from .resources.payout_resource import PayoutResource
from .resources.refunds_resource import RefundsResource
from .resources.sandbox_resource import SandboxResource
from .resources.settlements_resource import SettlementsResource
from .resources.transactions_resource import TransactionsResource
from .resources.signing_requests_resource import SigningRequestsResource
from .resources.wallets_resource import WalletsResource
from .resources.webhook_deliveries_resource import WebhookDeliveriesResource
from .resources.webhook_endpoints_resource import WebhookEndpointsResource
from .resources.withdrawals_resource import WithdrawalsResource
from .resources.workflows_resource import WorkflowsResource
from .util.polling import poll_until
from .webhook.webhook_signature_verifier import verify_webhook_signature


@dataclass(frozen=True)
class EasyWithdrawResult:
    withdrawal_id: str
    requested_amount: Decimal
    estimated_network_fee: Decimal | None
    """Deprecated -- vestigial under SelfCustody, always None. Use network_execution_cost."""
    estimated_recipient_amount: Decimal
    network_execution_cost: Decimal | None
    status: EnumValue[int]


@dataclass(frozen=True)
class EasyPaymentResult:
    transaction_id: str
    payment_intent_id: str
    transaction_status: EnumValue[int]
    payment_intent_status: EnumValue[int]
    deposit_address: str | None
    amount: Decimal


class IshtaranClient:
    """
    The SDK's single public facade. Composes Core (resources) and Easy Mode over the SAME HTTP
    transport -- Easy Mode never duplicates business logic, it only combines Core calls (see
    SDK_CAPABILITY_SPEC.md section 5).
    """

    def __init__(self, raw_transport: HttpTransport, api_key: str | None, retry_policy: RetryPolicy) -> None:
        bearer_token_holder = BearerTokenHolder()
        authenticated: HttpTransport = AuthenticatingTransport(raw_transport, api_key, bearer_token_holder)
        transport: HttpTransport = RetryingTransport(authenticated, retry_policy)

        # DEC-032 -- own transport for AccountHolder, never the Organization's api_key nor the
        # Member bearer_token_holder above: complete domain separation between the two
        # principals, the same reasoning as AccountHolderJwtScheme never sharing a key with
        # MemberJwtScheme on the backend.
        account_holder_token_holder = BearerTokenHolder()
        account_holder_authenticated: HttpTransport = AuthenticatingTransport(raw_transport, None, account_holder_token_holder)
        account_holder_transport: HttpTransport = RetryingTransport(account_holder_authenticated, retry_policy)

        self.auth = AuthResource(transport, bearer_token_holder)
        self.organizations = OrganizationsResource(transport)
        self.applications = ApplicationsResource(transport)
        self.environments = EnvironmentsResource(transport)
        self.api_keys = ApiKeysResource(transport)
        self.members = MembersResource(transport)
        self.asset_network_catalog = AssetNetworkCatalogResource(transport)
        self.accounts = AccountsResource(transport)
        self.account_holders = AccountHoldersResource(account_holder_transport, account_holder_token_holder)
        self.transactions = TransactionsResource(transport)
        self.deposits = DepositsResource(transport)
        self.ledger = LedgerResource(transport)
        self.settlements = SettlementsResource(transport)
        self.refunds = RefundsResource(transport)
        self.withdrawals = WithdrawalsResource(transport)
        self.workflows = WorkflowsResource(transport)
        self.event_types = EventTypesResource(transport)
        self.events = EventsResource(transport)
        self.sandbox = SandboxResource(transport)
        self.webhook_endpoints = WebhookEndpointsResource(transport)
        self.webhook_deliveries = WebhookDeliveriesResource(transport)
        # SPEC-018/021, checkpoint 10 -- only the extended PUBLIC key travels through this client (INV-SC-01).
        self.wallets = WalletsResource(transport)
        # SPEC-019/020/021, checkpoint 10 -- the SDK signs locally (wallet.signer) and submits it back.
        self.signing_requests = SigningRequestsResource(transport)
        # DEC-037 -- a beneficiary's registered on-chain receiving address per AssetNetwork, required before a Settlement can execute under SelfCustody.
        self.execution_destinations = ExecutionDestinationsResource(transport)
        self.execution_sources = ExecutionSourcesResource(transport)
        self.network_cost_payer_accounts = NetworkCostPayerAccountsResource(transport)
        self.network_execution = NetworkExecutionResource(transport)
        self.payout = PayoutResource(transport)

    @staticmethod
    def create(
        *,
        api_key: str | None = None,
        environment: Environment = Environment.LOCAL,
        base_url: str | None = None,
        connect_timeout_seconds: float = 5.0,
        request_timeout_seconds: float = 30.0,
        retry_policy: RetryPolicy | None = None,
        user_agent: str | None = None,
        enable_logging: bool = False,
        allow_insecure_tls_for_local_development: bool = False,
    ) -> "IshtaranClient":
        config = build_client_config(
            api_key=api_key, environment=environment, base_url=base_url,
            connect_timeout_seconds=connect_timeout_seconds, request_timeout_seconds=request_timeout_seconds,
            retry_policy=retry_policy, user_agent=user_agent, enable_logging=enable_logging,
            allow_insecure_tls_for_local_development=allow_insecure_tls_for_local_development,
        )
        transport: HttpTransport = HttpxTransport(config)
        if config.logging_enabled:
            transport = LoggingTransport(transport)
        return IshtaranClient(transport, config.api_key, config.retry_policy)

    @staticmethod
    def for_testing(transport: HttpTransport) -> "IshtaranClient":
        """Injects a fake HttpTransport (no network), no retry (already has its own dedicated suite)."""
        return IshtaranClient(transport, None, disabled_retry_policy())

    # ---- Easy Mode ----

    def get_balance(self, account_id: str, asset_network_id: str) -> BalanceResponse:
        """Direct pass-through to ledger.get_balance() -- no business transformation."""
        return self.ledger.get_balance(account_id, asset_network_id)

    def withdraw(
        self,
        organization_id: str,
        environment_id: str,
        account_id: str,
        asset_network_id: str,
        amount: Decimal,
        destination_address: str,
        existing_destination_id: str | None = None,
    ) -> EasyWithdrawResult:
        """Composes withdrawals.create_destination() (if needed) + .request() -- never hides the Network Fee."""
        destination_id = existing_destination_id
        if not destination_id:
            destination = self.withdrawals.create_destination(organization_id, destination_address, asset_network_id)
            destination_id = destination.withdrawal_destination_id
        result = self.withdrawals.request(organization_id, environment_id, account_id, destination_id, asset_network_id, amount)
        return EasyWithdrawResult(
            withdrawal_id=result.withdrawal_id,
            requested_amount=result.amount,
            estimated_network_fee=result.estimated_network_fee,
            estimated_recipient_amount=result.estimated_recipient_amount,
            network_execution_cost=result.network_execution_cost,
            status=result.status,
        )

    def receive_payment(
        self, organization_id: str, application_id: str, payer_account_id: str, recipient_account_id: str, asset_network_id: str, amount: Decimal,
    ) -> EasyPaymentResult:
        """Composes transactions.create() + deposits.create_payment_intent() + a follow-up GET."""
        participants = [
            ParticipantInput(account_id=payer_account_id, role="payer", is_payer=True),
            ParticipantInput(account_id=recipient_account_id, role="recipient", is_payer=False),
        ]
        created_transaction = self.transactions.create(organization_id, application_id, None, asset_network_id, amount, participants)
        created_payment_intent = self.deposits.create_payment_intent(organization_id, created_transaction.transaction_id, asset_network_id, amount)
        return self.get_payment(created_transaction.transaction_id, created_payment_intent.payment_intent_id)

    def get_payment(self, transaction_id: str, payment_intent_id: str) -> EasyPaymentResult:
        transaction = self.transactions.get(transaction_id)
        payment_intent = self.deposits.get_payment_intent(payment_intent_id)
        return EasyPaymentResult(
            transaction_id=transaction_id,
            payment_intent_id=payment_intent_id,
            transaction_status=transaction.status,
            payment_intent_status=payment_intent.status,
            deposit_address=payment_intent.deposit_address,
            amount=transaction.amount,
        )

    def wait_for_payment(self, transaction_id: str, payment_intent_id: str, timeout_seconds: float, poll_interval_seconds: float) -> EasyPaymentResult:
        """Safe polling -- never infinite. Ends when the Payment Intent leaves PENDING/PARTIALLY_PAID."""
        pending = PaymentIntentStatus.PENDING.raw_value  # type: ignore[attr-defined]
        partially_paid = PaymentIntentStatus.PARTIALLY_PAID.raw_value  # type: ignore[attr-defined]
        return poll_until(
            lambda: self.get_payment(transaction_id, payment_intent_id),
            lambda r: r.payment_intent_status.raw_value not in (pending, partially_paid),
            timeout_seconds,
            poll_interval_seconds,
            f"payment_intent_id={payment_intent_id}",
        )

    def verify_webhook_signature(self, raw_body: str, signature_header: str, timestamp_header: str, endpoint_secret: str) -> bool:
        """No HTTP call -- local computation."""
        return verify_webhook_signature(raw_body, signature_header, timestamp_header, endpoint_secret)
