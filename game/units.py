from abc import ABC
from enum import Enum
from typing import ClassVar, Any, List

import pygame
from pydantic import BaseModel, field_validator
from pygame import Color, Rect

from config.loader import app_config


def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


class UnitLayer(Enum):
    Background = -1
    Terrain = 0
    MoveRange = 1
    Character = 10
    Effect = 20

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

    def __hash__(self):
        return hash((self.x, self.y))


class Unit(pygame.sprite.Sprite):
    _observers: List[Any]
    bg_color = Color('white')
    boarder_color = Color('black')
    is_block = False

    def __init__(self, tile: Tile, image: pygame.surface.Surface = None, layer: UnitLayer = UnitLayer.Background):
        pygame.sprite.Sprite.__init__(self)
        self.tile = tile
        self.rect = self.tile.get_rect()
        self.image = self.create_plain_image() if image is None else pygame.transform.scale(image, self.rect.size)
        self.use_plain_image = image is None
        self.layer = layer.value
        self._observers = []

    def create_plain_image(self):
        return pygame.Surface(self.rect.size, pygame.SRCALPHA)

    def update(self):
        self.rect.update(self.tile.get_rect())
        self.render_boarder()
        self.render_image()

    def render_image(self):
        if self.use_plain_image:
            self.image.fill(self.bg_color)

    def render_boarder(self):
        pygame.draw.rect(self.image, self.boarder_color, self.image.get_rect(), 1)

    def selected(self):
        if self.use_plain_image:
            self.bg_color = Color(0, 255, 0, 50)

    def unselected(self):
        if self.use_plain_image:
            self.bg_color = Color('white')

    def update_pos(self, tile: Tile):
        previous_tile = self.tile
        self.tile = tile
        self.notify(previous_tile, tile)

    def subscribe(self, observer: Any):
        self._observers.append(observer)

    def unsubscribe(self, observer: Any):
        self._observers.remove(observer)

    def notify(self, previous: Tile, current: Tile):
        for observer in self._observers:
            observer.update(self, previous, current)


class AnimatedUnit(Unit):
    def __init__(self, tile: Tile, images: List[pygame.surface.Surface], layer: UnitLayer = UnitLayer.Background,
                 speed_frame=10):
        super().__init__(tile=tile, image=images[0], layer=layer)
        self.speed_frame = speed_frame
        self.current_animate_frame = 0
        self.images = images

    def update(self):
        super().update()
        self.current_animate_frame = (self.current_animate_frame + 1) % self.speed_frame
        if self.current_animate_frame == 0:
            self.images.append(self.images.pop(0))
            self.image = pygame.transform.scale(self.images[0], self.rect.size)


class Terrain(Unit, ABC):
    bg_color = Color('yellow')

    def __init__(self, tile=Tile(x=0, y=0), image: pygame.surface.Surface = None, layer=UnitLayer.Terrain):
        super().__init__(tile=tile, image=image, layer=layer)


class Character(Unit, ABC):
    bg_color = Color('blue')
    boarder_color = Color('black')
    is_block = True
    is_moving = False
    move_fps = 30
    fps_count = 0
    move_path = []

    def __init__(self, tile=Tile(x=0, y=0), image: pygame.surface.Surface = None, move_distance=3):
        super().__init__(tile=tile, image=image, layer=UnitLayer.Character)
        self.move_distance = move_distance

    def update(self):
        super().update()
        self.fps_count += 1
        if self.fps_count == self.move_fps:
            self.fps_count = 0
            if self.move_path:
                self.update_pos(self.move_path.pop(0))
                self.is_moving = True
            else:
                self.is_moving = False

    def save_shortest_path(self, tile: Tile):
        self.move_path = []
        current_x = self.tile.x
        current_y = self.tile.y
        x = tile.x
        y = tile.y
        while current_x != x:
            if current_x < x:
                current_x += 1
            else:
                current_x -= 1
            self.move_path.append(Tile(x=current_x, y=current_y))

        while current_y != y:
            if current_y < y:
                current_y += 1
            else:
                current_y -= 1
            self.move_path.append(Tile(x=current_x, y=current_y))

    def update_pos(self, tile: Tile):
        super().update_pos(tile)
        self.unselected()
        if self.is_in_distance(tile.x, tile.y):
            self.save_shortest_path(tile)
            # self.tile = tile
        else:
            print('out of distance')

    def selected(self):
        self.bg_color = Color('red')

    def unselected(self):
        self.bg_color = Color('blue')

    def is_in_distance(self, x, y):
        return manhattan_distance(self.tile.x, self.tile.y, x, y) <= self.move_distance

    def move_range(self):
        ranges = []
        for i in range(-self.move_distance, self.move_distance + 1):
            for j in range(-self.move_distance, self.move_distance + 1):
                x = self.tile.x + i
                y = self.tile.y + j
                if 0 <= x < app_config.game.tiles.width and 0 <= y < app_config.game.tiles.height:
                    if self.is_in_distance(x, y):
                        ranges.append(Tile(x=x, y=y))
        return ranges
