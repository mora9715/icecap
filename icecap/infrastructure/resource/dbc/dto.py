from dataclasses import dataclass, fields
from .enums import DBCFieldType


@dataclass(frozen=True, slots=True)
class DBCColumnDefinition:
    """Definition of a DBC column"""

    field_type: DBCFieldType
    array_size: int = 1
    is_primary_key: bool = False

    @classmethod
    def generate_default_definitions(cls, field_count: int) -> list["DBCColumnDefinition"]:
        columns = [DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)]

        for i in range(1, field_count):
            columns.append(DBCColumnDefinition(DBCFieldType.UINT))

        return columns


@dataclass(frozen=True, slots=True)
class DBCHeader:
    signature: str
    record_count: int
    field_count: int
    record_size: int
    string_block_size: int


@dataclass(frozen=True, slots=True)
class DBCRowWithDefinitions:
    METADATA_KEY = "definition"

    @classmethod
    def get_definitions(cls) -> list[DBCColumnDefinition]:
        definitions = []
        for field in fields(cls):
            definition: DBCColumnDefinition = field.metadata.get(cls.METADATA_KEY)  # type: ignore
            definitions.append(definition)

        return definitions
