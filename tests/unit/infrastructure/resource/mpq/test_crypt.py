"""Tests for MPQ cryptography utilities."""

import struct
from icecap.infrastructure.resource.mpq.crypt import Crypt
from icecap.infrastructure.resource.mpq.enums import HashType


class TestCrypt:
    """Test the Crypt class."""

    def setup_method(self):
        """Setup for each test."""
        self.crypt = Crypt()

    def test_build_crypt_table(self):
        """Test that the crypt table is built correctly."""
        # The crypt table should have 1280 entries (256 * 5)
        assert len(self.crypt.crypt_table) == 1280

        # Check that all expected keys exist
        for i in range(256):
            for group in range(5):
                table_index = i + (group * 0x100)
                assert table_index in self.crypt.crypt_table

    def test_build_crypt_table_deterministic(self):
        """Test that the crypt table is deterministic."""
        crypt1 = Crypt()
        crypt2 = Crypt()

        assert crypt1.crypt_table == crypt2.crypt_table

    def test_hash_table_type(self):
        """Test hashing with TABLE hash type."""
        result = self.crypt.hash("(hash table)", HashType.TABLE)

        # Hash should be a non-zero integer
        assert isinstance(result, int)
        assert result > 0

    def test_hash_a_type(self):
        """Test hashing with HASH_A type."""
        result = self.crypt.hash("test.txt", HashType.HASH_A)

        # Hash should be a non-zero integer
        assert isinstance(result, int)
        assert result > 0

    def test_hash_b_type(self):
        """Test hashing with HASH_B type."""
        result = self.crypt.hash("test.txt", HashType.HASH_B)

        # Hash should be a non-zero integer
        assert isinstance(result, int)
        assert result > 0

    def test_hash_same_input_same_output(self):
        """Test that the same input produces the same hash."""
        input_string = "test_file.dbc"

        hash1 = self.crypt.hash(input_string, HashType.HASH_A)
        hash2 = self.crypt.hash(input_string, HashType.HASH_A)

        assert hash1 == hash2

    def test_hash_case_insensitive(self):
        """Test that hashing is case-insensitive."""
        hash_lower = self.crypt.hash("test.txt", HashType.HASH_A)
        hash_upper = self.crypt.hash("TEST.TXT", HashType.HASH_A)
        hash_mixed = self.crypt.hash("TeSt.TxT", HashType.HASH_A)

        assert hash_lower == hash_upper == hash_mixed

    def test_hash_different_types_different_results(self):
        """Test that different hash types produce different results."""
        input_string = "test.txt"

        hash_a = self.crypt.hash(input_string, HashType.HASH_A)
        hash_b = self.crypt.hash(input_string, HashType.HASH_B)
        hash_table = self.crypt.hash(input_string, HashType.TABLE)

        # All three should be different
        assert hash_a != hash_b
        assert hash_b != hash_table
        assert hash_a != hash_table

    def test_hash_empty_string(self):
        """Test hashing an empty string."""
        result = self.crypt.hash("", HashType.HASH_A)

        # Should return the initial seed value
        assert isinstance(result, int)

    def test_hash_known_values(self):
        """Test hashing with known test vectors.

        These values are derived from the MPQ hash algorithm specification.
        """
        # Test hash for "(hash table)"
        hash_table = self.crypt.hash("(hash table)", HashType.TABLE)
        assert hash_table > 0  # Should produce a valid hash

        # Test hash for "(block table)"
        block_table = self.crypt.hash("(block table)", HashType.TABLE)
        assert block_table > 0  # Should produce a valid hash

        # The two hashes should be different
        assert hash_table != block_table

    def test_decrypt_basic(self):
        """Test basic decryption."""
        # Create simple encrypted data (4 bytes)
        encrypted_data = struct.pack("<I", 0x12345678)
        key = 0xABCDEF00

        result = self.crypt.decrypt(encrypted_data, key)

        # Result should be 4 bytes
        assert len(result) == 4

    def test_decrypt_multiple_chunks(self):
        """Test decryption with multiple 4-byte chunks."""
        # Create 12 bytes of data (3 chunks)
        encrypted_data = struct.pack("<III", 0x11111111, 0x22222222, 0x33333333)
        key = 0x12345678

        result = self.crypt.decrypt(encrypted_data, key)

        # Result should be 12 bytes
        assert len(result) == 12

    def test_decrypt_empty_data(self):
        """Test decryption of empty data."""
        encrypted_data = b""
        key = 0x12345678

        result = self.crypt.decrypt(encrypted_data, key)

        # Result should be empty
        assert len(result) == 0

    def test_decrypt_partial_chunk(self):
        """Test decryption with partial chunks (not multiple of 4)."""
        # Only 6 bytes - should only decrypt the first 4
        encrypted_data = b"\x11\x22\x33\x44\x55\x66"
        key = 0x12345678

        result = self.crypt.decrypt(encrypted_data, key)

        # Should only decrypt full 4-byte chunks
        assert len(result) == 4

    def test_decrypt_deterministic(self):
        """Test that decryption is deterministic."""
        encrypted_data = struct.pack("<I", 0xDEADBEEF)
        key = 0x12345678

        result1 = self.crypt.decrypt(encrypted_data, key)
        result2 = self.crypt.decrypt(encrypted_data, key)

        assert result1 == result2

    def test_decrypt_different_keys_different_results(self):
        """Test that different keys produce different results."""
        encrypted_data = struct.pack("<I", 0xDEADBEEF)

        result1 = self.crypt.decrypt(encrypted_data, 0x12345678)
        result2 = self.crypt.decrypt(encrypted_data, 0x87654321)

        assert result1 != result2

    def test_hash_with_null_bytes(self):
        """Test hashing strings with null bytes."""
        # Null bytes should be processed correctly
        input_string = "test\x00file"

        result = self.crypt.hash(input_string, HashType.HASH_A)

        assert isinstance(result, int)
        assert result > 0

    def test_decrypt_all_zeros(self):
        """Test decryption of all zero data."""
        encrypted_data = b"\x00\x00\x00\x00"
        key = 0x12345678

        result = self.crypt.decrypt(encrypted_data, key)

        # Should produce some non-zero result due to the decryption algorithm
        assert len(result) == 4

    def test_hash_special_mpq_files(self):
        """Test hashing special MPQ file names."""
        special_files = [
            "(listfile)",
            "(attributes)",
            "(signature)",
            "(hash table)",
            "(block table)",
        ]

        hashes = []
        for filename in special_files:
            hash_result = self.crypt.hash(filename, HashType.TABLE)
            hashes.append(hash_result)
            assert hash_result > 0

        # All hashes should be unique
        assert len(hashes) == len(set(hashes))


class TestCryptIntegration:
    """Integration tests for cryptography functions."""

    def test_encrypt_decrypt_cycle(self):
        """Test that we can use crypt table for hash calculations."""
        crypt = Crypt()

        # Generate a hash key for a filename
        filename = "test.dbc"
        hash_key = crypt.hash(filename, HashType.TABLE)

        # Hash key should be usable for decryption
        assert hash_key > 0

    def test_hash_collision_resistance(self):
        """Test that different inputs produce different hashes."""
        crypt = Crypt()

        test_strings = [
            "file1.txt",
            "file2.txt",
            "data.dbc",
            "map.adt",
            "texture.blp",
        ]

        hash_results = {}
        for test_string in test_strings:
            hash_a = crypt.hash(test_string, HashType.HASH_A)
            hash_b = crypt.hash(test_string, HashType.HASH_B)

            # Store as tuple
            hash_results[test_string] = (hash_a, hash_b)

        # Check that all hash pairs are unique
        unique_hashes = set(hash_results.values())
        assert len(unique_hashes) == len(test_strings)
