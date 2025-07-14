"""The module provides tooling to manipulate game assets.

World of Warcraft assets are stored in MPQ archives. Depending on the archive name,
the assets are loaded with different priorities.

Currently, the module provides tools to load MPQ archives, list and extract individual
files from the archives.
"""

from .mpq import MPQArchive, MPQArchiveChain
from .dbc import DBCFile, MapRowWithDefinitions


__all__ = ["MPQArchive", "MPQArchiveChain", "DBCFile", "MapRowWithDefinitions"]
