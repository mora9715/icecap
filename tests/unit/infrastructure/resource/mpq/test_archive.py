"""Tests for MPQ archive parsing.

Note: These tests use mocked data and don't require actual MPQ files.
They test the parsing logic and file reading capabilities.
"""

import struct
import pytest
from unittest.mock import Mock, patch, mock_open
from icecap.infrastructure.resource.mpq.archive import MPQArchive
from icecap.infrastructure.resource.mpq.dto import (
    Header,
    HeaderExtension,
    HashTableEntry,
    BlockTableEntry,
)
from icecap.infrastructure.resource.mpq.enums import HashType
from icecap.infrastructure.resource.mpq.flags import (
    MPQ_FILE_EXISTS,
)


class TestMPQArchiveHeader:
    """Test MPQ archive header parsing."""

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_valid_header_v0(self, mock_file):
        """Test parsing a valid MPQ header version 0."""
        # Create a valid MPQ v0 header
        header_data = struct.pack(
            "<4s2I2H4I",
            b"MPQ\x1a",  # Magic
            32,  # Header size
            1024,  # Archive size
            0,  # Format version
            3,  # Block size (512 << 3 = 4096)
            32,  # Hash table offset
            128,  # Block table offset
            16,  # Hash table size
            8,  # Block table size
        )

        mock_file.return_value.read.side_effect = [b"MPQ\x1a", header_data]

        archive = MPQArchive("test.mpq")
        header = archive.get_header()

        assert header.magic == b"MPQ\x1a"
        assert header.header_size == 32
        assert header.archive_size == 1024
        assert header.format_version == 0
        assert header.block_size == 3
        assert header.hash_table_offset == 32
        assert header.block_table_offset == 128
        assert header.hash_table_size == 16
        assert header.block_table_size == 8
        assert header.extension is None

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_valid_header_v1(self, mock_file):
        """Test parsing a valid MPQ header version 1."""
        # Create a valid MPQ v1 header with extension
        header_data = struct.pack(
            "<4s2I2H4I",
            b"MPQ\x1a",  # Magic
            32,  # Header size
            1024,  # Archive size
            1,  # Format version (v1)
            3,  # Block size
            32,  # Hash table offset
            128,  # Block table offset
            16,  # Hash table size
            8,  # Block table size
        )
        extension_data = struct.pack(
            "<q2h",
            0,  # Extended block table offset
            0,  # Hash table offset high
            0,  # Block table offset high
        )

        mock_file.return_value.read.side_effect = [
            b"MPQ\x1a",
            header_data,
            extension_data,
        ]

        archive = MPQArchive("test.mpq")
        header = archive.get_header()

        assert header.format_version == 1
        assert header.extension is not None
        assert isinstance(header.extension, HeaderExtension)

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_invalid_signature(self, mock_file):
        """Test parsing with invalid MPQ signature."""
        mock_file.return_value.read.return_value = b"INVALID"

        archive = MPQArchive("test.mpq")

        with pytest.raises(ValueError, match="Invalid MPQ header"):
            archive.get_header()

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_shunt_signature_not_supported(self, mock_file):
        """Test that MPQ shunts are not supported."""
        mock_file.return_value.read.return_value = b"MPQ\x1b"

        archive = MPQArchive("test.mpq")

        with pytest.raises(ValueError, match="MPQ shunts are not supported"):
            archive.get_header()

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_unsupported_version(self, mock_file):
        """Test parsing with unsupported MPQ version."""
        header_data = struct.pack(
            "<4s2I2H4I",
            b"MPQ\x1a",
            32,
            1024,
            2,  # Format version 2 (unsupported)
            3,
            32,
            128,
            16,
            8,
        )

        mock_file.return_value.read.side_effect = [b"MPQ\x1a", header_data]

        archive = MPQArchive("test.mpq")

        with pytest.raises(ValueError, match="Unsupported MPQ format version"):
            archive.get_header()

    @patch("builtins.open", new_callable=mock_open)
    def test_header_caching(self, mock_file):
        """Test that header is cached after first read."""
        header_data = struct.pack("<4s2I2H4I", b"MPQ\x1a", 32, 1024, 0, 3, 32, 128, 16, 8)

        mock_file.return_value.read.side_effect = [b"MPQ\x1a", header_data]

        archive = MPQArchive("test.mpq")

        header1 = archive.get_header()
        header2 = archive.get_header()

        # Should return the same cached object
        assert header1 is header2


