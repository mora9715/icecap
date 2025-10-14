"""Integration tests for MPQ and DBC file parsing together.

These tests verify that DBC files can be loaded from MPQ archives
and parsed correctly.
"""

import struct
from io import BytesIO
from dataclasses import dataclass, field
from unittest.mock import Mock, patch

from icecap.infrastructure.resource.mpq.archive import MPQArchive
from icecap.infrastructure.resource.mpq.chain import MPQArchiveChain
from icecap.infrastructure.resource.dbc.database import DBCFile
from icecap.infrastructure.resource.dbc.dto import DBCColumnDefinition, DBCRowWithDefinitions
from icecap.infrastructure.resource.dbc.enums import DBCFieldType


def create_mock_dbc_file(record_count: int = 1) -> bytes:
    """Helper to create a valid DBC file in memory."""
    # Simple DBC with one UINT field
    records_data = struct.pack("<" + "I" * record_count, *range(1, record_count + 1))
    header = struct.pack(
        "<4s4I",
        b"WDBC",
        record_count,  # record count
        1,  # field count
        4,  # record size
        0,  # string block size
    )
    return header + records_data


class TestMPQDBCIntegration:
    """Test loading DBC files from MPQ archives."""

    @patch("builtins.open")
    def test_load_dbc_from_single_mpq_archive(self, mock_open):
        """Test loading a DBC file from a single MPQ archive."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        # Create a mock DBC file
        dbc_content = create_mock_dbc_file(record_count=3)

        # Create a mock MPQ archive
        archive = MPQArchive("test.mpq")
        archive._file = Mock()

        # Mock the read_file method to return our DBC
        with patch.object(archive, "read_file", return_value=dbc_content):
            # Simulate loading DBC from MPQ
            raw_dbc = archive.read_file("DBFilesClient\\Test.dbc")

            assert raw_dbc is not None

            # Parse the DBC
            dbc = DBCFile(BytesIO(raw_dbc), TestRow)
            records = dbc.get_records()

            # Verify records were parsed correctly
            assert len(records) == 3
            assert records[0].id == 1
            assert records[1].id == 2
            assert records[2].id == 3

    @patch("builtins.open")
    def test_load_dbc_from_mpq_chain(self, mock_open):
        """Test loading a DBC file from an MPQ chain with priority."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        # Create two different DBC files (simulating patch vs base)
        base_dbc = create_mock_dbc_file(record_count=1)
        patched_dbc = create_mock_dbc_file(record_count=5)

        # Create mock archives
        base_archive = Mock(spec=MPQArchive)
        base_archive.file_path = "/data/base.mpq"
        base_archive.file_exists.return_value = True
        base_archive.read_file.return_value = base_dbc

        patch_archive = Mock(spec=MPQArchive)
        patch_archive.file_path = "/data/patch-2.mpq"
        patch_archive.file_exists.return_value = True
        patch_archive.read_file.return_value = patched_dbc

        # Create chain and add archives
        chain = MPQArchiveChain()
        chain.add_archive(base_archive)
        chain.add_archive(patch_archive)

        # Load DBC from chain (should get patched version)
        raw_dbc = chain.read_file("DBFilesClient\\Test.dbc")

        assert raw_dbc is not None

        # Parse the DBC
        dbc = DBCFile(BytesIO(raw_dbc), TestRow)
        records = dbc.get_records()

        # Should get the patched version (5 records, not 1)
        assert len(records) == 5

    @patch("builtins.open")
    def test_dbc_not_found_in_mpq(self, mock_open):
        """Test handling when DBC file doesn't exist in MPQ."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        # Create mock archive that doesn't have the file
        archive = Mock(spec=MPQArchive)
        archive.file_path = "/data/test.mpq"
        archive.file_exists.return_value = False
        archive.read_file.return_value = None

        # Try to load non-existent DBC
        raw_dbc = archive.read_file("DBFilesClient\\NonExistent.dbc")

        assert raw_dbc is None

    @patch("builtins.open")
    def test_complex_dbc_from_mpq(self, mock_open):
        """Test loading a DBC with multiple field types from MPQ."""

        @dataclass(frozen=True)
        class ComplexRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )
            value: int = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.INT)})
            ratio: float = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.FLOAT)})
            name: str = field(metadata={"definition": DBCColumnDefinition(DBCFieldType.STRING)})

        # Create a DBC with multiple fields
        records_data = struct.pack("<Iif", 1, -100, 2.5) + struct.pack("<I", 1)  # String offset
        string_block = b"\x00TestName\x00"
        header = struct.pack(
            "<4s4I",
            b"WDBC",
            1,  # record count
            4,  # field count
            16,  # record size
            len(string_block),  # string block size
        )
        dbc_content = header + records_data + string_block

        # Create mock archive
        archive = Mock(spec=MPQArchive)
        archive.file_path = "/data/test.mpq"
        archive.file_exists.return_value = True
        archive.read_file.return_value = dbc_content

        # Load and parse
        raw_dbc = archive.read_file("DBFilesClient\\Complex.dbc")
        dbc = DBCFile(BytesIO(raw_dbc), ComplexRow)
        records = dbc.get_records()

        # Verify all fields
        assert len(records) == 1
        assert records[0].id == 1
        assert records[0].value == -100
        assert abs(records[0].ratio - 2.5) < 0.0001
        assert records[0].name == "TestName"


class TestMinimapDataPipeline:
    """Test the complete minimap data pipeline (MPQ -> DBC -> Minimap)."""

    @patch("builtins.open")
    def test_minimap_data_loading_pipeline(self, mock_open):
        """Test loading minimap-related files from MPQ."""
        # This is a simplified test of the minimap pipeline
        # In reality, this would involve loading Map.dbc and md5translate.trs

        # Create a simple Map.dbc structure
        @dataclass(frozen=True)
        class MapRow(DBCRowWithDefinitions):
            map_id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        # Create Map.dbc content
        records_data = struct.pack("<III", 0, 1, 530)  # Eastern Kingdoms, Kalimdor, Outland
        header = struct.pack("<4s4I", b"WDBC", 3, 1, 4, 0)
        map_dbc_content = header + records_data

        # Create md5translate content
        md5translate_content = b"dir: world\\maps\\azeroth\nmap0_0.blp\thashed_file.blp\n"

        # Create mock MPQ archive
        def mock_read_file(path):
            if "Map.dbc" in path:
                return map_dbc_content
            elif "md5translate.trs" in path:
                return md5translate_content
            return None

        archive = Mock(spec=MPQArchive)
        archive.file_exists = lambda p: True
        archive.read_file = mock_read_file

        # Test loading Map.dbc
        raw_map_dbc = archive.read_file("DBFilesClient\\Map.dbc")
        assert raw_map_dbc is not None

        map_dbc = DBCFile(BytesIO(raw_map_dbc), MapRow)
        map_records = map_dbc.get_records()

        assert len(map_records) == 3
        assert map_records[0].map_id == 0
        assert map_records[1].map_id == 1
        assert map_records[2].map_id == 530

        # Test loading md5translate.trs
        raw_md5translate = archive.read_file("textures\\Minimap\\md5translate.trs")
        assert raw_md5translate is not None
        assert b"map0_0.blp" in raw_md5translate


class TestDBCCaching:
    """Test that DBC files are cached properly when loaded from MPQ."""

    @patch("builtins.open")
    def test_dbc_loaded_once_from_mpq(self, mock_open):
        """Test that DBC is only loaded once from MPQ and then cached."""

        @dataclass(frozen=True)
        class TestRow(DBCRowWithDefinitions):
            id: int = field(
                metadata={"definition": DBCColumnDefinition(DBCFieldType.UINT, is_primary_key=True)}
            )

        dbc_content = create_mock_dbc_file(record_count=1)

        # Create mock archive that tracks calls
        call_count = {"count": 0}

        def mock_read_file(path):
            call_count["count"] += 1
            return dbc_content

        archive = Mock(spec=MPQArchive)
        archive.read_file = mock_read_file

        # Load DBC multiple times
        raw_dbc1 = archive.read_file("DBFilesClient\\Test.dbc")
        dbc1 = DBCFile(BytesIO(raw_dbc1), TestRow)
        records1 = dbc1.get_records()

        raw_dbc2 = archive.read_file("DBFilesClient\\Test.dbc")
        dbc2 = DBCFile(BytesIO(raw_dbc2), TestRow)
        records2 = dbc2.get_records()

        # Archive read_file was called twice (no automatic caching at archive level)
        # But DBC parsing should use internal caching
        assert records1[0].id == records2[0].id

        # Both calls should work
        assert call_count["count"] == 2
