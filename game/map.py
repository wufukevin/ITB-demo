import random
from collections import deque
from typing import Sequence, Tuple, List

import pygame

from config.loader import app_config
from game.factories import unit_factory, UnitType
from game.units import Tile, UnitLayer, Unit


class Map:
    reachable_tiles = []

    def __init__(self, surface: pygame.Surface):
        self.__unit_generate_count = {
            UnitType.CHARACTER: app_config.game.character,
            UnitType.TERRAIN: app_config.game.terrain
        }
        self.__surface = surface
        self.__background = pygame.sprite.LayeredUpdates()
        for x in range(app_config.game.tiles.width):
            for y in range(app_config.game.tiles.height):
                self.__background.add(Unit(Tile(x=x, y=y), UnitLayer.Background))

    def __getitem__(self, game_coordinate: Tuple[int, int]) -> Unit:
        x, y = game_coordinate
        units = [unit for unit in self.__background.get_sprites_at(Tile(x=x, y=y).get_rect().center) if
                 UnitLayer(unit.layer) in UnitLayer.selectable_layers()]
        return units[-1] if len(units) else None

    def show(self):
        self.show_unit_groups(self.__background)

    def show_unit_groups(self, unit_group: pygame.sprite.AbstractGroup):
        unit_group.update()
        unit_group.draw(self.__surface)

    def add(self, units: Sequence[pygame.sprite], **kwargs):
        self.__background.add(units, **kwargs)

    def mark_move_range(self):
        for tile in self.reachable_tiles:
            for unit in self.__background:
                if UnitLayer(unit.layer) is UnitLayer.Background and unit.tile == tile:
                    unit.selected()

    def remove_move_range(self):
        for unit in self.__background:
            if UnitLayer(unit.layer) is UnitLayer.Background:
                unit.unselected()
        self.clean_reachable_tiles()

    def remove(self, units: Sequence[pygame.sprite]):
        self.__background.remove(units)

    def __available_tiles_for_units(self) -> List[Tile]:
        background_tiles = set(
            [unit.tile for unit in self.__background if (UnitLayer(unit.layer) is UnitLayer.Background)])
        unit_tiles = set(
            [unit.tile for unit in self.__background if (UnitLayer(unit.layer) in UnitLayer.selectable_layers())])
        return list(background_tiles.difference(unit_tiles))

    def generate_units(self, unit_type: UnitType):
        generate_tiles = self.__pick_random_available_tiles(self.__unit_generate_count[unit_type])
        self.add(unit_factory(unit_type).generate(generate_tiles))

    def __pick_random_available_tiles(self, count: int) -> List[Tile]:
        available_unit_tiles = self.__available_tiles_for_units()
        if len(available_unit_tiles) < count:
            return []
        random.shuffle(available_unit_tiles)
        return available_unit_tiles[:count]

    def clean_reachable_tiles(self):
        self.reachable_tiles = []

    def update_reachable_tiles(self, unit: Unit):
        queue = deque([(unit.tile.x, unit.tile.y, 0)])
        visited = {(unit.tile.x, unit.tile.y)}
        reachable_tiles = list()

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            x, y, distance = queue.popleft()

            if distance <= unit.move_distance:
                reachable_tiles.append(Tile(x=x, y=y))

            if distance < unit.move_distance:
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < app_config.game.tiles.width and 0 <= ny < app_config.game.tiles.height:
                        if self.is_tile_reachable(nx, ny, visited):
                            queue.append((nx, ny, distance + 1))
                            visited.add((nx, ny))
        self.reachable_tiles = reachable_tiles

    def is_tile_reachable(self, nx, ny, visited):
        cell = self[(nx, ny)]
        if cell is None:
            return True
        return not cell.is_block and (nx, ny) not in visited
