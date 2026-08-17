"""
RotateApiKeyRequest.overlap_window e um TimeSpan real do .NET (sem converter customizado
registrado -- confirmado via grep em OrganizationTenancy.Contracts), serializado no formato
constante "c" do System.Text.Json nativo desde .NET 6: [-][d.]hh:mm:ss[.fffffff]. Nunca usar o
formato ISO-8601 de timedelta aqui -- quebraria a chamada real.
"""

from __future__ import annotations

from datetime import timedelta


def format_dotnet_timespan(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    prefix = f"{days}." if days else ""
    return f"{prefix}{hours:02d}:{minutes:02d}:{seconds:02d}"
