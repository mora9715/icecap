import logging
import psutil
from icecap.constants import WOW_PROCESS_NAME

logger = logging.getLogger(__name__)


class GameProcessManager:
    def __init__(self, game_process_name: str = WOW_PROCESS_NAME):
        self.game_process_name = game_process_name

        self.last_known_process_id: int | None = None
        logger.debug(f"GameProcessManager initialized for process: {game_process_name}")

    def get_process_id(self) -> int | None:
        """Get the PID of the game process."""
        # Try the last known PID first. ~100x faster
        # Edge case when a process was recreated with the same PID is accepted.
        if self.last_known_process_id and psutil.pid_exists(self.last_known_process_id):
            logger.debug(f"Using cached process ID: {self.last_known_process_id}")
            return self.last_known_process_id

        logger.debug(f"Searching for process: {self.game_process_name}")
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] == WOW_PROCESS_NAME:
                self.last_known_process_id = int(proc.info["pid"])
                logger.info(
                    f"Found game process: {self.game_process_name} (PID: "
                    f"{self.last_known_process_id})"
                )
                return self.last_known_process_id

        logger.warning(f"Game process not found: {self.game_process_name}")
        return None

    def pid_changed_since_last_call(self) -> bool:
        last_known_process_id = self.last_known_process_id
        current_process_id = self.get_process_id()
        changed = current_process_id != last_known_process_id
        if changed:
            logger.info(f"Process ID changed: {last_known_process_id} -> {current_process_id}")
        return changed
