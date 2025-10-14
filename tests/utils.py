"""Test utilities and helpers for IceCap tests."""

from unittest.mock import Mock
from icecap.domain.dto import Position


class MockMemoryManager:
    """Mock implementation of MemoryManager for testing."""

    def __init__(self, memory_map: dict[int, bytes] | None = None):
        """Initialize with a memory map."""
        self.memory = memory_map or {}

    def read_uint(self, address: int) -> int:
        """Read an unsigned int from memory."""
        # Simulate access violation for very low addresses
        if address < 0x1000:
            raise OSError(f"Access violation at address {hex(address)}")
        data = self.memory.get(address, b"\x00\x00\x00\x00")
        return int.from_bytes(data[:4], byteorder="little", signed=False)

    def read_ulonglong(self, address: int) -> int:
        """Read an unsigned long long from memory."""
        data = self.memory.get(address, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        return int.from_bytes(data[:8], byteorder="little", signed=False)

    def read_float(self, address: int) -> float:
        """Read a float from memory."""
        import struct

        data = self.memory.get(address, b"\x00\x00\x00\x00")
        return struct.unpack("<f", data[:4])[0]

    def read_bytes(self, address: int, size: int) -> bytes:
        """Read bytes from memory."""
        # Build a contiguous buffer by checking each byte in the range
        result = bytearray(size)
        for i in range(size):
            byte_addr = address + i
            # Check if we have data at this address
            if byte_addr in self.memory:
                data = self.memory[byte_addr]
                # Handle case where data is stored as a multi-byte value
                if isinstance(data, bytes) and len(data) > 0:
                    result[i] = data[0]
                else:
                    result[i] = 0
            else:
                # Check if this address is within a larger stored block
                found = False
                for stored_addr, stored_data in self.memory.items():
                    if isinstance(
                        stored_data, bytes
                    ) and stored_addr <= byte_addr < stored_addr + len(stored_data):
                        result[i] = stored_data[byte_addr - stored_addr]
                        found = True
                        break
                if not found:
                    result[i] = 0
        return bytes(result)

    def read_string(self, address: int, length: int = 256) -> str:
        """Read a null-terminated string from memory."""
        data = self.memory.get(address, b"\x00" * length)
        # Find null terminator
        null_index = data.find(b"\x00")
        if null_index != -1:
            data = data[:null_index]
        return data.decode("utf-8", errors="ignore")

    def read_ctype_dataclass(self, address: int, dataclass_type):
        """Read a ctypes dataclass from memory."""
        # Get the byte size of the structure
        length = dataclass_type.byte_size()
        # Read the bytes from memory
        data = self.read_bytes(address, length)
        # Use the dataclass's from_bytes method to deserialize
        return dataclass_type.from_bytes(data)


class MemoryBuilder:
    """Builder pattern for creating mock memory layouts."""

    def __init__(self):
        """Initialize empty memory map."""
        self.memory_map: dict[int, bytes] = {}

    def with_uint_at(self, address: int, value: int):
        """Add an unsigned int at address."""
        self.memory_map[address] = value.to_bytes(4, byteorder="little", signed=False)
        return self

    def with_ulonglong_at(self, address: int, value: int):
        """Add an unsigned long long at address."""
        self.memory_map[address] = value.to_bytes(8, byteorder="little", signed=False)
        return self

    def with_float_at(self, address: int, value: float):
        """Add a float at address."""
        import struct

        self.memory_map[address] = struct.pack("<f", value)
        return self

    def with_bytes_at(self, address: int, data: bytes):
        """Add raw bytes at address."""
        self.memory_map[address] = data
        return self

    def build(self) -> MockMemoryManager:
        """Build and return the MockMemoryManager."""
        return MockMemoryManager(self.memory_map)


def assert_position_equal(pos1: Position, pos2: Position, tolerance: float = 0.01):
    """Assert two positions are equal within tolerance."""
    assert abs(pos1.x - pos2.x) < tolerance, f"X mismatch: {pos1.x} vs {pos2.x}"
    assert abs(pos1.y - pos2.y) < tolerance, f"Y mismatch: {pos1.y} vs {pos2.y}"
    assert abs(pos1.z - pos2.z) < tolerance, f"Z mismatch: {pos1.z} vs {pos2.z}"
    assert abs(pos1.rotation - pos2.rotation) < tolerance, (
        f"Rotation mismatch: {pos1.rotation} vs {pos2.rotation}"
    )


def create_mock_rpc_connection():
    """Factory for mock RPC connections."""
    mock = Mock()
    mock.send = Mock()
    mock.receive = Mock(return_value=b"")
    mock.close = Mock()
    mock.is_connected = Mock(return_value=True)
    return mock
