"""Tests for DBC database parsing."""

import struct
import pytest
from io import BytesIO
from dataclasses import dataclass, field
from icecap.infrastructure.resource.dbc.database import DBCFile
from icecap.infrastructure.resource.dbc.dto import DBCColumnDefinition, DBCRowWithDefinitions
from icecap.infrastructure.resource.dbc.enums import DBCFieldType, DBCLocale


def create_dbc_file(
    record_count: int,
    field_count: int,
    record_size: int,
    records_data: bytes,
    string_block: bytes,
) -> BytesIO:
    """Helper function to create a DBC file in memory."""
    header = struct.pack(
        "<4s4I",
        b"WDBC",
        record_count,
        field_count,
        record_size,
        len(string_block),
    )

    file_data = header + records_data + string_block
    return BytesIO(file_data)


class TestDBCFileHeader:
    """Test DBC file header parsing."""

    def test_parse_valid_header(self):
        """Test parsing a valid DBC header."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        dbc_file = create_dbc_file(
            record_count=10, field_count=1, record_size=4, records_data=b"", string_block=b""
        )

        dbc = DBCFile(dbc_file, TestRow)
        header = dbc.get_header()

        assert header.signature == "WDBC"
        assert header.record_count == 10
        assert header.field_count == 1
        assert header.record_size == 4
        assert header.string_block_size == 0

    def test_parse_invalid_signature(self):
        """Test parsing an invalid DBC signature."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        # Create file with invalid signature
        header = struct.pack("<4s4I", b"INVALID", 0, 1, 4, 0)
        dbc_file = BytesIO(header)

        dbc = DBCFile(dbc_file, TestRow)

        with pytest.raises(ValueError, match="Invalid DBC file signature"):
            dbc.get_header()

    def test_header_caching(self):
        """Test that header is cached after first read."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        dbc_file = create_dbc_file(
            record_count=5, field_count=1, record_size=4, records_data=b"", string_block=b""
        )

        dbc = DBCFile(dbc_file, TestRow)

        header1 = dbc.get_header()
        header2 = dbc.get_header()

        # Should return the same cached object
        assert header1 is header2


class TestDBCFileRecordParsing:
    """Test DBC file record parsing."""

    def test_parse_single_uint_record(self):
        """Test parsing a single UINT record."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        records_data = struct.pack("<I", 12345)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].id == 12345

    def test_parse_single_int_record(self):
        """Test parsing a single INT record."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            value: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.INT)})

        records_data = struct.pack("<i", -12345)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].value == -12345

    def test_parse_single_float_record(self):
        """Test parsing a single FLOAT record."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            value: float = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT)})

        records_data = struct.pack("<f", 3.14159)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert abs(records[0].value - 3.14159) < 0.0001

    def test_parse_single_boolean_record(self):
        """Test parsing a single BOOLEAN record."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            is_active: bool = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.BOOLEAN)}
            )

        records_data = struct.pack("<I", 1)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].is_active is True

    def test_parse_boolean_false_record(self):
        """Test parsing a BOOLEAN record with false value."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            is_active: bool = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.BOOLEAN)}
            )

        records_data = struct.pack("<I", 0)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].is_active is False

    def test_parse_string_record(self):
        """Test parsing a STRING record."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            name: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})

        # String offset points to position 1 in string block (0 is reserved for empty)
        records_data = struct.pack("<I", 1)
        string_block = b"\x00Test String\x00"  # Empty string at 0, actual string at 1

        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=string_block,
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].name == "Test String"

    def test_parse_empty_string_record(self):
        """Test parsing an empty STRING record."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            name: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})

        # Offset 0 means empty string
        records_data = struct.pack("<I", 0)
        string_block = b"\x00"

        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=string_block,
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].name == ""

    def test_parse_multiple_records(self):
        """Test parsing multiple records."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        records_data = struct.pack("<III", 1, 2, 3)

        dbc_file = create_dbc_file(
            record_count=3,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 3
        assert records[0].id == 1
        assert records[1].id == 2
        assert records[2].id == 3

    def test_parse_multiple_fields(self):
        """Test parsing records with multiple fields."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            value: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.INT)})
            ratio: float = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT)})

        records_data = struct.pack("<Iif", 1, -100, 2.5)

        dbc_file = create_dbc_file(
            record_count=1,
            field_count=3,
            record_size=12,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].id == 1
        assert records[0].value == -100
        assert abs(records[0].ratio - 2.5) < 0.0001

    def test_parse_array_field(self):
        """Test parsing records with array fields."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            values: list = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.INT, array_size=3)}
            )

        records_data = struct.pack("<Iiii", 1, 10, 20, 30)

        dbc_file = create_dbc_file(
            record_count=1,
            field_count=4,
            record_size=16,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].id == 1
        assert records[0].values == [10, 20, 30]

    def test_parse_localized_string(self):
        """Test parsing LOCALIZED_STRING field."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            name: dict = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.LOCALIZED_STRING)}
            )

        # Create offsets for each locale (9 locales)
        # Point enUS to offset 1, others to 0 (empty string)
        offsets = [1] + [0] * 8  # enUS at 1, others at 0 (empty)
        records_data = struct.pack("<" + "I" * 9, *offsets)
        string_block = b"\x00Hello World\x00"  # Empty at 0, "Hello World" at 1

        dbc_file = create_dbc_file(
            record_count=1,
            field_count=9,
            record_size=36,
            records_data=records_data,
            string_block=string_block,
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].name[DBCLocale.enUS] == "Hello World"
        assert records[0].name[DBCLocale.koKR] == ""

    def test_records_caching(self):
        """Test that records are cached after first read."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        records_data = struct.pack("<I", 1)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)

        records1 = dbc.get_records()
        records2 = dbc.get_records()

        # Should return the same cached list
        assert records1 is records2


class TestDBCFileStringBlock:
    """Test DBC file string block handling."""

    def test_multiple_strings_in_block(self):
        """Test parsing multiple strings from string block."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            name1: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})
            name2: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})

        # Two records pointing to different strings
        # String block: \x00 (empty at 0), "First\x00" (at 1), "Second\x00" (at 7)
        records_data = struct.pack("<II", 1, 7) + struct.pack("<II", 7, 7)
        string_block = b"\x00First\x00Second\x00"

        dbc_file = create_dbc_file(
            record_count=2,
            field_count=2,
            record_size=8,
            records_data=records_data,
            string_block=string_block,
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 2
        assert records[0].name1 == "First"
        assert records[0].name2 == "Second"
        assert records[1].name1 == "Second"
        assert records[1].name2 == "Second"

    def test_utf8_string_parsing(self):
        """Test parsing UTF-8 strings."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            name: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})

        records_data = struct.pack("<I", 1)  # Point to offset 1
        string_block = b"\x00" + "Тест\x00".encode("utf-8")  # Empty at 0, UTF-8 string at 1

        dbc_file = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=string_block,
        )

        dbc = DBCFile(dbc_file, TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].name == "Тест"


class TestDBCFileFromFile:
    """Test creating DBCFile from file path."""

    def test_from_file_class_method(self, tmp_path):
        """Test creating DBCFile using from_file class method."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        # Create a temporary DBC file
        file_path = tmp_path / "test.dbc"
        records_data = struct.pack("<I", 42)
        dbc_content = create_dbc_file(
            record_count=1,
            field_count=1,
            record_size=4,
            records_data=records_data,
            string_block=b"",
        )

        with open(file_path, "wb") as f:
            f.write(dbc_content.read())

        # Load using from_file
        dbc = DBCFile.from_file(str(file_path), TestRow)
        records = dbc.get_records()

        assert len(records) == 1
        assert records[0].id == 42


class TestDBCFileDefaultDefinitions:
    """Test DBC file with default column definitions."""

    def test_use_default_definitions(self):
        """Test using default column definitions when none provided."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            @classmethod
            def get_definitions(cls) -> list[DBCColumnDefinition]:
                # Return empty list to trigger default generation
                return []

        # Create a simple DBC with 2 fields
        records_data = struct.pack("<II", 1, 2)
        dbc_file = create_dbc_file(
            record_count=1,
            field_count=2,
            record_size=8,
            records_data=records_data,
            string_block=b"",
        )

        dbc = DBCFile(dbc_file, TestRow)

        # Should generate default definitions
        assert len(dbc.column_definitions) == 2
        assert dbc.column_definitions[0].is_primary_key is True
        assert dbc.column_definitions[1].is_primary_key is False
