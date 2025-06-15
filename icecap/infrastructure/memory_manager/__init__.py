from icecap.constants import OS_SYSTEM
from .interface import MemoryManager

from .linux import LinuxMemoryManager


def get_memory_manager(pid: int) -> MemoryManager:
    if OS_SYSTEM == "Linux":
        return LinuxMemoryManager(pid)

    raise NotImplementedError(f"Memory manager for {OS_SYSTEM} is not implemented.")


__all__ = ["MemoryManager", "get_memory_manager"]
