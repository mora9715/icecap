import logging
from icecap.constants import WOW_PROCESS_NAME

from .manager import GameProcessManager as ConcreteGameProcessManager
from .interface import GameProcessManager

logger = logging.getLogger(__name__)


def get_game_process_manager(
    game_process_name: str = WOW_PROCESS_NAME,
) -> GameProcessManager:
    """Game process manager factory."""
    logger.debug(f"Creating GameProcessManager for process: {game_process_name}")
    return ConcreteGameProcessManager(game_process_name)