class TestMPQArchiveHashTable:
    """Test MPQ archive hash table parsing."""

    @patch("builtins.open", new_callable=mock_open)
    def test_parse_hash_table(self, mock_file):
        """Test parsing hash table."""
        archive = MPQArchive("test.mpq")

        # Mock header
        archive._header = Header(
            magic="MPQ\x1a",
            header_size=32,
            archive_size=1024,
            format_version=0,
            block_size=3,
            hash_table_offset=100,
            block_table_offset=200,
            hash_table_size=2,
            block_table_size=1,
        )

        # Create encrypted hash table data (2 entries)
        # Each entry is 16 bytes: name1(4), name2(4), locale(2), platform(2), block_index(4)
        hash_entry1 = struct.pack("<2I2HI", 0x12345678, 0x87654321, 0, 0, 0)
        hash_entry2 = struct.pack("<2I2HI", 0xAABBCCDD, 0xDDCCBBAA, 0, 0, 1)
        hash_data = hash_entry1 + hash_entry2

        mock_file.return_value.seek = Mock()
        mock_file.return_value.read.return_value = hash_data

        hash_table = archive.get_hash_table()

        assert len(hash_table.entries) == 2
        assert all(isinstance(entry, HashTableEntry) for entry in hash_table.entries)

    @patch("builtins.open", new_callable=mock_open)
    def test_hash_table_caching(self, mock_file):
        """Test that hash table is cached."""
        archive = MPQArchive("test.mpq")

        # Mock header
        archive._header = Header(
            magic="MPQ\x1a",
            header_size=32,
            archive_size=1024,
            format_version=0,
            block_size=3,
            hash_table_offset=100,
            block_table_offset=200,
            hash_table_size=1,
            block_table_size=1,
        )

        hash_data = struct.pack("<2I2HI", 0x12345678, 0x87654321, 0, 0, 0)
        mock_file.return_value.seek = Mock()
        mock_file.return_value.read.return_value = hash_data

        table1 = archive.get_hash_table()
        table2 = archive.get_hash_table()

        assert table1 is table2


class TestMPQArchiveBlockTable:
    """Test MPQ archive block table parsing."""

    @patch("builtins.open", new_callable=mock_open)
    def test_block_table_caching(self, mock_file):
        """Test that block table is cached."""
        archive = MPQArchive("test.mpq")

        archive._header = Header(
            magic="MPQ\x1a",
            header_size=32,
            archive_size=1024,
            format_version=0,
            block_size=3,
            hash_table_offset=100,
            block_table_offset=200,
            hash_table_size=1,
            block_table_size=1,
        )

        block_data = struct.pack("<4I", 300, 100, 200, MPQ_FILE_EXISTS)
        mock_file.return_value.seek = Mock()
        mock_file.return_value.read.return_value = block_data

        table1 = archive.get_block_table()
        table2 = archive.get_block_table()

        assert table1 is table2


class TestMPQArchiveFileOperations:
    """Test MPQ archive file operations."""

    @patch("builtins.open", new_callable=mock_open)
    def test_file_exists_true(self, mock_file):
        """Test checking if a file exists in the archive."""
        archive = MPQArchive("test.mpq")

        # Mock hash table with a matching entry
        hash_a = archive.crypt.hash("test.txt", HashType.HASH_A)
        hash_b = archive.crypt.hash("test.txt", HashType.HASH_B)

        archive._hash_table = Mock()
        archive._hash_table.entries = [
            HashTableEntry(name1=hash_a, name2=hash_b, locale=0, platform=0, block_index=0)
        ]

        assert archive.file_exists("test.txt") is True

    @patch("builtins.open", new_callable=mock_open)
    def test_file_exists_false(self, mock_file):
        """Test checking if a file doesn't exist."""
        archive = MPQArchive("test.mpq")

        archive._hash_table = Mock()
        archive._hash_table.entries = [
            HashTableEntry(name1=0x12345678, name2=0x87654321, locale=0, platform=0, block_index=0)
        ]

        assert archive.file_exists("nonexistent.txt") is False

    @patch("builtins.open", new_callable=mock_open)
    def test_get_hash_table_entry(self, mock_file):
        """Test getting a specific hash table entry."""
        archive = MPQArchive("test.mpq")

        hash_a = archive.crypt.hash("test.txt", HashType.HASH_A)
        hash_b = archive.crypt.hash("test.txt", HashType.HASH_B)

        expected_entry = HashTableEntry(
            name1=hash_a, name2=hash_b, locale=0, platform=0, block_index=0
        )

        archive._hash_table = Mock()
        archive._hash_table.entries = [expected_entry]

        entry = archive.get_hash_table_entry("test.txt")

        assert entry == expected_entry

    @patch("builtins.open", new_callable=mock_open)
    def test_get_hash_table_entry_not_found(self, mock_file):
        """Test getting a non-existent hash table entry."""
        archive = MPQArchive("test.mpq")

        archive._hash_table = Mock()
        archive._hash_table.entries = []

        entry = archive.get_hash_table_entry("nonexistent.txt")

        assert entry is None


