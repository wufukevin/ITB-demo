from typing import ClassVar, Self, List, Tuple

import pygame
from pydantic import BaseModel, field_validator
from pygame import Rect

from config.loader import app_config


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

    @property
    def right_tile(self) -> Self:
        return Tile(x=self.x + 1, y=self.y) if self.x + 1 < app_config.game.tiles.width else None

    @property
    def bottom_tile(self) -> Self:
        return Tile(x=self.x, y=self.y + 1) if self.y + 1 < app_config.game.tiles.height else None

    @property
    def left_tile(self) -> Self:
        return Tile(x=self.x - 1, y=self.y) if self.x - 1 >= 0 else None

    @property
    def top_tile(self) -> Self:
        return Tile(x=self.x, y=self.y - 1) if self.y - 1 >= 0 else None

    @property
    def neighbor_tiles(self) -> List[Self]:
        return [neighbor for neighbor in [self.left_tile, self.top_tile, self.right_tile, self.bottom_tile] if neighbor]

    @classmethod
    def from_screen_coordinate(cls: Self, x: int, y: int) -> Self:
        return Tile(x=int(x / Tile.width), y=int(y / Tile.height))

    def distance_to(self, tile: Self | Tuple[int, int]) -> int:
        if isinstance(tile, tuple):
            x, y = tile
            return manhattan_distance(self.x, self.y, x, y)
        else:
            return manhattan_distance(self.x, self.y, tile.x, tile.y)

    def __hash__(self):
        return hash((self.x, self.y))


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)
