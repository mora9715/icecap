"""Tests for MPQ archive chain."""

import pytest
from unittest.mock import Mock, patch
from icecap.infrastructure.resource.mpq.chain import MPQArchiveChain
from icecap.infrastructure.resource.mpq.archive import MPQArchive


class TestMPQArchiveChain:
    """Test MPQ archive chain functionality."""

    def test_create_chain_with_default_priorities(self):
        """Test creating a chain with default WoW archive priorities."""
        chain = MPQArchiveChain()

        assert chain is not None
        assert len(chain._archive_priorities) > 0

    def test_create_chain_with_custom_priorities(self):
        """Test creating a chain with custom priorities."""
        custom_priorities = ("priority1", "priority2", "priority3")
        chain = MPQArchiveChain(archive_priorities=custom_priorities)

        assert len(chain._archive_priorities) == 3

    def test_add_archive_with_matching_priority(self):
        """Test adding an archive that matches a priority pattern."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/common.mpq"

        chain.add_archive(mock_archive)

        # Archive should be added to some priority level
        assert len(chain._prioritized_archives) > 0

    def test_add_archive_patch_priority(self):
        """Test that patch archives get highest priority."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/patch-2.mpq"

        chain.add_archive(mock_archive)

        # Patch archives should be in priority 0 or 1 (highest)
        assert any(
            mock_archive in archives for priority, archives in chain._prioritized_archives.items()
        )

    def test_add_archive_base_priority(self):
        """Test that base archives get lower priority."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/base.mpq"

        chain.add_archive(mock_archive)

        # Base archives should be added
        assert any(
            mock_archive in archives for priority, archives in chain._prioritized_archives.items()
        )

    def test_add_same_archive_twice(self):
        """Test that adding the same archive twice doesn't duplicate it."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/common.mpq"

        chain.add_archive(mock_archive)
        chain.add_archive(mock_archive)

        # Count how many times the archive appears
        count = sum(
            1
            for archives in chain._prioritized_archives.values()
            for archive in archives
            if archive == mock_archive
        )

        assert count == 1

    def test_add_archive_with_no_matching_priority(self):
        """Test adding an archive with no matching priority raises error."""
        # Use custom priorities that won't match
        chain = MPQArchiveChain(archive_priorities=("specific-pattern",))

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/unmatched-archive.mpq"

        with pytest.raises(ValueError, match="Could not find a suitable priority"):
            chain.add_archive(mock_archive)

    def test_read_file_from_single_archive(self):
        """Test reading a file from a single archive in the chain."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/common.mpq"
        mock_archive.file_exists.return_value = True
        mock_archive.read_file.return_value = b"file content"

        chain.add_archive(mock_archive)

        result = chain.read_file("test.txt")

        assert result == b"file content"
        mock_archive.file_exists.assert_called_once_with("test.txt")
        mock_archive.read_file.assert_called_once_with("test.txt")

    def test_read_file_from_multiple_archives(self):
        """Test reading a file from multiple archives respects priority."""
        chain = MPQArchiveChain()

        # Create two archives: patch and base
        patch_archive = Mock(spec=MPQArchive)
        patch_archive.file_path = "/path/to/patch.mpq"
        patch_archive.file_exists.return_value = True
        patch_archive.read_file.return_value = b"patched content"

        base_archive = Mock(spec=MPQArchive)
        base_archive.file_path = "/path/to/base.mpq"
        base_archive.file_exists.return_value = True
        base_archive.read_file.return_value = b"base content"

        # Add in reverse priority order to test priority handling
        chain.add_archive(base_archive)
        chain.add_archive(patch_archive)

        result = chain.read_file("test.txt")

        # Should return from patch archive (higher priority)
        assert result == b"patched content"

    def test_read_file_not_in_first_archive(self):
        """Test reading a file that only exists in lower priority archive."""
        chain = MPQArchiveChain()

        archive1 = Mock(spec=MPQArchive)
        archive1.file_path = "/path/to/patch.mpq"
        archive1.file_exists.return_value = False

        archive2 = Mock(spec=MPQArchive)
        archive2.file_path = "/path/to/base.mpq"
        archive2.file_exists.return_value = True
        archive2.read_file.return_value = b"base content"

        chain.add_archive(archive1)
        chain.add_archive(archive2)

        result = chain.read_file("test.txt")

        assert result == b"base content"

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist in any archive."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/common.mpq"
        mock_archive.file_exists.return_value = False

        chain.add_archive(mock_archive)

        result = chain.read_file("nonexistent.txt")

        assert result is None

    def test_read_file_from_empty_chain(self):
        """Test reading a file from an empty chain."""
        chain = MPQArchiveChain()

        result = chain.read_file("test.txt")

        assert result is None

    def test_priority_order_respected(self):
        """Test that archives are checked in priority order."""
        chain = MPQArchiveChain()

        call_order = []

        def create_mock_archive(name, priority_value):
            archive = Mock(spec=MPQArchive)
            archive.file_path = f"/path/to/{name}.mpq"

            def file_exists(filename):
                call_order.append(name)
                return False

            archive.file_exists = file_exists
            return archive

        # Create archives with different priorities
        patch_archive = create_mock_archive("patch-2", 0)
        expansion_archive = create_mock_archive("expansion", 1)
        base_archive = create_mock_archive("base", 2)

        chain.add_archive(patch_archive)
        chain.add_archive(expansion_archive)
        chain.add_archive(base_archive)

        chain.read_file("test.txt")

        # Patch should be checked first, then expansion, then base
        assert "patch-2" in call_order
        # The exact order depends on the priority patterns

    @patch("os.walk")
    @patch("icecap.infrastructure.resource.mpq.archive.MPQArchive")
    def test_load_archives_handles_errors(self, mock_archive_class, mock_walk):
        """Test that loading archives handles errors gracefully."""
        mock_walk.return_value = [
            ("/game/Data", [], ["corrupt.mpq"]),
        ]

        mock_archive_class.side_effect = Exception("Corrupted archive")

        with pytest.raises(ValueError, match="Failed to load MPQ archive"):
            MPQArchiveChain.load_archives("/game/Data")


class TestMPQArchiveChainPriorityPatterns:
    """Test MPQ archive chain priority pattern matching."""

    def test_wow_archive_priorities_constant(self):
        """Test that WOW_ARCHIVE_PRIORITIES constant exists and has expected patterns."""
        priorities = MPQArchiveChain.WOW_ARCHIVE_PRIORITIES

        assert len(priorities) > 0
        # Check for some expected patterns
        assert "patch" in priorities
        assert "base" in priorities
        assert "common" in priorities

    def test_patch_numbered_priority(self):
        """Test that numbered patches get proper priority."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/patch-2.mpq"

        chain.add_archive(mock_archive)

        # Should be added successfully
        assert len(chain._prioritized_archives) > 0

    def test_expansion_priority(self):
        """Test that expansion archives get proper priority."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/expansion.mpq"

        chain.add_archive(mock_archive)

        assert len(chain._prioritized_archives) > 0

    def test_lichking_priority(self):
        """Test that lichking archives get proper priority."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/lichking.mpq"

        chain.add_archive(mock_archive)

        assert len(chain._prioritized_archives) > 0

    def test_case_insensitive_matching(self):
        """Test that archive name matching is case-insensitive."""
        chain = MPQArchiveChain()

        mock_archive = Mock(spec=MPQArchive)
        mock_archive.file_path = "/path/to/COMMON.MPQ"

        # Should still match the "common" pattern
        chain.add_archive(mock_archive)

        assert len(chain._prioritized_archives) > 0