class TestMPQArchiveListfile:
    """Test MPQ archive listfile parsing."""

    @patch("builtins.open", new_callable=mock_open)
    def test_get_file_names(self, mock_file):
        """Test parsing the listfile."""
        archive = MPQArchive("test.mpq")

        # Mock read_file to return a listfile
        listfile_content = b"file1.txt\nfile2.dbc\npath/to/file3.blp\n"

        with patch.object(archive, "read_file", return_value=listfile_content):
            file_names = archive.get_file_names()

        assert len(file_names) == 3
        assert "file1.txt" in file_names
        assert "file2.dbc" in file_names
        assert "path/to/file3.blp" in file_names

    @patch("builtins.open", new_callable=mock_open)
    def test_get_file_names_no_listfile(self, mock_file):
        """Test when no listfile is present."""
        archive = MPQArchive("test.mpq")

        with patch.object(archive, "read_file", return_value=None):
            file_names = archive.get_file_names()

        assert file_names == []

    @patch("builtins.open", new_callable=mock_open)
    def test_file_names_caching(self, mock_file):
        """Test that file names are cached."""
        archive = MPQArchive("test.mpq")

        listfile_content = b"file1.txt\n"

        with patch.object(archive, "read_file", return_value=listfile_content) as mock_read:
            names1 = archive.get_file_names()
            names2 = archive.get_file_names()

            # read_file should only be called once due to caching
            mock_read.assert_called_once()
            assert names1 is names2


class TestMPQArchiveCompression:
    """Test MPQ archive compression handling."""

    @patch("builtins.open", new_callable=mock_open)
    def test_decompress_uncompressed_data(self, mock_file):
        """Test decompressing uncompressed data."""
        archive = MPQArchive("test.mpq")

        # Type 0 means no compression
        data = b"\x00Hello World"
        result = archive._decompress_data(data)

        assert result == data

    @patch("builtins.open", new_callable=mock_open)
    def test_decompress_zlib_data(self, mock_file):
        """Test decompressing zlib compressed data."""
        import zlib

        archive = MPQArchive("test.mpq")

        original = b"Hello World" * 100
        compressed = zlib.compress(original)
        # Type 2 means zlib compression
        data = b"\x02" + compressed

        result = archive._decompress_data(data)

        assert result == original

    @patch("builtins.open", new_callable=mock_open)
    def test_decompress_bz2_data(self, mock_file):
        """Test decompressing bz2 compressed data."""
        import bz2

        archive = MPQArchive("test.mpq")

        original = b"Hello World" * 100
        compressed = bz2.compress(original)
        # Type 16 means bz2 compression
        data = b"\x10" + compressed

        result = archive._decompress_data(data)

        assert result == original

    @patch("builtins.open", new_callable=mock_open)
    def test_decompress_unsupported_type(self, mock_file):
        """Test decompressing with unsupported compression type."""
        archive = MPQArchive("test.mpq")

        # Type 99 is unsupported
        data = b"\x63Hello World"

        with pytest.raises(RuntimeError, match="Unsupported compression type"):
            archive._decompress_data(data)


class TestMPQArchiveFileReading:
    """Test MPQ archive file reading."""

    @patch("builtins.open", new_callable=mock_open)
    def test_read_nonexistent_file(self, mock_file):
        """Test reading a file that doesn't exist."""
        archive = MPQArchive("test.mpq")

        with patch.object(archive, "get_hash_table_entry", return_value=None):
            result = archive.read_file("nonexistent.txt")

        assert result is None

    @patch("builtins.open", new_callable=mock_open)
    def test_read_file_with_zero_size(self, mock_file):
        """Test reading a file with zero compressed size."""
        archive = MPQArchive("test.mpq")

        hash_entry = HashTableEntry(name1=1, name2=2, locale=0, platform=0, block_index=0)
        block_entry = BlockTableEntry(
            file_position=100,
            compressed_size=0,
            uncompressed_size=0,
            flags=MPQ_FILE_EXISTS,
        )

        archive._header = Header(
            magic="MPQ\x1a",
            header_size=32,
            archive_size=1024,
            format_version=0,
            block_size=3,
            hash_table_offset=100,
            block_table_offset=200,
            hash_table_size=1,
            block_table_size=1,
        )
        archive._block_table = Mock()
        archive._block_table.entries = [block_entry]

        with patch.object(archive, "get_hash_table_entry", return_value=hash_entry):
            result = archive.read_file("test.txt")

        assert result is None

    @patch("builtins.open", new_callable=mock_open)
    def test_read_encrypted_file_raises_error(self, mock_file):
        """Test that reading encrypted files raises NotImplementedError."""
        from icecap.infrastructure.resource.mpq.flags import MPQ_FILE_ENCRYPTED

        archive = MPQArchive("test.mpq")

        hash_entry = HashTableEntry(name1=1, name2=2, locale=0, platform=0, block_index=0)
        block_entry = BlockTableEntry(
            file_position=100,
            compressed_size=50,
            uncompressed_size=100,
            flags=MPQ_FILE_EXISTS | MPQ_FILE_ENCRYPTED,
        )

        archive._header = Header(
            magic="MPQ\x1a",
            header_size=32,
            archive_size=1024,
            format_version=0,
            block_size=3,
            hash_table_offset=100,
            block_table_offset=200,
            hash_table_size=1,
            block_table_size=1,
        )
        archive._block_table = Mock()
        archive._block_table.entries = [block_entry]

        mock_file.return_value.seek = Mock()
        mock_file.return_value.read.return_value = b"encrypted data"

        with patch.object(archive, "get_hash_table_entry", return_value=hash_entry):
            with pytest.raises(NotImplementedError, match="Encryption is not supported"):
                archive.read_file("test.txt")
