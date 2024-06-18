from enum import Enum

import pygame
from pydantic import BaseModel, field_validator
from pygame import Rect, Color

from config.loader import app_config


class UnitLayer(Enum):
    Terrain = 0
    Character = 1
    Effect = 2


class Tile(BaseModel):
    x: int
    y: int
    padding: int = 0

    """
    Tile accepts x and y which represents the tile coordination on the map starting from 0,0
    """

    @field_validator('x')
    @classmethod
    def check_x(cls, v):
        if v < 0 or v >= app_config.game.tiles.width:
            raise ValueError('x out of range')
        return v

    @field_validator('y')
    @classmethod
    def check_y(cls, v):
        if v < 0 or v >= app_config.game.tiles.height:
            raise ValueError('y out of range')
        return v

    @staticmethod
    def width():
        return app_config.screen.width / app_config.game.tiles.width

    @staticmethod
    def height():
        return app_config.screen.height / app_config.game.tiles.height

    def get_rect(self) -> Rect:
        return pygame.Rect(self.x * Tile.width(), self.y * Tile.height(), Tile.width(),
                           Tile.height())

    @property
    def left(self) -> float:
        return self.get_rect().left

    @property
    def top(self) -> float:
        return self.get_rect().top

    @property
    def right(self) -> float:
        return self.get_rect().right

    @property
    def bottom(self) -> float:
        return self.get_rect().bottom


class Unit(pygame.sprite.Sprite):

    def __init__(self, tile: Tile, layer: UnitLayer = UnitLayer.Terrain):
        pygame.sprite.Sprite.__init__(self)
        self.tile = tile
        self.rect = self.tile.get_rect()
        self.image = pygame.Surface(self.rect.size)
        self.layer = layer.value

    def update(self):
        self.image.fill(Color("white"))
        self.rect.update(self.tile.get_rect())
        pygame.draw.rect(self.image, Color("black"), self.image.get_rect(), 1)
