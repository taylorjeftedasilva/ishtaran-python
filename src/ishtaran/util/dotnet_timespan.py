"""
RotateApiKeyRequest.overlap_window is a real .NET TimeSpan (no custom converter
registered -- confirmed via grep in OrganizationTenancy.Contracts), serialized in the constant
"c" format used natively by System.Text.Json since .NET 6: [-][d.]hh:mm:ss[.fffffff]. Never use
timedelta's ISO-8601 format here -- it would break the real call.
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
