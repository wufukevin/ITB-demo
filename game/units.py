import pygame
from pygame import Vector2

from config.loader import app_config


class Unit(pygame.sprite.Sprite):
    """
    Unit accepts x and y which represents the tile coordination on the map
    """

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.pos = Vector2(x, y)
        self.image = pygame.Surface(app_config.get_tile_rect())
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
