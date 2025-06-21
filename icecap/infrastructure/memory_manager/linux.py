import struct
from typing import Type
from .interface import CStructTypeVar


class LinuxMemoryManager:
    pid: int

    def __init__(self, pid: int):
        self.pid = pid
        self._mem_path = f"/proc/{pid}/mem"
        # We'll open the file lazily when needed
        self._mem_file = None

    def _get_mem_file(self):
        """Get or create the memory file handle."""
        if self._mem_file is None:
            try:
                self._mem_file = open(self._mem_path, "rb")
            except (IOError, PermissionError) as e:
                raise IOError(f"Failed to open process memory: {e}")
        return self._mem_file

    def read_bytes(self, address: int, size: int) -> bytes:
        """Read a sequence of bytes from the given address.

        This method is cached for optimization of frequent reads.
        """
        mem_file = self._get_mem_file()
        try:
            mem_file.seek(address)
            data = mem_file.read(size)
            if len(data) < size:
                raise IOError(
                    f"Could only read {len(data)} bytes out of {size} at address {address}"
                )
            return data
        except (IOError, OSError) as e:
            raise IOError(f"Failed to read memory at address {address}: {e}")

    def read_short(self, address: int) -> int:
        """Read a signed 2 bytes integer from the given address."""
        data = self.read_bytes(address, 2)
        return struct.unpack("<h", data)[0]

    def read_ushort(self, address: int) -> int:
        """Read a signed 2 bytes integer from the given address."""
        data = self.read_bytes(address, 2)
        return struct.unpack("<H", data)[0]

    def read_uint(self, address: int) -> int:
        """Read an unsigned 4 bytes integer from the given address."""
        data = self.read_bytes(address, 4)
        return struct.unpack("<I", data)[0]

    def read_float(self, address: int) -> float:
        """Read a 4 bytes float from the given address."""
        data = self.read_bytes(address, 4)
        return struct.unpack("<f", data)[0]

    def read_ulonglong(self, address: int) -> int:
        """Read an unsigned 8 bytes integer from the given address."""
        data = self.read_bytes(address, 8)
        return struct.unpack("<Q", data)[0]

    def read_string(self, address: int, length: int) -> str:
        """Read a string from the given address with the specified length."""
        data = self.read_bytes(address, length)
        # Find null terminator if present
        null_pos = data.find(b"\0")
        if null_pos != -1:
            data = data[:null_pos]
        return data.decode("utf-8", errors="replace")

    def read_ctype_dataclass(self, address: int, dataclass: Type[CStructTypeVar]) -> CStructTypeVar:
        length = dataclass.byte_size()

        data = self.read_bytes(address, length)
        return dataclass.from_bytes(data)

    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        if self._mem_file is not None:
            try:
                self._mem_file.close()
            except Exception:
                pass  # Ignore errors during cleanup
