from typing import TYPE_CHECKING

import pygame
from pygame import Color

if TYPE_CHECKING:
    from config.loader import AppConfig


class Screen:

    def __init__(self, app_config: 'AppConfig'):
        pygame.init()
        self.screen = app_config.app.screen
        self.fps = app_config.app.game.fps
        # 建立 window 視窗畫布
        self.surface = pygame.display.set_mode((self.screen.width, self.screen.height), pygame.SCALED)
        # 設置視窗標題
        pygame.display.set_caption(self.screen.title)
        # 清除畫面並填滿背景色
        self.surface.fill(Color("black"))
        self.clock = pygame.time.Clock()

    def update(self):
        self.clock.tick(self.fps)
        pygame.display.update()
