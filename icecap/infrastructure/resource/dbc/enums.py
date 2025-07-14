from enum import Enum, auto


class DBCFieldType(Enum):
    """Enumeration of field types supported in DBC files"""

    INT = auto()  # 32-bit signed integer
    UINT = auto()  # 32-bit unsigned integer
    FLOAT = auto()  # 32-bit floating point
    STRING = auto()  # String reference (offset into string block)
    BOOLEAN = auto()  # Boolean stored as 32-bit integer (0 or 1)
    LOCALIZED_STRING = auto()  # Multiple string references for different locales


class DBCLocale(Enum):
    """Supported locales in World of Warcraft"""

    enUS = 0
    koKR = 1
    frFR = 2
    deDE = 3
    zhCN = 4
    zhTW = 5
    esES = 6
    esMX = 7
    ruRU = 8
