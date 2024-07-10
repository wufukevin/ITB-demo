import random
from typing import Sequence, Tuple, List

import pygame

from config.loader import app_config
from game.factories import unit_factory, UnitType
from game.units import Tile, UnitLayer, Unit


class Map:

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

    def mark_move_range(self, tiles: List[Tile]):
        for tile in tiles:
            for unit in self.__background:
                if UnitLayer(unit.layer) is UnitLayer.Background and unit.tile == tile:
                    unit.selected()

    def remove_move_range(self):
        for unit in self.__background:
            if UnitLayer(unit.layer) is UnitLayer.Background:
                unit.unselected()

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
