import pygame

from config.loader import app_config
from game.units import Tile, UnitLayer, Unit


class Map:

    def __init__(self, surface):
        self.surface = surface
        self.plain = pygame.sprite.LayeredUpdates()
        for x in range(app_config.game.tiles.width):
            for y in range(app_config.game.tiles.height):
                self.plain.add(Unit(Tile(x=x, y=y), UnitLayer.Terrain))

    def __getitem__(self, item):
        x, y = item
        return self.plain.get_sprites_at(Tile(x=x, y=y).get_rect().size)[-1]

    def show(self):
        self.plain.update()
        self.plain.draw(self.surface)
