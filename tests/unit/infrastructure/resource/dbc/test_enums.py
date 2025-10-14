"""Tests for DBC enumerations."""

import pytest
from icecap.infrastructure.resource.dbc.enums import DBCFieldType, DBCLocale


class TestDBCFieldType:
    """Test the DBCFieldType enumeration."""

    def test_field_type_members(self):
        """Test that all expected field types exist."""
        expected_types = ["INT", "UINT", "FLOAT", "STRING", "BOOLEAN", "LOCALIZED_STRING"]

        for type_name in expected_types:
            assert hasattr(DBCFieldType, type_name)

    def test_field_type_values_are_unique(self):
        """Test that all field type values are unique."""
        values = [field_type.value for field_type in DBCFieldType]
        assert len(values) == len(set(values))

    def test_int_type(self):
        """Test INT field type."""
        assert DBCFieldType.INT is not None
        assert isinstance(DBCFieldType.INT.value, int)

    def test_uint_type(self):
        """Test UINT field type."""
        assert DBCFieldType.UINT is not None
        assert isinstance(DBCFieldType.UINT.value, int)

    def test_float_type(self):
        """Test FLOAT field type."""
        assert DBCFieldType.FLOAT is not None
        assert isinstance(DBCFieldType.FLOAT.value, int)

    def test_string_type(self):
        """Test STRING field type."""
        assert DBCFieldType.STRING is not None
        assert isinstance(DBCFieldType.STRING.value, int)

    def test_boolean_type(self):
        """Test BOOLEAN field type."""
        assert DBCFieldType.BOOLEAN is not None
        assert isinstance(DBCFieldType.BOOLEAN.value, int)

    def test_localized_string_type(self):
        """Test LOCALIZED_STRING field type."""
        assert DBCFieldType.LOCALIZED_STRING is not None
        assert isinstance(DBCFieldType.LOCALIZED_STRING.value, int)

    def test_field_type_comparison(self):
        """Test that field types can be compared."""
        assert DBCFieldType.INT == DBCFieldType.INT
        assert DBCFieldType.INT != DBCFieldType.UINT

    def test_field_type_iteration(self):
        """Test that we can iterate over field types."""
        field_types = list(DBCFieldType)
        assert len(field_types) == 6


class TestDBCLocale:
    """Test the DBCLocale enumeration."""

    def test_locale_members(self):
        """Test that all expected locales exist."""
        expected_locales = ["enUS", "koKR", "frFR", "deDE", "zhCN", "zhTW", "esES", "esMX", "ruRU"]

        for locale_name in expected_locales:
            assert hasattr(DBCLocale, locale_name)

    def test_locale_values(self):
        """Test that locale values match expected indices."""
        assert DBCLocale.enUS.value == 0
        assert DBCLocale.koKR.value == 1
        assert DBCLocale.frFR.value == 2
        assert DBCLocale.deDE.value == 3
        assert DBCLocale.zhCN.value == 4
        assert DBCLocale.zhTW.value == 5
        assert DBCLocale.esES.value == 6
        assert DBCLocale.esMX.value == 7
        assert DBCLocale.ruRU.value == 8

    def test_locale_values_are_unique(self):
        """Test that all locale values are unique."""
        values = [locale.value for locale in DBCLocale]
        assert len(values) == len(set(values))

    def test_locale_values_are_sequential(self):
        """Test that locale values are sequential starting from 0."""
        values = sorted([locale.value for locale in DBCLocale])
        expected = list(range(len(DBCLocale)))
        assert values == expected

    def test_locale_by_value(self):
        """Test that we can get locale by value."""
        assert DBCLocale(0) == DBCLocale.enUS
        assert DBCLocale(4) == DBCLocale.zhCN
        assert DBCLocale(8) == DBCLocale.ruRU

    def test_locale_comparison(self):
        """Test that locales can be compared."""
        assert DBCLocale.enUS == DBCLocale.enUS
        assert DBCLocale.enUS != DBCLocale.frFR

    def test_locale_iteration(self):
        """Test that we can iterate over locales."""
        locales = list(DBCLocale)
        assert len(locales) == 9

    def test_locale_name_format(self):
        """Test that locale names follow the expected format."""
        # All locale names should be 4 characters
        for locale in DBCLocale:
            assert len(locale.name) == 4

    def test_invalid_locale_value_raises_error(self):
        """Test that invalid locale value raises ValueError."""
        with pytest.raises(ValueError):
            DBCLocale(999)
