# Working with DBC Files in Icecap

This guide will help you understand how to work with DBC (Database Container) files, which are database files used by Blizzard Entertainment games like World of Warcraft to store various game information.

## What are DBC Files?

DBC (Database Container) is a proprietary database format developed by Blizzard Entertainment for their games. These files contain structured data about various game elements such as maps, items, spells, creatures, and more. Understanding how to work with DBC files allows you to access and analyze game data for research or tool development.

## Basic Usage

### Opening a DBC File

To work with a DBC file, you first need to open it using the `DBCFile` class and provide a row prototype that defines the structure of the records:

```python
from icecap.infrastructure.resource import DBCFile, MapRowWithDefinitions

# Open a DBC file using a predefined row prototype
dbc_file = DBCFile("path/to/your/Map.dbc", MapRowWithDefinitions)
```

### Reading Records from a DBC File

You can get all records from the DBC file:

```python
# Get all records from the DBC file
records = dbc_file.get_records()

# Print the first 5 records
for record in records[:5]:
    print(f"Map ID: {record.map_id}, Directory: {record.directory}, Instance Type: {record.instance_type}")
```

### Getting File Header Information

You can access the header information of the DBC file:

```python
# Get the DBC file header
header = dbc_file.get_header()

# Print header information
print(f"Signature: {header.signature}")
print(f"Record Count: {header.record_count}")
print(f"Field Count: {header.field_count}")
print(f"Record Size: {header.record_size} bytes")
print(f"String Block Size: {header.string_block_size} bytes")
```

## Advanced Usage

### Creating Custom Row Prototypes

For each DBC file type, you need a row prototype that defines the structure of the records. Icecap provides `MapRowWithDefinitions` for Map.dbc, but you can create your own for other DBC files:

```python
from dataclasses import dataclass, field
from icecap.infrastructure.resource.dbc.dto import DBCRowWithDefinitions, DBCColumnDefinition
from icecap.infrastructure.resource.dbc.enums import DBCFieldType

@dataclass(frozen=True, slots=True)
class SpellRowWithDefinitions(DBCRowWithDefinitions):
    spell_id: int = field(
        metadata={
            DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(
                DBCFieldType.INT, is_primary_key=True
            )
        }
    )
    name: str = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.STRING)}
    )
    description: str = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.STRING)}
    )
    mana_cost: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )
    # Add more fields as needed
```

### Working with Different Field Types

DBC files support various field types:

```python
from icecap.infrastructure.resource.dbc.enums import DBCFieldType

# Available field types:
# DBCFieldType.INT - 32-bit signed integer
# DBCFieldType.UINT - 32-bit unsigned integer
# DBCFieldType.FLOAT - 32-bit floating point
# DBCFieldType.STRING - String reference
# DBCFieldType.BOOLEAN - Boolean (0 or 1)
# DBCFieldType.LOCALIZED_STRING - Multiple string references for different locales
```

### Working with Localized Strings

Some DBC files contain localized strings for different languages. You can define a field as a localized string and access the values for different locales:

```python
from dataclasses import dataclass, field
from icecap.infrastructure.resource.dbc.dto import DBCRowWithDefinitions, DBCColumnDefinition
from icecap.infrastructure.resource.dbc.enums import DBCFieldType, DBCLocale

@dataclass(frozen=True, slots=True)
class ItemRowWithDefinitions(DBCRowWithDefinitions):
    item_id: int = field(
        metadata={
            DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(
                DBCFieldType.INT, is_primary_key=True
            )
        }
    )
    name: dict = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.LOCALIZED_STRING)}
    )
    # Add more fields as needed

# Open the DBC file
dbc_file = DBCFile("path/to/your/Item.dbc", ItemRowWithDefinitions)

# Get all records
records = dbc_file.get_records()

# Access localized strings
for record in records[:5]:
    print(f"Item ID: {record.item_id}")
    print(f"Name (English): {record.name[DBCLocale.enUS]}")
    print(f"Name (German): {record.name[DBCLocale.deDE]}")
    print(f"Name (French): {record.name[DBCLocale.frFR]}")
    print()
```

