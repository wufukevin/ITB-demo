from enum import Enum
from typing import ClassVar

import pygame
from pydantic import BaseModel, field_validator
from pygame import Rect, Color

from config.loader import app_config


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


class UnitLayer(Enum):
    Background = -1
    Terrain = 0
    Character = 1
    Effect = 2

    @staticmethod
    def selectable_layers():
        return [UnitLayer.Terrain, UnitLayer.Character]


class Tile(BaseModel):
    width: ClassVar[float] = app_config.screen.width / app_config.game.tiles.width
    height: ClassVar[float] = app_config.screen.height / app_config.game.tiles.height
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
        return pygame.Rect(self.x * self.width + self.padding, self.y * self.height + self.padding,
                           self.width - self.padding * 2,
                           self.height - self.padding * 2)

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
    bg_color = Color('white')
    boarder_color = Color('black')
    is_block = False

    def __init__(self, tile: Tile, layer: UnitLayer = UnitLayer.Background):
        pygame.sprite.Sprite.__init__(self)
        self.tile = tile
        self.rect = self.tile.get_rect()
        self.image = pygame.Surface(self.rect.size)
        self.layer = layer.value

    def update(self):
        self.image.fill(self.bg_color)
        self.rect.update(self.tile.get_rect())
        pygame.draw.rect(self.image, self.boarder_color, self.image.get_rect(), 1)

    def change_bg_color(self, color: Color):
        self.bg_color = color


class Character(Unit):
    bg_color = Color('blue')
    boarder_color = Color('black')
    is_block = True

    def __init__(self, tile=Tile(x=0, y=0), move_distance=2):
        super().__init__(tile=tile, layer=UnitLayer.Character)
        self.move_distance = move_distance

    def update_pos(self, tile: Tile):
        self.unselected()
        if self.is_in_distance(tile.x, tile.y):
            self.tile = tile
        else:
            print('out of distance')

    def selected(self):
        self.bg_color = Color('red')

    def unselected(self):
        self.bg_color = Color('blue')

    def is_in_distance(self, x, y):
        return manhattan_distance(self.tile.x, self.tile.y, x, y) <= self.move_distance
