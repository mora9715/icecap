"""Tests for the MinimapService."""

import struct
import pytest
from unittest.mock import Mock

from icecap.services.navigation.minimap.service import MinimapService


def create_mock_map_dbc(map_ids: list[tuple[int, str]]) -> bytes:
    """Helper to create a Map.dbc file for testing.

    Args:
        map_ids: List of (map_id, directory) tuples
    """
    # Map.dbc structure (simplified): map_id (UINT)
    record_count = len(map_ids)
    records_data = b""
    string_block = b"\x00"  # Start with null byte

    for map_id, directory in map_ids:
        # Add directory string to string block
        offset = len(string_block)
        string_block += directory.encode("utf-8") + b"\x00"

        # Record: map_id (4 bytes), directory_offset (4 bytes)
        records_data += struct.pack("<II", map_id, offset)

    header = struct.pack(
        "<4s4I",
        b"WDBC",
        record_count,
        2,  # 2 fields: map_id, directory
        8,  # 8 bytes per record
        len(string_block),
    )

    return header + records_data + string_block


class TestMinimapServiceInitialization:
    """Test MinimapService initialization."""

    def test_service_initialization_loads_files(self):
        """Test that service loads md5translate and Map.dbc on initialization."""
        mock_mpq_reader = Mock()

        # Mock md5translate.trs
        md5_content = b"dir: world\\maps\\azeroth\nmap0_0.blp\thashed_file.blp\n"

        # Mock Map.dbc
        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\azeroth")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        # Initialize service
        service = MinimapService(mock_mpq_reader)

        # Verify both files were loaded
        assert service._md5_translate is not None
        assert service._map_database is not None

    def test_service_raises_error_if_md5translate_missing(self):
        """Test that service raises error if md5translate.trs is missing."""
        mock_mpq_reader = Mock()
        mock_mpq_reader.read_file.return_value = None

        with pytest.raises(Exception, match="Failed to read md5translate.trs"):
            MinimapService(mock_mpq_reader)

    def test_service_raises_error_if_map_dbc_missing(self):
        """Test that service raises error if Map.dbc is missing."""
        mock_mpq_reader = Mock()

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return b"dir: test\n"
            return None

        mock_mpq_reader.read_file = mock_read_file

        with pytest.raises(Exception, match="Failed to read map.dbc"):
            MinimapService(mock_mpq_reader)


class TestMinimapServiceMD5TranslateParsing:
    """Test md5translate.trs parsing."""

    def test_parse_single_directory(self):
        """Test parsing md5translate with a single directory."""
        mock_mpq_reader = Mock()

        md5_content = b"dir: world\\maps\\azeroth\nmap0_0.blp\thash1.blp\nmap0_1.blp\thash2.blp\n"

        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\azeroth")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Verify structure
        assert "world\\maps\\azeroth" in service._md5_translate
        assert service._md5_translate["world\\maps\\azeroth"]["map0_0.blp"] == "hash1.blp"
        assert service._md5_translate["world\\maps\\azeroth"]["map0_1.blp"] == "hash2.blp"

    def test_parse_multiple_directories(self):
        """Test parsing md5translate with multiple directories."""
        mock_mpq_reader = Mock()

        md5_content = (
            b"dir: world\\maps\\azeroth\n"
            b"map0_0.blp\thash1.blp\n"
            b"dir: world\\maps\\kalimdor\n"
            b"map0_0.blp\thash3.blp\n"
        )

        map_dbc_content = create_mock_map_dbc(
            [
                (0, "world\\maps\\azeroth"),
                (1, "world\\maps\\kalimdor"),
            ]
        )

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Verify both directories
        assert len(service._md5_translate) == 2
        assert "world\\maps\\azeroth" in service._md5_translate
        assert "world\\maps\\kalimdor" in service._md5_translate

    def test_parse_empty_lines_ignored(self):
        """Test that empty lines are ignored."""
        mock_mpq_reader = Mock()

        md5_content = b"dir: world\\maps\\azeroth\n\nmap0_0.blp\thash1.blp\n\n"

        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\azeroth")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Should parse correctly despite empty lines
        assert len(service._md5_translate["world\\maps\\azeroth"]) == 1


class TestMinimapServiceBuildTexturePath:
    """Test building minimap texture paths."""

    def test_build_texture_path_found(self):
        """Test building texture path when file exists."""
        mock_mpq_reader = Mock()

        md5_content = b"dir: world\\maps\\azeroth\nmap5_10.blp\thashed_5_10.blp\n"

        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\azeroth")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Build path
        path = service.build_minimap_texture_path("world\\maps\\azeroth", 5, 10)

        assert path == "textures\\Minimap\\hashed_5_10.blp"

    def test_build_texture_path_not_found(self):
        """Test building texture path when file doesn't exist."""
        mock_mpq_reader = Mock()

        md5_content = b"dir: world\\maps\\azeroth\n"
        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\azeroth")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Try to build path for non-existent tile
        path = service.build_minimap_texture_path("world\\maps\\azeroth", 99, 99)

        assert path is None

    def test_build_texture_path_unknown_directory(self):
        """Test building texture path for unknown directory."""
        mock_mpq_reader = Mock()

        md5_content = b"dir: world\\maps\\azeroth\nmap0_0.blp\thash.blp\n"
        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\azeroth")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Try unknown directory
        path = service.build_minimap_texture_path("world\\maps\\unknown", 0, 0)

        assert path is None


class TestMinimapServiceEdgeCases:
    """Test edge cases and error handling."""

    def test_service_handles_unicode_characters(self):
        """Test service handles unicode in directory names."""
        mock_mpq_reader = Mock()

        # Directory with special characters
        md5_content = "dir: world\\maps\\тест\nmap0_0.blp\thash.blp\n".encode("utf-8")
        map_dbc_content = create_mock_map_dbc([(0, "world\\maps\\тест")])

        def mock_read_file(path):
            if "md5translate.trs" in path:
                return md5_content
            elif "Map.dbc" in path:
                return map_dbc_content
            return None

        mock_mpq_reader.read_file = mock_read_file

        service = MinimapService(mock_mpq_reader)

        # Should handle unicode correctly
        assert "world\\maps\\тест" in service._md5_translate
