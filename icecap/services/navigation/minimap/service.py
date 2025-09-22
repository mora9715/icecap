from icecap.infrastructure.resource import MPQFileReader
from icecap.infrastructure.resource import DBCFile
from icecap.infrastructure.resource.dbc.definitions import MapRowWithDefinitions
import os
from io import BytesIO
from icecap.services.navigation.minimap.dto import MapTile, MapPosition, Map, Minimap


class MinimapService:
    """
    Provides tooling to manage and interact with the minimap system in the application.

    This class is designed to interact with map-related files to load, parse, and manage
    minimap data using data from the game's MPQ archive files.
    """

    # File paths
    TEXTURES_DIRECTORY = r"textures\Minimap"
    MD5_TRANSLATE_FILE_PATH = TEXTURES_DIRECTORY + r"\md5translate.trs"
    MAP_DATABASE_FILE_PATH = r"DBFilesClient\Map.dbc"

    def __init__(self, mpq_reader: MPQFileReader):
        self.mpq_reader = mpq_reader

        self._md5_translate = self.load_md5_translate()
        self._map_database = self.load_map_database()

    def load_md5_translate(self) -> dict[str, dict[str, str]]:
        raw_file_contents = self.mpq_reader.read_file(self.MD5_TRANSLATE_FILE_PATH)
        if not raw_file_contents:
            raise Exception("Failed to read md5translate.trs")

        file_contents = raw_file_contents.decode("utf-8")

        result: dict[str, dict[str, str]] = {}
        current_dir = None

        for line in file_contents.splitlines():
            if line.startswith("dir: "):
                current_dir = line[5:]
                result[current_dir] = {}
            elif current_dir is not None and line.strip():
                file_path, md5_filename = line.split("\t")
                file_name = os.path.basename(file_path)

                result[current_dir][file_name] = md5_filename

        return result

    def load_map_database(self) -> DBCFile:
        raw_file_contents = self.mpq_reader.read_file(self.MAP_DATABASE_FILE_PATH)
        if not raw_file_contents:
            raise Exception("Failed to read map.dbc")

        return DBCFile(BytesIO(raw_file_contents), MapRowWithDefinitions)

    def build_minimap_texture_path(
        self, directory: str, map_block_x: int, map_block_y: int
    ) -> str | None:
        file_name = f"map{map_block_x}_{map_block_y}.blp"
        hashed_file_name = self._md5_translate.get(directory, {}).get(file_name)

        if not hashed_file_name:
            return None

        return self.TEXTURES_DIRECTORY + "\\" + hashed_file_name

    def get_minimap(self) -> Minimap:
        """
        Constructs and returns a minimap containing map tiles for various map records.

        Returns:
            Minimap: An object containing a collection of maps with their respective tiles.
        """
        maps: dict[int, Map] = {}
        for record in self._map_database.get_records():
            map_id = getattr(record, "map_id")
            directory = getattr(record, "directory")
            maps[map_id] = Map(map_id=map_id, tiles={})

            for i in range(64):
                for j in range(64):
                    texture_path = self.build_minimap_texture_path(directory, i, j)

                    if not texture_path:
                        continue

                    map_position = MapPosition(x=i, y=j)
                    maps[map_id].tiles[map_position] = MapTile(
                        position=map_position, texture_path=texture_path, mpq_reader=self.mpq_reader
                    )

        return Minimap(maps=maps)
