"""Exceptions for the TCP agent client."""


class AgentError(Exception):
    """Base exception for agent client errors."""

    pass


class AgentConnectionError(AgentError):
    """Raised when connection to an agent fails or is lost."""

    pass


class AgentTimeoutError(AgentError):
    """Raised when waiting for a response times out."""

    pass
