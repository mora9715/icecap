from typing import Type

import struct

from .dto import DBCColumnDefinition, DBCHeader, DBCRowWithDefinitions
from .enums import DBCFieldType, DBCLocale


class DBCFile:
    HEADER_SIGNATURE = "WDBC"
    HEADER_SIZE = 20

    def __init__(self, path: str, row_prototype: Type[DBCRowWithDefinitions]):
        self.path = path
        self.row_prototype = row_prototype

        self._header: DBCHeader | None = None
        self._records: list[DBCRowWithDefinitions] | None = None

        self.column_definitions = (
            row_prototype.get_definitions()
            or DBCColumnDefinition.generate_default_definitions(self.get_header().field_count)
        )

        self.file = open(path, "rb")

    def get_header(self) -> DBCHeader:
        if self._header:
            return self._header

        self.file.seek(0)

        unpacked_data = struct.unpack("<4s4I", self.file.read(self.HEADER_SIZE))

        self._header = DBCHeader(
            signature=unpacked_data[0].decode(),
            record_count=unpacked_data[1],
            field_count=unpacked_data[2],
            record_size=unpacked_data[3],
            string_block_size=unpacked_data[4],
        )

        if self._header.signature != self.HEADER_SIGNATURE:
            raise ValueError("Invalid DBC file signature.")

        return self._header

    def get_records(self) -> list[DBCRowWithDefinitions]:
        if self._records:
            return self._records

        records = []

        header = self.get_header()

        record_data_size = header.record_count * header.record_size

        self.file.seek(self.HEADER_SIZE)

        records_data = self.file.read(record_data_size)
        string_block = self.file.read(header.string_block_size)

        for i in range(header.record_count):
            offset = i * header.record_size
            record_data = records_data[offset : offset + header.record_size]

            position = 0

            column_values = []

            for column_definition in self.column_definitions:
                field_values = []

                for _ in range(column_definition.array_size):
                    if column_definition.field_type == DBCFieldType.INT:
                        value = struct.unpack_from("<i", record_data, position)[0]
                        position += 4
                    elif column_definition.field_type == DBCFieldType.UINT:
                        value = struct.unpack_from("<I", record_data, position)[0]
                        position += 4
                    elif column_definition.field_type == DBCFieldType.FLOAT:
                        value = struct.unpack_from("<f", record_data, position)[0]
                        position += 4
                    elif column_definition.field_type == DBCFieldType.BOOLEAN:
                        value = bool(struct.unpack_from("<I", record_data, position)[0])
                        position += 4
                    elif column_definition.field_type == DBCFieldType.STRING:
                        string_offset = struct.unpack_from("<I", record_data, position)[0]
                        value = self._get_string(string_block, string_offset)
                        position += 4
                    elif column_definition.field_type == DBCFieldType.LOCALIZED_STRING:
                        localized_values = {}
                        for locale in DBCLocale:
                            string_offset = struct.unpack_from("<I", record_data, position)[0]
                            localized_values[locale] = self._get_string(string_block, string_offset)
                            position += 4
                        value = localized_values
                    else:
                        raise ValueError(f"Unknown field type: {column_definition.field_type}")

                    field_values.append(value)

                if column_definition.array_size > 1:
                    column_values.append(field_values)
                else:
                    column_values.append(field_values[0])

            records.append(self.row_prototype(*column_values))

        self._records = records
        return self._records

    def _get_string(self, string_block: bytes, offset: int) -> str:
        if offset == 0:  # Empty string
            return ""

        # Find the null terminator
        end = offset
        while end < len(string_block) and string_block[end] != 0:
            end += 1

        return string_block[offset:end].decode("utf-8")

    def __del__(self):
        try:
            self.file.close()
        except Exception:
            pass
