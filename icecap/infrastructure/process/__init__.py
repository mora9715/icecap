from icecap.constants import OS_SYSTEM

from .linux import find_linux_wow_process_id


def get_wow_process_id() -> int:
    if OS_SYSTEM == "Linux":
        return find_linux_wow_process_id()
    raise NotImplementedError(
        f"Process ID retrieval for {OS_SYSTEM} is not implemented."
    )


__all__ = [
    "get_wow_process_id",
]
