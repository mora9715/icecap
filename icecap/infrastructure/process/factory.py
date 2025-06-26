from icecap.constants import WOW_PROCESS_NAME

from .manager import GameProcessManager as ConcreteGameProcessManager
from .interface import GameProcessManager


def get_game_process_manager(game_process_name: str = WOW_PROCESS_NAME) -> GameProcessManager:
    """Game process manager factory."""
    return ConcreteGameProcessManager(game_process_name)
