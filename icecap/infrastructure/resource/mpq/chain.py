import re
import os.path
from .archive import MPQArchive


class MPQArchiveChain:
    """The class allows reading files from multiple archives in a priority order.

    The service checks the highest priority archive first.

    Default priorities are set to the WOW archive name priorities.
    """

    WOW_ARCHIVE_PRIORITIES = (
        r"patch-([a-z]+)-(\d+)",
        r"patch-(\d+)",
        "patch",
        r"lichking-([a-z]+)",
        r"lichking",
        r"expansion-([-a-z]+)",
        "expansion",
        r"base-([a-z]+)",
        "base",
        r"locale-([a-z]+)",
        r"common-(\d+)",
        "common",
        ".*",
    )

    def __init__(self, archive_priorities: tuple[str, ...] = WOW_ARCHIVE_PRIORITIES):
        self._prioritized_archives: dict[int, list[MPQArchive]] = {}
        self._archive_priorities: list[re.Pattern] = [
            re.compile(pattern) for pattern in archive_priorities
        ]

    def add_archive(self, archive: MPQArchive):
        """Add an archive to the chain."""
        archive_name = os.path.split(archive.file_path)[-1].lower().rstrip(".mpq")

        for number, priority_regex in enumerate(self._archive_priorities):
            if not priority_regex.match(archive_name):
                continue

            if not self._prioritized_archives.get(number):
                self._prioritized_archives[number] = []

            if archive not in self._prioritized_archives[number]:
                self._prioritized_archives[number].append(archive)
            return

        raise ValueError(f"Could not find a suitable priority for archive '{archive_name}'")

    def read_file(self, filename: str) -> bytes | None:
        """Read a file from the chain.

        The file is searched in the archives in the priority order.
        """
        for priority in sorted(self._prioritized_archives.keys()):
            for archive in self._prioritized_archives[priority]:
                if archive.file_exists(filename):
                    return archive.read_file(filename)

        return None
