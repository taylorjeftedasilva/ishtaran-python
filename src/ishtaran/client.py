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
from .resources.api_keys_resource import ApiKeysResource
from .resources.applications_resource import ApplicationsResource
from .resources.asset_network_catalog_resource import AssetNetworkCatalogResource
from .resources.auth_resource import AuthResource
from .resources.deposits_resource import DepositsResource
from .resources.environments_resource import EnvironmentsResource
from .resources.event_types_resource import EventTypesResource
from .resources.events_resource import EventsResource
from .resources.ledger_resource import LedgerResource
from .resources.members_resource import MembersResource
from .resources.organizations_resource import OrganizationsResource
from .resources.refunds_resource import RefundsResource
from .resources.sandbox_resource import SandboxResource
from .resources.settlements_resource import SettlementsResource
from .resources.transactions_resource import TransactionsResource
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
    estimated_network_fee: Decimal
    estimated_recipient_amount: Decimal
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
    Fachada publica unica do SDK. Compoe Core (resources) e Easy Mode sobre o MESMO transporte
    HTTP -- Easy Mode nunca duplica logica de negocio, so combina chamadas Core (ver
    SDK_CAPABILITY_SPEC.md secao 5).
    """

    def __init__(self, raw_transport: HttpTransport, api_key: str | None, retry_policy: RetryPolicy) -> None:
        bearer_token_holder = BearerTokenHolder()
        authenticated: HttpTransport = AuthenticatingTransport(raw_transport, api_key, bearer_token_holder)
        transport: HttpTransport = RetryingTransport(authenticated, retry_policy)

        self.auth = AuthResource(transport, bearer_token_holder)
        self.organizations = OrganizationsResource(transport)
        self.applications = ApplicationsResource(transport)
        self.environments = EnvironmentsResource(transport)
        self.api_keys = ApiKeysResource(transport)
        self.members = MembersResource(transport)
        self.asset_network_catalog = AssetNetworkCatalogResource(transport)
        self.accounts = AccountsResource(transport)
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
        """Injeta um HttpTransport falso (sem rede), sem retry (ja tem suite propria dedicada)."""
        return IshtaranClient(transport, None, disabled_retry_policy())

    # ---- Easy Mode ----

    def get_balance(self, account_id: str, asset_network_id: str) -> BalanceResponse:
        """Passagem direta para ledger.get_balance() -- sem transformacao de negocio."""
        return self.ledger.get_balance(account_id, asset_network_id)

    def withdraw(
        self,
        organization_id: str,
        account_id: str,
        asset_network_id: str,
        amount: Decimal,
        destination_address: str,
        existing_destination_id: str | None = None,
    ) -> EasyWithdrawResult:
        """Compoe withdrawals.create_destination() (se necessario) + .request() -- nunca esconde a Network Fee."""
        destination_id = existing_destination_id
        if not destination_id:
            destination = self.withdrawals.create_destination(organization_id, destination_address, asset_network_id)
            destination_id = destination.withdrawal_destination_id
        result = self.withdrawals.request(organization_id, account_id, destination_id, asset_network_id, amount)
        return EasyWithdrawResult(
            withdrawal_id=result.withdrawal_id,
            requested_amount=result.amount,
            estimated_network_fee=result.estimated_network_fee,
            estimated_recipient_amount=result.estimated_recipient_amount,
            status=result.status,
        )

    def receive_payment(
        self, organization_id: str, application_id: str, payer_account_id: str, recipient_account_id: str, asset_network_id: str, amount: Decimal,
    ) -> EasyPaymentResult:
        """Compoe transactions.create() + deposits.create_payment_intent() + GET de acompanhamento."""
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
        """Polling seguro -- nunca infinito. Termina quando o Payment Intent sai de PENDING/PARTIALLY_PAID."""
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
        """Sem chamada HTTP -- calculo local."""
        return verify_webhook_signature(raw_body, signature_header, timestamp_header, endpoint_secret)
