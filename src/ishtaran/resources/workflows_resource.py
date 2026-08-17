from __future__ import annotations

from typing import List

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.workflow import (
    ConditionInput,
    CreateRuleResult,
    CreateWorkflowResult,
    CreateWorkflowVersionResult,
    StateInput,
    TransitionInput,
    WorkflowResponse,
    WorkflowVersionResponse,
    map_create_rule_result,
    map_create_workflow_result,
    map_create_workflow_version_result,
    map_workflow_response,
    map_workflow_version_response,
)


class WorkflowsResource(ResourceSupport):
    """Data Plane -- WorkflowRules (7 rotas de Workflow/Version/Rule; Events/EventTypes em recursos proprios)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def create(self, organization_id: str, name: str) -> CreateWorkflowResult:
        return self._execute(post_request(f"/v1/organizations/{organization_id}/workflows", self._to_json({"name": name}), False), map_create_workflow_result)

    # Retorno anotado com typing.List (nao list[...]) -- dentro desta classe, o metodo `list`
    # abaixo shadowaria o builtin `list` em qualquer anotacao subsequente no corpo da classe
    # (bug real encontrado via mypy, nao apenas estilo).
    def list(self, organization_id: str) -> List[WorkflowResponse]:
        return self._execute_list(get_request(f"/v1/organizations/{organization_id}/workflows"), map_workflow_response)

    def get(self, workflow_id: str) -> WorkflowResponse:
        return self._execute(get_request(f"/v1/workflows/{workflow_id}"), map_workflow_response)

    def create_version(self, workflow_id: str, states: List[StateInput], transitions: List[TransitionInput]) -> CreateWorkflowVersionResult:
        body = self._to_json({"states": [s.to_dict() for s in states], "transitions": [t.to_dict() for t in transitions]})
        return self._execute(post_request(f"/v1/workflows/{workflow_id}/versions", body, False), map_create_workflow_version_result)

    def get_version(self, workflow_id: str, workflow_version_id: str) -> WorkflowVersionResponse:
        return self._execute(get_request(f"/v1/workflows/{workflow_id}/versions/{workflow_version_id}"), map_workflow_version_response)

    def publish_version(self, workflow_id: str, workflow_version_id: str) -> None:
        self._execute_no_content(post_request(f"/v1/workflows/{workflow_id}/versions/{workflow_version_id}/publish", None, False))

    def create_rule(
        self, workflow_id: str, workflow_version_id: str, from_state_id: str, to_state_id: str, event_type_id: str, conditions: List[ConditionInput],
    ) -> CreateRuleResult:
        body = self._to_json({
            "fromStateId": from_state_id, "toStateId": to_state_id, "eventTypeId": event_type_id,
            "conditions": [c.to_dict() for c in conditions],
        })
        return self._execute(post_request(f"/v1/workflows/{workflow_id}/versions/{workflow_version_id}/rules", body, False), map_create_rule_result)
