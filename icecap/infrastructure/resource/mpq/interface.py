from typing import Protocol


class MPQFileReader(Protocol):
    def read_file(self, filename: str) -> bytes | None: ...
