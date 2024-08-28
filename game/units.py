from enum import Enum
from typing import Any, List

import pygame
from pygame import Color

from config.loader import app_config
from game.tile import Tile


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


class Unit(pygame.sprite.Sprite):
    _observers: List[Any]
    bg_color: Color = Color('white')
    boarder_color: Color = Color('black')
    is_block = False
    is_destroyable = False
    show_boarder = True

    def __init__(self, tile: Tile, image: pygame.surface.Surface = None, layer: UnitLayer = UnitLayer.Background,
                 **kwargs):
        pygame.sprite.Sprite.__init__(self)

        # Accessing additional keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.tile = tile
        self.rect = self.tile.get_rect()
        self.image = self.create_plain_image(self.bg_color) if image is None else pygame.transform.scale(image,
                                                                                                         self.rect.size)
        self.layer = layer.value
        self._observers = []

    def create_plain_image(self, color):
        surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surface.fill(color)
        return surface

    def update(self):
        self.rect.update(self.tile.get_rect())
        self.render_boarder()

    def render_boarder(self):
        if not self.show_boarder:
            return
        self.boarder_color = Color('red') if self.is_block else self.boarder_color
        pygame.draw.rect(self.image, self.boarder_color, self.image.get_rect(), 1)

    def selected(self):
        self.image = self.create_plain_image(Color(0, 255, 0, 50))

    def unselected(self):
        self.image = self.create_plain_image(Color(0, 0, 0, 0))

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
                 frame_per_image=10):
        super().__init__(tile=tile, image=images[0], layer=layer)
        self.speed_frame = frame_per_image
        self.current_animate_frame = 0
        self.images = images
        self.show_boarder = False

    def render_image(self):
        self.current_animate_frame = (self.current_animate_frame + 1) % self.speed_frame
        if self.current_animate_frame == 0:
            self.images.append(self.images.pop(0))
            self.image = pygame.transform.scale(self.images[0], self.rect.size)


class Character(AnimatedUnit):
    bg_color = Color('blue')
    boarder_color = Color('black')
    is_block = True
    is_moving = False
    move_fps = 30
    fps_count = 0
    move_path = []
    reachable_tiles_with_path = []
    max_health = 5
    current_health = max_health

    def __init__(self, tile=Tile(x=0, y=0), images: List[pygame.surface.Surface] = None, frame_per_image=10,
                 move_distance=3):
        super().__init__(tile=tile, images=images, layer=UnitLayer.Character, frame_per_image=frame_per_image)
        self.move_distance = move_distance
        self.set_hp_position()

    def set_hp_position(self):
        # 血條位置
        image_rect = self.image.get_rect()
        self.health_bar_x = 5
        self.health_bar_y = image_rect.bottom - 10
        self.health_bar_width = image_rect.width - 10
        self.health_bar_height = 5

    def update(self):
        super().update()
        self.draw_health_bar()
        self.fps_count += 1
        if self.fps_count == self.move_fps:
            self.fps_count = 0
            if self.move_path:
                self.update_pos(self.move_path.pop(0))
                self.is_moving = True
            else:
                self.is_moving = False

    def draw_health_bar(self):
        pygame.draw.rect(self.image, (100, 100, 100),
                         (self.health_bar_x, self.health_bar_y, self.health_bar_width, self.health_bar_height))
        segment_width = self.health_bar_width / self.max_health
        for i in range(self.current_health):
            pygame.draw.rect(self.image, (255, 0, 0),
                             (self.health_bar_x + i * segment_width, self.health_bar_y,
                              segment_width, self.health_bar_height))
            pygame.draw.rect(self.image, self.boarder_color, (self.health_bar_x + i * segment_width, self.health_bar_y,
                                                              segment_width, self.health_bar_height), 1)

    def update_reachable_tiles_with_path(self, data):
        self.reachable_tiles_with_path = data

    def update_move_path(self, path: list[Tile]):
        self.move_path = path

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

    def on_hit(self, damage: int):
        self.current_health -= damage
        if self.current_health <= 0:
            self.notify_death()

    def notify_death(self):
        for observer in self._observers:
            observer.remove([self])
