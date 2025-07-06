from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HeaderExtension:
    extended_block_table_offset: int
    hash_table_offset_high: int
    block_table_offset_high: int


@dataclass(slots=True)
class Header:
    magic: str
    header_size: int
    archive_size: int
    format_version: int
    block_size: int
    hash_table_offset: int
    block_table_offset: int
    hash_table_size: int
    block_table_size: int
    extension: HeaderExtension | None = None


@dataclass(frozen=True, slots=True)
class HashTableEntry:
    name1: int
    name2: int
    locale: int
    platform: int
    block_index: int


@dataclass(frozen=True, slots=True)
class HashTable:
    entries: list[HashTableEntry]


@dataclass(frozen=True, slots=True)
class BlockTableEntry:
    file_position: int
    compressed_size: int
    uncompressed_size: int
    flags: int


@dataclass(frozen=True, slots=True)
class BlockTable:
    entries: list[BlockTableEntry]
