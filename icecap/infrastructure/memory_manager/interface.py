from typing import Protocol


class MemoryManager(Protocol):
    pid: int

    def read_bytes(self, address: int, size: int) -> bytes:
        """Read a sequence of bytes from the given address."""

    def read_short(self, address: int) -> int:
        """Read a signed 2 bytes integer from the given address."""

    def read_uint(self, address: int) -> int:
        """Read an unsigned 4 bytes integer from the given address."""

    def read_float(self, address: int) -> float:
        """Read a 4 bytes float from the given address."""

    def read_ulonglong(self, address: int) -> int:
        """Read an unsigned 8 bytes integer from the given address."""

    def read_string(self, address: int, length: int) -> str:
        """Read a string from the given address with the specified length."""
