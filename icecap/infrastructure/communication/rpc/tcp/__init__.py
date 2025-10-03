"""TCP client for icecap-agent communication."""

from .client import TCPAgentClient as AgentClient
from icecap.infrastructure.communication.rpc.exceptions import (
    AgentConnectionError,
    AgentError,
    AgentTimeoutError,
)

__all__ = [
    "AgentClient",
    "AgentError",
    "AgentConnectionError",
    "AgentTimeoutError",
]
