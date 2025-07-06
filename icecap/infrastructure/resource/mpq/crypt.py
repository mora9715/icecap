from io import BytesIO
import struct

from .enums import HashType


class Crypt:
    def __init__(self):
        self.crypt_table = self.build_crypt_table()

    def hash(self, value: str, hash_type: HashType) -> int:
        """
        Generate a hash value for a given string using the specified hash type.

        This implements a custom hash algorithm that processes each character
        of the input string and combines it with values from the cryptographic
        lookup table to produce a final hash value.
        """
        # Initial seed values for the hash algorithm
        initial_seed1 = 0x7FED7FED
        initial_seed2 = 0xEEEEEEEE
        hash_type_offset = 8  # Left shift for the hash type in the table lookup
        seed2_shift = 5  # Left shift for seed2 in accumulation
        seed2_increment = 3  # Constant added to seed2
        mask_32_bit = 0xFFFFFFFF  # Mask to keep values within the 32-bit range

        hash_seed1 = initial_seed1
        hash_seed2 = initial_seed2

        # Process each character in the uppercase string
        normalized_value = value.upper()

        for character in normalized_value:
            # Get character code (handle both string chars and int values)
            char_code = ord(character) if isinstance(character, str) else character

            # Calculate table index: (hash_type << 8) + character_code
            table_index = (hash_type.value << hash_type_offset) + char_code

            # Get the cryptographic value from the lookup table
            crypt_value = self.crypt_table[table_index]

            # Update the first hash seed using XOR with combined seeds
            hash_seed1 = (crypt_value ^ (hash_seed1 + hash_seed2)) & mask_32_bit

            # Update the second hash seed using character code and both seeds
            hash_seed2 = (
                char_code + hash_seed1 + hash_seed2 + (hash_seed2 << seed2_shift) + seed2_increment
            ) & mask_32_bit

        return hash_seed1

    def decrypt(self, data: bytes, key: int) -> bytes:
        """
        Decrypt encrypted resource using a custom decryption algorithm.

        This method processes the resource in 4-byte chunks, using two seeds that are
        updated with each iteration. The decryption uses values from the cryptographic
        lookup table combined with XOR operations and seed transformations.
        """
        # Constants for the decryption algorithm
        initial_seed2 = 0xEEEEEEEE
        crypt_table_offset = 0x400  # Offset for decryption table entries
        seed1_constant = 0x11111111  # Constant added during seed1 transformation
        seed1_left_shift = 0x15  # Left shift (21 bits) for seed1
        seed1_right_shift = 0x0B  # Right shift (11 bits) for seed1
        seed2_left_shift = 5  # Left shift for seed2 in accumulation
        seed2_increment = 3  # Constant added to seed2
        mask_32_bit = 0xFFFFFFFF  # Mask to keep values within 32-bit range
        mask_8_bit = 0xFF  # Mask for lower 8 bits
        bytes_per_chunk = 4  # Process resource in 4-byte chunks

        # Initialize decryption seeds
        decrypt_seed1 = key
        decrypt_seed2 = initial_seed2

        # Use BytesIO for efficient byte operations
        decrypted_result = BytesIO()

        # Calculate the number of 4-byte chunks to process
        num_chunks = len(data) // bytes_per_chunk

        for chunk_index in range(num_chunks):
            # Update the second seed using crypt table lookup
            table_index = crypt_table_offset + (decrypt_seed1 & mask_8_bit)
            decrypt_seed2 = (decrypt_seed2 + self.crypt_table[table_index]) & mask_32_bit

            # Extract the 4-byte chunk from resource and convert to integer
            chunk_start = chunk_index * bytes_per_chunk
            chunk_end = chunk_start + bytes_per_chunk
            encrypted_chunk = data[chunk_start:chunk_end]
            encrypted_value = struct.unpack("<I", encrypted_chunk)[0]

            # Decrypt the value using XOR with combined seeds
            decrypted_value = (encrypted_value ^ (decrypt_seed1 + decrypt_seed2)) & mask_32_bit

            # Transform first seed using bitwise operations
            # This creates a complex transformation: invert, shift left,
            #   add constant, OR with right shift
            seed1_inverted = ~decrypt_seed1
            seed1_left_part = (seed1_inverted << seed1_left_shift) + seed1_constant
            seed1_right_part = decrypt_seed1 >> seed1_right_shift
            decrypt_seed1 = (seed1_left_part | seed1_right_part) & mask_32_bit

            # Update the second seed using decrypted value and accumulation
            decrypt_seed2 = (
                decrypted_value
                + decrypt_seed2
                + (decrypt_seed2 << seed2_left_shift)
                + seed2_increment
            ) & mask_32_bit

            # Write decrypted 4-byte chunk to result
            decrypted_result.write(struct.pack("<I", decrypted_value))

        return decrypted_result.getvalue()

    def build_crypt_table(self) -> dict:
        """
        Build a cryptographic lookup table with 1280 entries (256 * 5).

        The table is organized in 5 groups of 256 entries each, where each group
        starts at offsets 0x000, 0x100, 0x200, 0x300, and 0x400.
        """
        initial_seed = 0x00100001
        multiplier = 125
        increment = 3
        modulus = 0x2AAAAB
        mask_16_bit = 0xFFFF
        group_offset = 0x100
        groups_per_index = 5
        table_size = 256

        current_seed = initial_seed
        crypt_table = {}

        for base_index in range(table_size):
            table_index = base_index

            # Generate 5 entries for each base index (at different offsets)
            for group in range(groups_per_index):
                # Generate high 16 bits
                current_seed = (current_seed * multiplier + increment) % modulus
                high_bits = (current_seed & mask_16_bit) << 16

                # Generate low 16 bits
                current_seed = (current_seed * multiplier + increment) % modulus
                low_bits = current_seed & mask_16_bit

                # Combine high and low bits to create the final hash value
                hash_value = high_bits | low_bits
                crypt_table[table_index] = hash_value

                # Move to the next group (add 256 to index)
                table_index += group_offset

        return crypt_table
