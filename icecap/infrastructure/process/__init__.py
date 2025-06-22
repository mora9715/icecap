from icecap.constants import WOW_PROCESS_NAME
import psutil


def get_wow_process_id() -> int:
    """Factory function to get the game process ID based on the OS.

    Raises:
        ValueError: If the process is not found.
    """
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == WOW_PROCESS_NAME:
            return int(proc.info["pid"])

    raise ValueError("WoW process not found.")


__all__ = [
    "get_wow_process_id",
]
