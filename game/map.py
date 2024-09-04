import random
from collections import defaultdict, deque
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

    def mark_action_range(self, tiles: List[Tile], is_move_mode: bool = False):
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
        self.__del_unit_cache(units)
        self.__background.remove(units)

    def __del_unit_cache(self, units):
        for unit in units:
            self.__units[unit.tile].remove(unit)

    def available_tiles_for_units(self) -> List[Tile]:
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
        available_unit_tiles = self.available_tiles_for_units()
        if len(available_unit_tiles) < tile_count:
            return []
        random.shuffle(available_unit_tiles)
        return available_unit_tiles[:tile_count]

    def reachable_tiles(self, start: Tile, move_distance: int):
        for x in range(start.x - move_distance, start.x + move_distance + 1):
            if x < 0 or x >= app_config.game.tiles.width:
                continue
            for y in range(start.y - move_distance, start.y + move_distance + 1):
                if y < 0 or y >= app_config.game.tiles.height:
                    continue
                if abs(x - start.x) + abs(y - start.y) > move_distance:
                    continue
                unit = self[(x, y)]
                if unit is None or not unit.is_block:
                    yield Tile(x=x, y=y)

    def find_path(self, tile: Tile, move_distance: int):
        queue = deque([(tile, 0, [tile])])
        visited = {tile}
        reachable_tiles = list()

        while queue:
            current_tile, distance, path = queue.popleft()

            if distance <= move_distance:
                reachable_tiles.append((current_tile, path))

            if distance < move_distance:
                for neighbor in current_tile.neighbor_tiles:
                    unit = self[neighbor]
                    if neighbor in visited:
                        continue
                    if unit is None or not unit.is_block:
                        queue.append((neighbor, distance + 1, path + [neighbor]))
                        visited.add(neighbor)
        return reachable_tiles

    def update(self, subject: Any, previous: Tile, current: Tile):
        self.__units[previous].remove(subject)
        self.__units[current].append(subject)
