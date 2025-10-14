"""Tests for DBC prototype classes."""

import pytest
from dataclasses import dataclass, field
from icecap.infrastructure.resource.dbc.prototype import BaseDBCRecord
from icecap.infrastructure.resource.dbc.dto import DBCRowWithDefinitions, DBCColumnDefinition
from icecap.infrastructure.resource.dbc.enums import DBCFieldType


class TestBaseDBCRecord:
    """Test the BaseDBCRecord class."""

    def test_base_dbc_record_exists(self):
        """Test that BaseDBCRecord class exists."""
        assert BaseDBCRecord is not None

    def test_base_dbc_record_instantiation(self):
        """Test that BaseDBCRecord can be instantiated."""
        record = BaseDBCRecord()
        assert isinstance(record, BaseDBCRecord)


class TestDBCRowWithDefinitions:
    """Test DBCRowWithDefinitions functionality in prototype context."""

    def test_simple_row_with_definitions(self):
        """Test creating a simple row with column definitions."""

        @dataclass(frozen=True)
        class SimpleRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            value: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.INT)})

        definitions = SimpleRow.get_definitions()

        assert len(definitions) == 2
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[0].is_primary_key is True
        assert definitions[1].field_type == DBCFieldType.INT
        assert definitions[1].is_primary_key is False

    def test_row_with_all_field_types(self):
        """Test creating a row with all DBC field types."""

        @dataclass(frozen=True)
        class CompleteRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            int_value: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.INT)})
            float_value: float = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT)}
            )
            string_value: str = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)}
            )
            bool_value: bool = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.BOOLEAN)}
            )
            localized: dict = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.LOCALIZED_STRING)}
            )

        definitions = CompleteRow.get_definitions()

        assert len(definitions) == 6
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[1].field_type == DBCFieldType.INT
        assert definitions[2].field_type == DBCFieldType.FLOAT
        assert definitions[3].field_type == DBCFieldType.STRING
        assert definitions[4].field_type == DBCFieldType.BOOLEAN
        assert definitions[5].field_type == DBCFieldType.LOCALIZED_STRING

    def test_row_with_array_columns(self):
        """Test creating a row with array columns."""

        @dataclass(frozen=True)
        class ArrayRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            values: list = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.INT, array_size=5)}
            )
            coordinates: list = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT, array_size=3)}
            )

        definitions = ArrayRow.get_definitions()

        assert len(definitions) == 3
        assert definitions[0].array_size == 1
        assert definitions[1].array_size == 5
        assert definitions[1].field_type == DBCFieldType.INT
        assert definitions[2].array_size == 3
        assert definitions[2].field_type == DBCFieldType.FLOAT

    def test_row_instantiation(self):
        """Test that row prototype can be instantiated."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            name: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})

        row = TestRow(id=1, name="Test")

        assert row.id == 1
        assert row.name == "Test"

    def test_row_immutability(self):
        """Test that row instances are immutable."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        row = TestRow(id=1)

        with pytest.raises(Exception):  # FrozenInstanceError
            row.id = 2

    def test_multiple_primary_keys_not_recommended(self):
        """Test that multiple primary keys can be defined (though not recommended)."""

        @dataclass(frozen=True)
        class MultiPKRow(DBCRowWithDefinitions):
            id1: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            id2: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        definitions = MultiPKRow.get_definitions()

        assert len(definitions) == 2
        assert definitions[0].is_primary_key is True
        assert definitions[1].is_primary_key is True

    def test_row_definition_order_preservation(self):
        """Test that field definition order is preserved."""

        @dataclass(frozen=True)
        class OrderedRow(DBCRowWithDefinitions):
            field_a: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            field_b: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})
            field_c: float = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT)})

        definitions = OrderedRow.get_definitions()

        assert len(definitions) == 3
        # Order should match field declaration order
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[1].field_type == DBCFieldType.STRING
        assert definitions[2].field_type == DBCFieldType.FLOAT


class TestMapRowPrototype:
    """Test creating Map-like DBC row prototypes."""

    def test_map_dbc_row_prototype(self):
        """Test creating a prototype similar to Map.dbc structure."""

        @dataclass(frozen=True)
        class MapRow(DBCRowWithDefinitions):
            map_id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            internal_name: str = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)}
            )
            map_type: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT)})
            instance_type: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT)}
            )
            map_name: dict = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.LOCALIZED_STRING)}
            )

        definitions = MapRow.get_definitions()

        assert len(definitions) == 5
        assert definitions[0].field_type == DBCFieldType.UINT
        assert definitions[0].is_primary_key is True
        assert definitions[1].field_type == DBCFieldType.STRING
        assert definitions[2].field_type == DBCFieldType.UINT
        assert definitions[3].field_type == DBCFieldType.UINT
        assert definitions[4].field_type == DBCFieldType.LOCALIZED_STRING

    def test_spell_dbc_row_prototype(self):
        """Test creating a prototype similar to Spell.dbc structure."""

        @dataclass(frozen=True)
        class SpellRow(DBCRowWithDefinitions):
            spell_id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            category: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT)})
            cast_time: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT)})
            cooldown: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.INT)})
            effects: list = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, array_size=3)}
            )
            name: dict = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.LOCALIZED_STRING)}
            )

        definitions = SpellRow.get_definitions()

        assert len(definitions) == 6
        assert definitions[0].is_primary_key is True
        assert definitions[4].array_size == 3
        assert definitions[5].field_type == DBCFieldType.LOCALIZED_STRING
