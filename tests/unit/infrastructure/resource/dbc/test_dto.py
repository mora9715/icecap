"""Tests for DBC data transfer objects."""

import pytest
from dataclasses import dataclass, field
from icecap.infrastructure.resource.dbc.dto import (
    DBCColumnDefinition,
    DBCHeader,
    DBCRowWithDefinitions,
)
from icecap.infrastructure.resource.dbc.enums import DBCFieldType


class TestDBCColumnDefinition:
    """Test the DBCColumnDefinition class."""

    def test_create_column_definition(self):
        """Test creating a basic column definition."""
        column = DBCColumnDefinition(field_type=DBCFieldType.UINT)

        assert column.field_type == DBCFieldType.UINT
        assert column.array_size == 1
        assert column.is_primary_key is False

    def test_create_column_definition_with_array(self):
        """Test creating a column definition with array."""
        column = DBCColumnDefinition(field_type=DBCFieldType.INT, array_size=5)

        assert column.field_type == DBCFieldType.INT
        assert column.array_size == 5
        assert column.is_primary_key is False

    def test_create_column_definition_as_primary_key(self):
        """Test creating a column definition as primary key."""
        column = DBCColumnDefinition(field_type=DBCFieldType.UINT, is_primary_key=True)

        assert column.field_type == DBCFieldType.UINT
        assert column.array_size == 1
        assert column.is_primary_key is True

    def test_column_definition_immutable(self):
        """Test that column definition is immutable."""
        column = DBCColumnDefinition(field_type=DBCFieldType.UINT)

        with pytest.raises(Exception):  # FrozenInstanceError
            column.field_type = DBCFieldType.INT

    def test_generate_default_definitions_single_field(self):
        """Test generating default definitions for 1 field."""
        definitions = DBCColumnDefinition.generate_default_definitions(1)

        assert len(definitions) == 1
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[0].is_primary_key is True

    def test_generate_default_definitions_multiple_fields(self):
        """Test generating default definitions for multiple fields."""
        definitions = DBCColumnDefinition.generate_default_definitions(5)

        assert len(definitions) == 5

        # First field should be primary key
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[0].is_primary_key is True

        # Other fields should not be primary keys
        for i in range(1, 5):
            assert definitions[i].field_type == DBCFieldType.UINT
            assert definitions[i].is_primary_key is False

    def test_generate_default_definitions_zero_fields(self):
        """Test generating default definitions for 0 fields."""
        # When field_count is 0, generate_default_definitions should return empty list
        # But actually this is an edge case that shouldn't happen in real DBC files
        definitions = DBCColumnDefinition.generate_default_definitions(0)

        assert isinstance(definitions, list)
        assert len(definitions) == 0

    def test_column_definition_equality(self):
        """Test column definition equality."""
        col1 = DBCColumnDefinition(field_type=DBCFieldType.UINT)
        col2 = DBCColumnDefinition(field_type=DBCFieldType.UINT)
        col3 = DBCColumnDefinition(field_type=DBCFieldType.INT)

        assert col1 == col2
        assert col1 != col3

    def test_column_definition_with_all_field_types(self):
        """Test creating column definitions with all field types."""
        for field_type in DBCFieldType:
            column = DBCColumnDefinition(field_type=field_type)
            assert column.field_type == field_type


class TestDBCHeader:
    """Test the DBCHeader class."""

    def test_create_header(self):
        """Test creating a DBC header."""
        header = DBCHeader(
            signature="WDBC",
            record_count=100,
            field_count=10,
            record_size=40,
            string_block_size=500,
        )

        assert header.signature == "WDBC"
        assert header.record_count == 100
        assert header.field_count == 10
        assert header.record_size == 40
        assert header.string_block_size == 500

    def test_header_immutable(self):
        """Test that header is immutable."""
        header = DBCHeader(
            signature="WDBC",
            record_count=100,
            field_count=10,
            record_size=40,
            string_block_size=500,
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            header.signature = "TEST"

    def test_header_with_zero_records(self):
        """Test creating a header with zero records."""
        header = DBCHeader(
            signature="WDBC", record_count=0, field_count=5, record_size=20, string_block_size=0
        )

        assert header.record_count == 0
        assert header.string_block_size == 0

    def test_header_equality(self):
        """Test header equality."""
        header1 = DBCHeader(
            signature="WDBC",
            record_count=100,
            field_count=10,
            record_size=40,
            string_block_size=500,
        )
        header2 = DBCHeader(
            signature="WDBC",
            record_count=100,
            field_count=10,
            record_size=40,
            string_block_size=500,
        )
        header3 = DBCHeader(
            signature="WDBC",
            record_count=50,
            field_count=10,
            record_size=40,
            string_block_size=500,
        )

        assert header1 == header2
        assert header1 != header3


class TestDBCRowWithDefinitions:
    """Test the DBCRowWithDefinitions class."""

    def test_get_definitions_from_dataclass(self):
        """Test getting column definitions from a dataclass."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            name: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})
            value: float = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT)})

        definitions = TestRow.get_definitions()

        assert len(definitions) == 3
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[0].is_primary_key is True
        assert definitions[1].field_type == DBCFieldType.STRING
        assert definitions[2].field_type == DBCFieldType.FLOAT

    def test_get_definitions_with_arrays(self):
        """Test getting column definitions with array fields."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            values: list = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.INT, array_size=3)}
            )

        definitions = TestRow.get_definitions()

        assert len(definitions) == 2
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[1].field_type == DBCFieldType.INT
        assert definitions[1].array_size == 3

    def test_metadata_key_constant(self):
        """Test that METADATA_KEY constant is correct."""
        assert DBCRowWithDefinitions.METADATA_KEY == "definition"

    def test_get_definitions_empty_dataclass(self):
        """Test getting definitions from an empty dataclass."""

        @dataclass(frozen=True)
        class EmptyRow(DBCRowWithDefinitions):
            pass

        definitions = EmptyRow.get_definitions()

        assert len(definitions) == 0

    def test_get_definitions_missing_metadata(self):
        """Test getting definitions when metadata is missing."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            # This field has no metadata
            other: int = 0

        definitions = TestRow.get_definitions()

        # Should handle missing metadata gracefully
        assert len(definitions) == 2
        assert definitions[0] is not None
        assert definitions[1] is None  # Missing metadata returns None