### Working with Array Fields

Some DBC fields are arrays. You can define a field as an array by setting the `array_size` parameter:

```python
from dataclasses import dataclass, field
from icecap.infrastructure.resource.dbc.dto import DBCRowWithDefinitions, DBCColumnDefinition
from icecap.infrastructure.resource.dbc.enums import DBCFieldType

@dataclass(frozen=True, slots=True)
class SpellEffectRowWithDefinitions(DBCRowWithDefinitions):
    spell_id: int = field(
        metadata={
            DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(
                DBCFieldType.INT, is_primary_key=True
            )
        }
    )
    effect_values: list = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT, array_size=3)}
    )
    # Add more fields as needed
```

## Complete Examples

### Example 1: Reading Map.dbc

Here's a complete example that demonstrates how to open the Map.dbc file and read its contents:

```python
from icecap.infrastructure.resource import DBCFile, MapRowWithDefinitions

# Open the Map.dbc file
dbc_file = DBCFile("path/to/your/Map.dbc", MapRowWithDefinitions)

# Get the header information
header = dbc_file.get_header()
print(f"Map.dbc contains {header.record_count} maps")

# Get all records
maps = dbc_file.get_records()

# Print information about each map
for map_record in maps:
    print(f"Map ID: {map_record.map_id}")
    print(f"Directory: {map_record.directory}")
    print(f"Instance Type: {map_record.instance_type}")
    print()

# Find a specific map by ID
azeroth_map = next((m for m in maps if m.map_id == 0), None)
if azeroth_map:
    print(f"Found Azeroth map: {azeroth_map.directory}")
```

### Example 2: Creating a Custom Row Prototype for a New DBC File

Here's an example of creating a custom row prototype for a DBC file that isn't predefined in Icecap:

```python
from dataclasses import dataclass, field
from icecap.infrastructure.resource import DBCFile
from icecap.infrastructure.resource.dbc.dto import DBCRowWithDefinitions, DBCColumnDefinition
from icecap.infrastructure.resource.dbc.enums import DBCFieldType

# Define a row prototype for AreaTable.dbc
@dataclass(frozen=True, slots=True)
class AreaTableRowWithDefinitions(DBCRowWithDefinitions):
    area_id: int = field(
        metadata={
            DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(
                DBCFieldType.INT, is_primary_key=True
            )
        }
    )
    map_id: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )
    parent_area_id: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )
    area_name: str = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.STRING)}
    )
    flags: int = field(
        metadata={DBCRowWithDefinitions.METADATA_KEY: DBCColumnDefinition(DBCFieldType.INT)}
    )

# Open the AreaTable.dbc file
dbc_file = DBCFile("path/to/your/AreaTable.dbc", AreaTableRowWithDefinitions)

# Get all records
areas = dbc_file.get_records()

# Print information about each area
for area in areas[:10]:  # Print first 10 areas
    print(f"Area ID: {area.area_id}")
    print(f"Map ID: {area.map_id}")
    print(f"Parent Area ID: {area.parent_area_id}")
    print(f"Area Name: {area.area_name}")
    print(f"Flags: {area.flags}")
    print()

# Find all areas in a specific map
map_id = 1  # Eastern Kingdoms
eastern_kingdoms_areas = [area for area in areas if area.map_id == map_id]
print(f"Found {len(eastern_kingdoms_areas)} areas in Eastern Kingdoms")
```

## Next Steps

Now that you understand how to work with DBC files, you can:

- Extract game data for analysis
- Create tools to browse and analyze DBC contents
- Build custom applications that use WoW game data
- Combine DBC data with other game resources like MPQ archives

For more information about the DBC format and available DBC files in World of Warcraft, check out the [WoWDev Wiki](https://wowdev.wiki/DBC).
