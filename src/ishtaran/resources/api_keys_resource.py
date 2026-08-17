from __future__ import annotations

from datetime import timedelta

from .resource_support import ResourceSupport
from ..http.types import HttpTransport, delete_request, post_request
from ..model.control_plane import RotateApiKeyResult, map_rotate_api_key_result
from ..util.dotnet_timespan import format_dotnet_timespan


class ApiKeysResource(ResourceSupport):
    """Control Plane -- ApiKeys (2 rotas reais)."""

    def __init__(self, transport: HttpTransport) -> None:
        super().__init__(transport)

    def revoke(self, api_key_id: str) -> None:
        self._execute_no_content(delete_request(f"/v1/api-keys/{api_key_id}"))

    def rotate(self, api_key_id: str, overlap_window: timedelta) -> RotateApiKeyResult:
        """
        overlap_window e enviado no formato real de TimeSpan do .NET (nao ISO-8601). plain_text_key
        da nova chave so aparece nesta resposta.
        """
        body = self._to_json({"overlapWindow": format_dotnet_timespan(overlap_window)})
        return self._execute(post_request(f"/v1/api-keys/{api_key_id}/rotate", body, False), map_rotate_api_key_result)
