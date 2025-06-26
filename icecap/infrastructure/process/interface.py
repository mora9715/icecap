from typing import Callable, Protocol


GamePIDGetter = Callable[[], int | None]


class GameProcessManager(Protocol):
    """The service encapsulates interaction with the OS process layer."""

    def get_process_id(self) -> int | None:
        """Locate the game process ID."""

    def pid_changed_since_last_call(self) -> bool:
        """Check if the game process ID changed since the last call.

        This is used to detect when the game process has been recreated.
        """
