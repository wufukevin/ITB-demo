import random
from collections import defaultdict
from collections import deque
from typing import Sequence, Tuple, List, Any

import pygame

from config.loader import app_config
from game.factories import unit_factory, UnitType
from game.units import Tile, UnitLayer, Unit


class Map:

    def __init__(self, surface: pygame.Surface):
        self.__unit_generate_count = {
            UnitType.CHARACTER: app_config.game.character,
            UnitType.BLOCKER: app_config.game.terrain,
        }
        self.__units = defaultdict(list)
        self.__surface = surface
        self.__background = pygame.sprite.LayeredUpdates()
        self.add(unit_factory(UnitType.BACKGROUND).generate(self.__background_tiles()))

    @staticmethod
    def __background_tiles() -> List[Tile]:
        return [Tile(x=x, y=y) for x in range(app_config.game.tiles.width) for y in range(app_config.game.tiles.height)]

    def __getitem__(self, game_coordinate: Tuple[int, int] | Tile) -> Unit:
        if not isinstance(game_coordinate, Tile):
            x, y = game_coordinate
            tile = Tile(x=x, y=y)
        else:
            tile = game_coordinate
        units = [unit for unit in self.__units[tile] if
                 UnitLayer(unit.layer) in UnitLayer.selectable_layers()]
        return units[-1] if len(units) else None

    def show(self):
        self.show_unit_groups(self.__background)

    def show_unit_groups(self, unit_group: pygame.sprite.AbstractGroup):
        unit_group.update()
        unit_group.draw(self.__surface)

    def add(self, units: Sequence[pygame.sprite], **kwargs):
        for unit in units:
            unit.subscribe(self)
        self.__add_unit_cache(units)
        self.__background.add(units, **kwargs)

    def __add_unit_cache(self, units):
        for unit in units:
            self.__units[unit.tile].append(unit)

    def mark_move_range(self, tiles: List[Tile]):
        move_ranges = unit_factory(UnitType.MOVE_RANGE).generate(tiles)
        self.add(move_ranges)
        for unit in move_ranges:
            unit.selected()

    def remove_move_range(self):
        move_range = self.__background.get_sprites_from_layer(UnitLayer.MoveRange.value)
        self.remove(move_range)

    def remove(self, units: Sequence[pygame.sprite]):
        for unit in units:
            unit.unsubscribe(self)
        self.__del_unit_cache(units)
        self.__background.remove(units)

    def __del_unit_cache(self, units):
        for unit in units:
            self.__units[unit.tile].remove(unit)

    def __available_tiles_for_units(self) -> List[Tile]:
        background_tiles = set(
            [unit.tile for unit in self.__background if (UnitLayer(unit.layer) is UnitLayer.Background)])
        unit_tiles = set(
            [unit.tile for unit in self.__background if
             (UnitLayer(unit.layer) in UnitLayer.selectable_layers())])
        return list(background_tiles.difference(unit_tiles))

    def generate_units(self, unit_type: UnitType):
        generate_tiles = self.__pick_random_available_tiles(self.__unit_generate_count[unit_type])
        self.add(unit_factory(unit_type).generate(generate_tiles))

    def __pick_random_available_tiles(self, tile_count: int) -> List[Tile]:
        available_unit_tiles = self.__available_tiles_for_units()
        if len(available_unit_tiles) < tile_count:
            return []
        random.shuffle(available_unit_tiles)
        return available_unit_tiles[:tile_count]

    def reachable_tiles_with_path(self, unit: Unit):
        queue = deque([(unit.tile.x, unit.tile.y, 0, [Tile(x=unit.tile.x, y=unit.tile.y)])])
        visited = {(unit.tile.x, unit.tile.y)}
        reachable_tiles = list()

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            x, y, distance, path = queue.popleft()

            if distance <= unit.move_distance:
                reachable_tiles.append((Tile(x=x, y=y), path))

            if distance < unit.move_distance:
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < app_config.game.tiles.width and 0 <= ny < app_config.game.tiles.height:
                        if self.is_tile_reachable(nx, ny, visited):
                            queue.append((nx, ny, distance + 1, path + [Tile(x=nx, y=ny)]))
                            visited.add((nx, ny))
        return reachable_tiles

    def is_tile_reachable(self, nx, ny, visited):
        cell = self[(nx, ny)]
        if (nx, ny) in visited:
            return False
        if cell is None:
            return True
        return not cell.is_block

    def update(self, subject: Any, previous: Tile, current: Tile):
        self.__units[previous].remove(subject)
        self.__units[current].append(subject)
