import struct
import zlib
import bz2
from io import BytesIO
from .dto import Header, HeaderExtension, HashTable, BlockTable, HashTableEntry, BlockTableEntry

from .crypt import Crypt
from .enums import HashType

from .flags import (
    MPQ_FILE_EXISTS,
    MPQ_FILE_ENCRYPTED,
    MPQ_FILE_SINGLE_UNIT,
    MPQ_FILE_SECTOR_CRC,
    MPQ_FILE_COMPRESS,
)


class MPQArchive:
    """Represents an MPQ archive.

    MPQ is a proprietary archive format used by Blizzard Entertainment.
    Read more about it here: https://wowdev.wiki/MPQ

    The implementation is very naive and most likely won't work with post-WOTLK expansions.
    """

    def __init__(self, path: str):
        self.file_path = path

        self.file = open(path, "rb")
        self.crypt = Crypt()

        self._header: Header | None = None
        self._hash_table: HashTable | None = None
        self._block_table: BlockTable | None = None
        self._file_names: list[str] | None = None

    def get_file_names(self) -> list[str]:
        """Get a list of file names in the archive.

        The list is lazily loaded the first time this method is called.
        """
        if self._file_names:
            return self._file_names

        listfile_data = self.read_file("(listfile)")

        if listfile_data is None:
            self._file_names = []
            return self._file_names

        self._file_names = listfile_data.decode().splitlines()

        return self._file_names

    def get_header(self) -> Header:
        """Get the MPQ header.

        The header contains metadata about the archive.
        The header is lazily loaded the first time this method is called.
        """
        if self._header:
            return self._header

        magic = self.file.read(4)
        self.file.seek(0)

        if magic == b"MPQ\x1b":
            raise ValueError("MPQ shunts are not supported.")
        elif magic != b"MPQ\x1a":
            raise ValueError("Invalid MPQ header.")

        data = self.file.read(32)
        header = Header(*struct.unpack("<4s2I2H4I", data))
        if header.format_version == 1:
            header_extension_data = self.file.read(12)
            header.extension = HeaderExtension(*struct.unpack("<q2h", header_extension_data))
        if header.format_version > 1:
            raise ValueError("Unsupported MPQ format version.")

        self._header = header
        return self._header

    def get_hash_table(self) -> HashTable:
        """Get the hash table of the archive.

        This is a classical hash table used to quickly locate files in the archive.
        """
        if self._hash_table:
            return self._hash_table

        header = self.get_header()

        key = self.crypt.hash("(hash table)", HashType.TABLE)

        self.file.seek(header.hash_table_offset)
        data = self.file.read(header.hash_table_size * 16)
        data = self.crypt.decrypt(data, key)

        def unpack_entry(position):
            entry_data = data[position * 16 : position * 16 + 16]
            return HashTableEntry(*struct.unpack("<2I2HI", entry_data))

        self._hash_table = HashTable([unpack_entry(i) for i in range(header.hash_table_size)])
        return self._hash_table

    def get_block_table(self) -> BlockTable:
        """Get the block table of the archive.

        The block table contains metadata about the position and size of each file in the archive.
        """
        if self._block_table:
            return self._block_table

        header = self.get_header()

        key = self.crypt.hash("(block table)", HashType.TABLE)

        self.file.seek(header.block_table_offset)
        data = self.file.read(header.block_table_size * 16)
        data = self.crypt.decrypt(data, key)

        def unpack_entry(position):
            entry_data = data[position * 16 : position * 16 + 16]
            return BlockTableEntry(*struct.unpack("<4I", entry_data))

        self._block_table = BlockTable([unpack_entry(i) for i in range(header.block_table_size)])
        return self._block_table

    def get_hash_table_entry(self, filename: str) -> HashTableEntry | None:
        """Get the hash table entry corresponding to a given filename."""
        hash_a = self.crypt.hash(filename, HashType.HASH_A)
        hash_b = self.crypt.hash(filename, HashType.HASH_B)

        for entry in self.get_hash_table().entries:
            if entry.name1 == hash_a and entry.name2 == hash_b:
                return entry

        return None

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in the archive."""
        return self.get_hash_table_entry(filename) is not None

    def _decompress_data(self, data: bytes) -> bytes:
        compression_type = ord(data[0:1])
        if compression_type == 0:
            return data
        elif compression_type == 2:
            return zlib.decompress(data[1:], 15)
        elif compression_type == 16:
            return bz2.decompress(data[1:])
        else:
            raise RuntimeError(f"Unsupported compression type: {compression_type}")

    def _process_multi_sector_file(
        self, file_data: bytes, block_entry: BlockTableEntry, block_size: int
    ) -> bytes:
        sector_size = 512 << block_size
        sectors = block_entry.uncompressed_size // sector_size + 1

        # Check if the file has CRC checksums
        has_crc = bool(block_entry.flags & MPQ_FILE_SECTOR_CRC)
        if has_crc:
            sectors += 1

        # Unpack sector positions
        positions = struct.unpack(f"<{sectors + 1}I", file_data[: 4 * (sectors + 1)])

        # Process each sector
        result = BytesIO()
        sector_bytes_left = block_entry.uncompressed_size
        for i in range(len(positions) - (2 if has_crc else 1)):
            sector = file_data[positions[i] : positions[i + 1]]

            # Decompress sector if needed
            if block_entry.flags & MPQ_FILE_COMPRESS and (sector_bytes_left > len(sector)):
                sector = self._decompress_data(sector)

            sector_bytes_left -= len(sector)
            result.write(sector)

        return result.getvalue()

    def _process_single_unit_file(self, file_data: bytes, block_entry: BlockTableEntry) -> bytes:
        if block_entry.flags & MPQ_FILE_COMPRESS and (
            block_entry.uncompressed_size > block_entry.compressed_size
        ):
            file_data = self._decompress_data(file_data)

        return file_data

    def read_file(self, filename: str) -> bytes | None:
        """
        Read a file from the MPQ archive.
        """
        # Get file metadata
        hash_entry = self.get_hash_table_entry(filename)
        if hash_entry is None:
            return None

        header = self.get_header()
        block_table = self.get_block_table()
        block_entry = block_table.entries[hash_entry.block_index]

        # Check if the file exists and has content
        if not (block_entry.flags & MPQ_FILE_EXISTS):
            return None

        if block_entry.compressed_size == 0:
            return None

        # Read file resource
        self.file.seek(block_entry.file_position)
        file_data = self.file.read(block_entry.compressed_size)

        # Check for encryption
        if block_entry.flags & MPQ_FILE_ENCRYPTED:
            raise NotImplementedError("Encryption is not supported yet.")

        # Process file based on its structure
        if block_entry.flags & MPQ_FILE_SINGLE_UNIT:
            return self._process_single_unit_file(file_data, block_entry)
        else:
            return self._process_multi_sector_file(file_data, block_entry, header.block_size)

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass
