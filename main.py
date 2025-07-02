import sys

import pygame
from pygame import MOUSEBUTTONDOWN, KEYDOWN, K_SPACE
from pygame.locals import QUIT

from config.loader import app_config
from events import EventHandler
from game.factories import UnitType
from game.map import Map
from game.screen import Screen
from game.rounds import round_manager, RoundPhase
from game.ui import RoundUI

# 初始化
screen = Screen(app_config)
game_map = Map(screen.surface)
game_map.generate_units(UnitType.BLOCKER)
game_map.generate_units(UnitType.CHARACTER)
events_handler = EventHandler()
round_ui = RoundUI(screen.surface)

# 事件迴圈監聽事件，進行事件處理
while True:
    # 迭代整個事件迴圈，若有符合事件則對應處理
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            events_handler.click(game_map)
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                events_handler.handle_end_turn()
        # 當使用者結束視窗，程式也結束
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Update round manager (handles execution phase)
    if round_manager.current_phase == RoundPhase.EXECUTION:
        round_manager.advance_phase()
    elif round_manager.current_phase == RoundPhase.RESOLUTION:
        round_manager.advance_phase()

    game_map.show()
    round_ui.draw_round_info(round_manager)
    screen.update()
