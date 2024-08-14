import sys

import pygame
from pygame import MOUSEBUTTONDOWN
from pygame.locals import QUIT

from config.loader import app_config
from events import EventHandler
from game.factories import UnitType
from game.map import Map
from game.screen import Screen

# 初始化
screen = Screen(app_config)
game_map = Map(screen.surface)
game_map.generate_units(UnitType.BLOCKER)
game_map.generate_units(UnitType.CHARACTER)
events_handler = EventHandler()

# 事件迴圈監聽事件，進行事件處理
while True:
    # 迭代整個事件迴圈，若有符合事件則對應處理
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            events_handler.click(game_map)
        # 當使用者結束視窗，程式也結束
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    game_map.show()
    screen.update()
