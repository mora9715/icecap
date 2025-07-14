from icecap.infrastructure.resource.dbc.dto import (
    DBCRowWithDefinitions,
    DBCColumnDefinition,
    DBCFieldType,
)
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MapRowWithDefinitions(DBCRowWithDefinitions):
    map_id: int = field(
        metadata={
            DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(
                DBCFieldType.INT, is_primary_key=True
            )
        }
    )
    directory: str = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.STRING)}
    )
    instance_type: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )
    flags: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )
    pvp: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )
    map_name: dict[str, str] = field(
        metadata={
            DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.LOCALIZED_STRING)
        }
    )
