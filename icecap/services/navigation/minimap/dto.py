from PIL import Image
from PIL.Image import Image as PILImage
from dataclasses import dataclass
from functools import cached_property
from io import BytesIO

from icecap.domain.dto import Position
from icecap.constants import MAX_MAP_COORDINATE, WORLD_TILE_SIZE, MINIMAP_TILE_SIZE

from icecap.infrastructure.resource import MPQFileReader


@dataclass(slots=True, frozen=True)
class MapPosition:
    x: int
    y: int

    @classmethod
    def from_entity_position(cls, position: Position) -> "MapPosition":
        x_tile = (MAX_MAP_COORDINATE - position.x) / WORLD_TILE_SIZE
        y_tile = (MAX_MAP_COORDINATE - position.y) / WORLD_TILE_SIZE

        return MapPosition(int(x_tile), int(y_tile))


@dataclass(frozen=True)
class MapTile:
    position: MapPosition

    texture_path: str

    mpq_reader: MPQFileReader

    @cached_property
    def image(self) -> PILImage:
        texture_data = self.mpq_reader.read_file(self.texture_path)
        if texture_data is None:
            return Image.new("RGBA", (256, 256), (0, 0, 0, 0))

        image: PILImage = Image.open(BytesIO(texture_data))

        if image.mode != "RGBA":
            image = image.convert("RGBA")

        return image


@dataclass()
class Map:
    map_id: int

    tiles: dict[MapPosition, MapTile]


@dataclass()
class Minimap:
    """Data class representing the minimap."""

    maps: dict[int, Map]

    def render(self, map_id: int, position: Position, extent_pixels: int = 0) -> PILImage:
        """
        Render a minimap centered at the given position with the specified radius in pixels.

        Args:
            map_id: The ID of the map
            position: The center position (entity position)
            extent_pixels: The extent in pixels (0 for a single tile)

        Returns:
            A PIL Image of the minimap centered on the position
        """
        map_obj = self.maps.get(map_id)
        if map_obj is None:
            return Image.new(
                "RGBA",
                (2 * extent_pixels, 2 * extent_pixels)
                if extent_pixels > 0
                else (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE),
                (0, 0, 0, 0),
            )

        # Convert position to MapPosition
        map_position = MapPosition.from_entity_position(position)

        # Calculate the exact position within the tile
        exact_x = (MAX_MAP_COORDINATE - position.x) / WORLD_TILE_SIZE
        exact_y = (MAX_MAP_COORDINATE - position.y) / WORLD_TILE_SIZE

        # Calculate the pixel offset within the tile
        pixel_offset_x = (exact_x - int(exact_x)) * MINIMAP_TILE_SIZE
        pixel_offset_y = (exact_y - int(exact_y)) * MINIMAP_TILE_SIZE

        if extent_pixels == 0:
            tile = map_obj.tiles.get(map_position)
            if tile is None:
                return Image.new("RGBA", (MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE), (0, 0, 0, 0))

            return tile.image

        # Calculate how many tiles we need in each direction
        tiles_needed_x = (extent_pixels + pixel_offset_x) // MINIMAP_TILE_SIZE
        tiles_needed_y = (extent_pixels + pixel_offset_y) // MINIMAP_TILE_SIZE
        tiles_needed = int(max(tiles_needed_x, tiles_needed_y))

        # Calculate the size of the temporary image before cropping
        matrix_size = 2 * tiles_needed + 1
        temp_size = int(matrix_size * MINIMAP_TILE_SIZE)
        temp_image = Image.new("RGBA", (temp_size, temp_size), (0, 0, 0, 0))

        for y_offset in range(-tiles_needed, tiles_needed + 1):
            for x_offset in range(-tiles_needed, tiles_needed + 1):
                current_pos = MapPosition(map_position.x + x_offset, map_position.y + y_offset)

                tile = map_obj.tiles.get(current_pos)

                matrix_x = x_offset + tiles_needed
                matrix_y = y_offset + tiles_needed

                pos_x = matrix_x * MINIMAP_TILE_SIZE
                pos_y = matrix_y * MINIMAP_TILE_SIZE

                if tile is not None:
                    tile_image = tile.image
                    temp_image.paste(tile_image, (pos_x, pos_y), tile_image)

        center_x = tiles_needed * MINIMAP_TILE_SIZE + pixel_offset_x
        center_y = tiles_needed * MINIMAP_TILE_SIZE + pixel_offset_y

        # Calculate the crop box
        left = int(center_x - extent_pixels)
        top = int(center_y - extent_pixels)
        right = int(center_x + extent_pixels)
        bottom = int(center_y + extent_pixels)

        return temp_image.crop((left, top, right, bottom))
