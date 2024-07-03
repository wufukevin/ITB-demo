from typing import Sequence

import pygame

from config.loader import app_config
from game.units import Tile, UnitLayer, Unit, Character
from pygame import Color


class Map:

    def __init__(self, surface):
        self.__surface = surface
        self.__background = pygame.sprite.LayeredUpdates()
        for x in range(app_config.game.tiles.width):
            for y in range(app_config.game.tiles.height):
                self.__background.add(Unit(Tile(x=x, y=y), UnitLayer.Background))

    def __getitem__(self, item) -> Unit:
        x, y = item
        units = [unit for unit in self.__background.get_sprites_at(Tile(x=x, y=y).get_rect().center) if
                 UnitLayer(unit.layer) in UnitLayer.selectable_layers()]
        return units[-1] if len(units) else None

    def show(self):
        self.__background.update()
        self.__background.draw(self.__surface)

    def add(self, units: Sequence[Unit], **kwargs):
        self.__background.add(units, **kwargs)

    def show_move_distance(self, char: Character):
        for i in range(-char.move_distance, char.move_distance + 1):
            for j in range(-char.move_distance, char.move_distance + 1):
                x = char.tile.x + i
                y = char.tile.y + j
                if 0 <= x < app_config.game.tiles.width and 0 <= y < app_config.game.tiles.height:
                    if char.is_in_distance(x, y):
                        for unit in self.__background:
                            if UnitLayer(unit.layer) is UnitLayer.Background and unit.tile.x == x and unit.tile.y == y:
                                unit.change_bg_color(Color('green'))

    def clean_bg_color(self):
        for unit in self.__background:
            if UnitLayer(unit.layer) is UnitLayer.Background:
                unit.change_bg_color(Color('white'))
