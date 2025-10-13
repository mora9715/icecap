"""Base test classes for IceCap tests."""

import pytest


class BaseTestCase:
    """Base class for all test cases with common setup/teardown."""

    pass


class MemoryTestCase(BaseTestCase):
    """Base class for tests requiring memory management mocking."""

    @pytest.fixture
    def mock_memory_manager(self):
        """Provides a mocked MemoryManager (override in conftest.py)."""
        pass

    @pytest.fixture
    def mock_process_manager(self):
        """Provides a mocked GameProcessManager (override in conftest.py)."""
        pass


class FileResourceTestCase(BaseTestCase):
    """Base class for tests involving file resources (MPQ, DBC)."""

    @pytest.fixture
    def sample_data_dir(self, tmp_path):
        """Provides temporary directory with sample files."""
        return tmp_path
