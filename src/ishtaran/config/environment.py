"""Ambientes oficiais do projeto (CLAUDE.md): Local, Sandbox, Production."""

from enum import Enum


class Environment(str, Enum):
    LOCAL = "local"
    SANDBOX = "sandbox"
    PRODUCTION = "production"
