from enum import Enum
from typing import ClassVar

import pygame
from pydantic import BaseModel, field_validator
from pygame import Rect, Color

from config.loader import app_config


class UnitLayer(Enum):
    Background = -1
    Terrain = 0
    Character = 1
    Effect = 2

    @staticmethod
    def selectable_layers():
        return [UnitLayer.Terrain, UnitLayer.Character]


class Tile(BaseModel):
    __width: ClassVar[float] = app_config.screen.width / app_config.game.tiles.width
    __height: ClassVar[float] = app_config.screen.height / app_config.game.tiles.height
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

    def get_rect(self) -> Rect:
        return pygame.Rect(self.x * self.__width + self.padding, self.y * self.__height + self.padding,
                           self.__width - self.padding * 2,
                           self.__height - self.padding * 2)

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
    __bg_color = Color('white')
    __boarder_color = Color('black')

    def __init__(self, tile: Tile, layer: UnitLayer = UnitLayer.Background):
        pygame.sprite.Sprite.__init__(self)
        self.tile = tile
        self.rect = self.tile.get_rect()
        self.image = pygame.Surface(self.rect.size)
        self.layer = layer.value

    def update(self):
        self.image.fill(self.__bg_color)
        self.rect.update(self.tile.get_rect())
        pygame.draw.rect(self.image, self.__boarder_color, self.image.get_rect(), 1)


class Character(Unit):
    __bg_color = Color('blue')
    __boarder_color = Color('black')

    def __init__(self, tile=Tile(x=0, y=0)):
        super().__init__(tile=tile, layer=UnitLayer.Character)

    def update(self):
        self.image.fill(self.__bg_color)
        self.rect.update(self.tile.get_rect())
        pygame.draw.rect(self.image, self.__boarder_color, self.image.get_rect(), 1)
