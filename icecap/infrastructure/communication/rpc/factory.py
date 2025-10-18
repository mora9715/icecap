import logging
from .interface import AgentClient

from .tcp.client import TCPAgentClient

logger = logging.getLogger(__name__)


def get_agent_client() -> AgentClient:
    logger.debug("Creating TCP agent client")
    return TCPAgentClient()
