from .interface import AgentClient

from .tcp.client import TCPAgentClient


def get_agent_client() -> AgentClient:
    return TCPAgentClient()
