import ctypes
from dataclasses import fields, is_dataclass
from typing import ClassVar, Type, Self

from icecap.infrastructure.memory_manager.interface import CTypeDataclass


class CTypeMixin(CTypeDataclass):
    """
    Mix-in for bridging a @dataclass <--> ctypes.Structure.

    Each dataclass field **must** provide `metadata={"ctype": <ctypes type>}`.
    The companion ctypes class is generated lazily the first time it is needed.
    """

    METADATA_KEY = f"{__package__}.ctype"

    _ctypes_cls: ClassVar[Type[ctypes.LittleEndianStructure]]

    @classmethod
    def _ensure_ctypes(cls) -> None:
        """Build and cache the ctypes.Structure that mirrors the dataclass."""
        if getattr(cls, "_ctypes_cls", None) is not None:
            return

        if not is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be a dataclass")

        c_fields: list[tuple[str, type[ctypes._SimpleCData]]] = []
        for f in fields(cls):
            ctype = f.metadata.get(cls.METADATA_KEY)
            if ctype is None:
                raise TypeError(f"Field '{f.name}' in {cls.__name__} is missing 'ctype' metadata")
            c_fields.append((f.name, ctype))

        # Dynamically create the mirror ctypes.Structure
        cls_name = f"{cls.__name__}CStruct"
        cls._ctypes_cls = type(
            cls_name,
            (ctypes.LittleEndianStructure,),
            {"_fields_": c_fields, "_pack_": 1},
        )

    def to_bytes(self) -> bytes:
        """Serialize the dataclass to its packed byte representation."""
        self.__class__._ensure_ctypes()
        c_obj = self._ctypes_cls()  # type: ignore
        for f in fields(self):  # type: ignore[arg-type]
            setattr(c_obj, f.name, getattr(self, f.name))
        size = ctypes.sizeof(c_obj)
        return ctypes.string_at(ctypes.byref(c_obj), size)

    @classmethod
    def from_bytes(cls, data: bytes, *, offset: int = 0) -> Self:
        """
        Build a dataclass instance from *data[offset:]*.
        Raises ValueError if the slice is too small.
        """
        cls._ensure_ctypes()
        size = ctypes.sizeof(cls._ctypes_cls)  # type: ignore
        if len(data) - offset < size:
            raise ValueError(f"Byte slice too small: need {size}, have {len(data) - offset}")

        c_obj = cls._ctypes_cls.from_buffer_copy(data[offset : offset + size])
        kwargs = {f.name: getattr(c_obj, f.name) for f in fields(cls)}  # type: ignore[arg-type]
        return cls(**kwargs)

    @classmethod
    def byte_size(cls) -> int:
        """Return the size in bytes of the corresponding C structure."""
        cls._ensure_ctypes()
        return ctypes.sizeof(cls._ctypes_cls)
