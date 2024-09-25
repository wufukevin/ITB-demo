import random
from collections import defaultdict, deque
from typing import Sequence, Tuple, List, Any, Dict, Generator, TYPE_CHECKING

import pygame

from config.loader import app_config
from game.factories import unit_factory, UnitType
from game.tile import Tile
from game.units import UnitLayer

if TYPE_CHECKING:
    from game.units import Unit


class Map:

    def __init__(self, surface: pygame.Surface):
        self.__unit_generate_count: Dict['UnitType', int] = {
            UnitType.CHARACTER: app_config.game.character,
            UnitType.BLOCKER: app_config.game.terrain,
        }
        self.__units = defaultdict(list)
        self.__surface = surface
        self.__background = pygame.sprite.LayeredUpdates()
        self.add(unit_factory(UnitType.BACKGROUND).generate(self.__config_game_tiles()))

    @staticmethod
    def __config_game_tiles() -> List['Tile']:
        return [Tile(x=x, y=y) for x in range(app_config.game.tiles.width) for y in range(app_config.game.tiles.height)]

    def __getitem__(self, game_coordinate: Tuple[int, int] | 'Tile') -> 'Unit':
        if not isinstance(game_coordinate, Tile):
            x, y = game_coordinate
            tile = Tile(x=x, y=y)
        else:
            tile = game_coordinate
        units = [unit for unit in self.__units[tile] if
                 UnitLayer(unit.layer) in UnitLayer.selectable_layers()]
        return units[-1] if len(units) else None

    def show(self):
        self.__background.update()
        self.__background.draw(self.__surface)

    def add(self, units: Sequence[pygame.sprite], **kwargs):
        for unit in units:
            unit.subscribe(self)
            self.__units[unit.tile].append(unit)
        self.__background.add(units, **kwargs)

    def __add_unit_cache(self, units):
        for unit in units:
            self.__units[unit.tile].append(unit)

    def mark_action_range(self, tiles: List['Tile'], is_move_mode: bool = False):
        action_ranges = unit_factory(UnitType.MOVE_RANGE).generate(tiles)
        self.add(action_ranges)
        for unit in action_ranges:
            if is_move_mode:
                unit.selected_green()
            else:
                unit.selected_yellow()

    def remove_action_range(self):
        action_range = self.__background.get_sprites_from_layer(UnitLayer.MoveRange.value)
        self.remove(action_range)

    def remove(self, units: Sequence[pygame.sprite]):
        for unit in units:
            unit.unsubscribe(self)
            self.__units[unit.tile].remove(unit)
        self.__background.remove(units)

    def __available_config_game_tiles(self) -> List['Tile']:
        config_game_tiles = set(
            [unit.tile for unit in self.__background if (UnitLayer(unit.layer) is UnitLayer.Background)])
        unit_tiles = set(
            [unit.tile for unit in self.__background if
             (UnitLayer(unit.layer) in UnitLayer.selectable_layers())])
        return list(config_game_tiles.difference(unit_tiles))

    def generate_units(self, unit_type: 'UnitType'):
        generate_tiles = self.__pick_random_available_config_game_tiles(self.__unit_generate_count[unit_type])
        self.add(unit_factory(unit_type).generate(generate_tiles))

    def __pick_random_available_config_game_tiles(self, tile_count: int) -> List['Tile']:
        available_config_game_tiles = self.__available_config_game_tiles()
        if len(available_config_game_tiles) < tile_count:
            return []
        random.shuffle(available_config_game_tiles)
        return available_config_game_tiles[:tile_count]

    def update(self, subject: Any, previous: 'Tile', current: 'Tile'):
        self.__units[previous].remove(subject)
        self.__units[current].append(subject)
