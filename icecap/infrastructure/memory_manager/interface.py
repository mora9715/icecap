from typing import Type, TypeVar
from typing import Protocol


from typing import Self


class CTypeDataclass(Protocol):
    """
    Protocol for dataclasses that can be converted to and from ctypes.Structure.
    """

    def to_bytes(self) -> bytes:
        """Serialize the dataclass to its packed byte representation."""

    @classmethod
    def from_bytes(cls, data: bytes, *, offset: int = 0) -> Self:
        """
        Build a dataclass instance from *data[offset:]*.
        Raises ValueError if the slice is too small.
        """

    @classmethod
    def byte_size(cls) -> int:
        """Return the size in bytes of the dataclass when serialized."""


CStructTypeVar = TypeVar("CStructTypeVar", bound=CTypeDataclass)


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

    def read_ctype_dataclass(self, address: int, dataclass: Type[CStructTypeVar]) -> CStructTypeVar:
        """Read a C-typed structure dataclass from the given address."""
