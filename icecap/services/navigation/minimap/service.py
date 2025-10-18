import logging
from icecap.infrastructure.resource import MPQFileReader
from icecap.infrastructure.resource import DBCFile
from icecap.infrastructure.resource.dbc.definitions import MapRowWithDefinitions
import os
from io import BytesIO
from icecap.services.navigation.minimap.dto import MapTile, MapPosition, Map, Minimap

logger = logging.getLogger(__name__)


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

        logger.debug("Initializing MinimapService")
        self._md5_translate = self.load_md5_translate()
        self._map_database = self.load_map_database()
        logger.info("MinimapService initialized successfully")

    def load_md5_translate(self) -> dict[str, dict[str, str]]:
        logger.debug(f"Loading MD5 translate file: {self.MD5_TRANSLATE_FILE_PATH}")
        raw_file_contents = self.mpq_reader.read_file(self.MD5_TRANSLATE_FILE_PATH)
        if not raw_file_contents:
            logger.error("Failed to read md5translate.trs")
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

        logger.info(f"Loaded MD5 translate with {len(result)} directories")
        return result

    def load_map_database(self) -> DBCFile:
        logger.debug(f"Loading map database: {self.MAP_DATABASE_FILE_PATH}")
        raw_file_contents = self.mpq_reader.read_file(self.MAP_DATABASE_FILE_PATH)
        if not raw_file_contents:
            logger.error("Failed to read map.dbc")
            raise Exception("Failed to read map.dbc")

        dbc_file = DBCFile(BytesIO(raw_file_contents), MapRowWithDefinitions)
        logger.info(f"Loaded map database with {len(dbc_file.get_records())} maps")
        return dbc_file

    def build_minimap_texture_path(
        self, directory: str, map_block_x: int, map_block_y: int
    ) -> str | None:
        file_name = f"map{map_block_x}_{map_block_y}.blp"
        hashed_file_name = self._md5_translate.get(directory, {}).get(file_name)

        if not hashed_file_name:
            logger.debug(f"Texture not found for {directory}/{file_name}")
            return None

        texture_path = self.TEXTURES_DIRECTORY + "\\" + hashed_file_name
        logger.debug(f"Built texture path: {texture_path}")
        return texture_path

    def get_minimap(self) -> Minimap:
        """
        Constructs and returns a minimap containing map tiles for various map records.

        Returns:
            Minimap: An object containing a collection of maps with their respective tiles.
        """
        logger.info("Building minimap from map database")
        maps: dict[int, Map] = {}
        total_tiles = 0

        for record in self._map_database.get_records():
            map_id = getattr(record, "map_id")
            directory = getattr(record, "directory")
            maps[map_id] = Map(map_id=map_id, tiles={})

            tiles_for_map = 0
            for i in range(64):
                for j in range(64):
                    texture_path = self.build_minimap_texture_path(directory, i, j)

                    if not texture_path:
                        continue

                    map_position = MapPosition(x=i, y=j)
                    maps[map_id].tiles[map_position] = MapTile(
                        position=map_position,
                        texture_path=texture_path,
                        mpq_reader=self.mpq_reader,
                    )
                    tiles_for_map += 1
                    total_tiles += 1

            logger.debug(f"Map {map_id} ({directory}): loaded {tiles_for_map} tiles")

        logger.info(f"Minimap built with {len(maps)} maps and {total_tiles} total tiles")
        return Minimap(maps=maps)
