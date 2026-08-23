from __future__ import annotations

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, get_request, post_request
from ..model.control_plane import (
    ApiKeyMetadataResponse,
    GenerateApiKeyResult,
    map_api_key_metadata_response,
    map_generate_api_key_result,
)


class EnvironmentsResource(ResourceSupport):
    """Control Plane -- Environments (2 real routes -- no real get/list route for Environment itself)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def list_api_keys(self, environment_id: str) -> list[ApiKeyMetadataResponse]:
        return self._execute_list(get_request(f"/v1/environments/{environment_id}/api-keys"), map_api_key_metadata_response)

    def generate_api_key(self, environment_id: str) -> GenerateApiKeyResult:
        """plain_text_key only appears in this response -- never retrievable afterward."""
        return self._execute(post_request(f"/v1/environments/{environment_id}/api-keys", "{}", False), map_generate_api_key_result)
