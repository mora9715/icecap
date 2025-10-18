import logging
from icecap.constants import OS_SYSTEM
from .interface import MemoryManager

from .linux import LinuxMemoryManager
from .windows import WindowsMemoryManager

logger = logging.getLogger(__name__)


def get_memory_manager(pid: int) -> MemoryManager:
    """Factory function to get the appropriate memory manager based on the OS.

    Raises:
        NotImplementedError: If the current OS is not supported
    """
    logger.debug(f"Creating memory manager for OS: {OS_SYSTEM}, PID: {pid}")
    if OS_SYSTEM == "Linux":
        return LinuxMemoryManager(pid)
    elif OS_SYSTEM == "Windows":
        return WindowsMemoryManager(pid)

    logger.error(f"Memory manager for {OS_SYSTEM} is not implemented")
    raise NotImplementedError(f"Memory manager for {OS_SYSTEM} is not implemented.")
