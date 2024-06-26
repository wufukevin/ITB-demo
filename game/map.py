from typing import Sequence

import pygame

from config.loader import app_config
from game.units import Tile, UnitLayer, Unit


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
