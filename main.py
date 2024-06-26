import sys

import pygame
from pygame import Color, MOUSEBUTTONDOWN
from pygame.locals import QUIT

from events import click
from config.loader import app_config
from game.map import Map
from game.units import Character, Tile

# 初始化
pygame.init()
# 建立 window 視窗畫布
window_surface = pygame.display.set_mode((app_config.app.screen.width, app_config.app.screen.height), pygame.SCALED)
# 設置視窗標題
pygame.display.set_caption(app_config.app.screen.title)
# 清除畫面並填滿背景色
window_surface.fill(Color("black"))

clock = pygame.time.Clock()

# game_screen = pygame.sprite.LayeredUpdates()
# game_screen.add([Unit(Tile(x=0, y=0), UnitLayer.Terrain)])
game_map = Map(window_surface)

game_map.add([Character(Tile(x=1, y=1))])
game_map.add([Character(Tile(x=2, y=2))])

# # 宣告 font 文字物件
# head_font = pygame.font.SysFont(None, 60)
# # 渲染方法會回傳 surface 物件
# text_surface = head_font.render('Hello World!', True, (0, 0, 0))
# # blit 用來把其他元素渲染到另外一個 surface 上，這邊是 window 視窗
# window_surface.blit(text_surface, (10, 10))

# map = Map(app_config.app.game.tiles, app_config.app.game.tiles)
# c = Chess(100, 100)
# window_surface.blit(c.image, c.rect)

# 更新畫面，等所有操作完成後一次更新（若沒更新，則元素不會出現）
# pygame.display.update()

# 事件迴圈監聽事件，進行事件處理
while True:
    # 迭代整個事件迴圈，若有符合事件則對應處理
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            click(game_map)
        # 當使用者結束視窗，程式也結束
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    game_map.show()

    clock.tick(app_config.app.game.fps)  # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    pygame.display.update()
