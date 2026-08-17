from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .enum_factory import EnumValue
from .enums import ConditionOperator
from ..util.json_util import array_field, field, string_field, string_field_or_none


@dataclass(frozen=True)
class ConditionInput:
    field_name: str
    operator: EnumValue[int]
    expected_value: str

    def to_dict(self) -> dict[str, Any]:
        return {"field": self.field_name, "operator": self.operator, "expectedValue": self.expected_value}


@dataclass(frozen=True)
class ConditionResponse:
    field: str | None
    operator: EnumValue[int]
    expected_value: str | None


def _map_condition(raw: Any) -> ConditionResponse:
    return ConditionResponse(
        field=string_field_or_none(raw, "field"),
        operator=ConditionOperator.from_raw(int(field(raw, "operator"))),
        expected_value=string_field_or_none(raw, "expectedValue"),
    )


@dataclass(frozen=True)
class StateInput:
    id: str
    name: str
    is_initial: bool
    is_final: bool

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "isInitial": self.is_initial, "isFinal": self.is_final}


@dataclass(frozen=True)
class StateResponse:
    state_id: str
    name: str | None
    is_initial: bool
    is_final: bool


def _map_state(raw: Any) -> StateResponse:
    return StateResponse(
        state_id=string_field(raw, "stateId"),
        name=string_field_or_none(raw, "name"),
        is_initial=bool(field(raw, "isInitial")),
        is_final=bool(field(raw, "isFinal")),
    )


@dataclass(frozen=True)
class TransitionInput:
    id: str
    from_state_id: str
    to_state_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "fromStateId": self.from_state_id, "toStateId": self.to_state_id}


@dataclass(frozen=True)
class TransitionResponse:
    transition_id: str
    from_state_id: str
    to_state_id: str


def _map_transition(raw: Any) -> TransitionResponse:
    return TransitionResponse(
        transition_id=string_field(raw, "transitionId"),
        from_state_id=string_field(raw, "fromStateId"),
        to_state_id=string_field(raw, "toStateId"),
    )


@dataclass(frozen=True)
class RuleResponse:
    rule_id: str
    from_state_id: str
    to_state_id: str
    event_type_id: str
    conditions: list[ConditionResponse]


def _map_rule(raw: Any) -> RuleResponse:
    return RuleResponse(
        rule_id=string_field(raw, "ruleId"),
        from_state_id=string_field(raw, "fromStateId"),
        to_state_id=string_field(raw, "toStateId"),
        event_type_id=string_field(raw, "eventTypeId"),
        conditions=array_field(raw, "conditions", _map_condition),
    )


@dataclass(frozen=True)
class WorkflowResponse:
    workflow_id: str
    organization_id: str
    name: str | None
    status: str | None
    created_at: str
    version_ids: list[str]


def map_workflow_response(raw: Any) -> WorkflowResponse:
    return WorkflowResponse(
        workflow_id=string_field(raw, "workflowId"),
        organization_id=string_field(raw, "organizationId"),
        name=string_field_or_none(raw, "name"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
        version_ids=array_field(raw, "versionIds", str),
    )


@dataclass(frozen=True)
class WorkflowVersionResponse:
    workflow_version_id: str
    workflow_id: str
    status: str | None
    created_at: str
    published_at: str | None
    states: list[StateResponse]
    transitions: list[TransitionResponse]
    rules: list[RuleResponse]


def map_workflow_version_response(raw: Any) -> WorkflowVersionResponse:
    return WorkflowVersionResponse(
        workflow_version_id=string_field(raw, "workflowVersionId"),
        workflow_id=string_field(raw, "workflowId"),
        status=string_field_or_none(raw, "status"),
        created_at=string_field(raw, "createdAt"),
        published_at=string_field_or_none(raw, "publishedAt"),
        states=array_field(raw, "states", _map_state),
        transitions=array_field(raw, "transitions", _map_transition),
        rules=array_field(raw, "rules", _map_rule),
    )


@dataclass(frozen=True)
class EventTypeResponse:
    event_type_id: str
    organization_id: str | None
    name: str | None
    created_at: str


def map_event_type_response(raw: Any) -> EventTypeResponse:
    return EventTypeResponse(
        event_type_id=string_field(raw, "eventTypeId"),
        organization_id=string_field_or_none(raw, "organizationId"),
        name=string_field_or_none(raw, "name"),
        created_at=string_field(raw, "createdAt"),
    )


@dataclass(frozen=True)
class EventIngestionResult:
    event_id: str
    outcome: str | None
    rejection_reason: str | None
    from_state_id: str | None
    to_state_id: str | None
    rule_id: str | None


def map_event_ingestion_result(raw: Any) -> EventIngestionResult:
    return EventIngestionResult(
        event_id=string_field(raw, "eventId"),
        outcome=string_field_or_none(raw, "outcome"),
        rejection_reason=string_field_or_none(raw, "rejectionReason"),
        from_state_id=string_field_or_none(raw, "fromStateId"),
        to_state_id=string_field_or_none(raw, "toStateId"),
        rule_id=string_field_or_none(raw, "ruleId"),
    )


@dataclass(frozen=True)
class CreateWorkflowResult:
    workflow_id: str


def map_create_workflow_result(raw: Any) -> CreateWorkflowResult:
    return CreateWorkflowResult(workflow_id=string_field(raw, "workflowId"))


@dataclass(frozen=True)
class CreateWorkflowVersionResult:
    workflow_version_id: str


def map_create_workflow_version_result(raw: Any) -> CreateWorkflowVersionResult:
    return CreateWorkflowVersionResult(workflow_version_id=string_field(raw, "workflowVersionId"))


@dataclass(frozen=True)
class CreateRuleResult:
    rule_id: str


def map_create_rule_result(raw: Any) -> CreateRuleResult:
    return CreateRuleResult(rule_id=string_field(raw, "ruleId"))


@dataclass(frozen=True)
class CreateEventTypeResult:
    event_type_id: str


def map_create_event_type_result(raw: Any) -> CreateEventTypeResult:
    return CreateEventTypeResult(event_type_id=string_field(raw, "eventTypeId"))
