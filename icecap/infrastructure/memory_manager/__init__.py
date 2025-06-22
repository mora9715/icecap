from icecap.constants import OS_SYSTEM
from .interface import MemoryManager

from .linux import LinuxMemoryManager
from .windows import WindowsMemoryManager


def get_memory_manager(pid: int) -> MemoryManager:
    """Factory function to get the appropriate memory manager based on the OS.

    Raises:
        NotImplementedError: If the current OS is not supported
    """
    if OS_SYSTEM == "Linux":
        return LinuxMemoryManager(pid)
    elif OS_SYSTEM == "Windows":
        return WindowsMemoryManager(pid)

    raise NotImplementedError(f"Memory manager for {OS_SYSTEM} is not implemented.")


__all__ = ["MemoryManager", "get_memory_manager", "WindowsMemoryManager", "LinuxMemoryManager"]
