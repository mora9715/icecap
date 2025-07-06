from enum import Enum


class HashType(Enum):
    """Enumeration of hash types."""

    TABLE_OFFSET = 0
    HASH_A = 1
    HASH_B = 2
    TABLE = 3
