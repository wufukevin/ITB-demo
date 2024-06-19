import sys

import pygame
from pygame.locals import QUIT

from config.loader import app_config


class Chess(pygame.sprite.Sprite):
    def __init__(self, x, y) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([x, y])
        self.image.fill((90, 90, 90))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        pass

    def moveTo(self, x, y):
        self.rect.x = x
        self.rect.y = y


class Map():
    def __init__(self, w, h) -> None:
        self.w = w
        self.h = h
        self.cell_w = app_config.app.screen.width / w
        self.cell_h = app_config.app.screen.height / h
        self.area = pygame.Surface((self.cell_w, self.cell_h))
        self.area_color = (50, 50, 50)
        self.area.fill(self.area_color)

        self.draeCheckerBoard()
        pass

    def draeCheckerBoard(self):
        x = []
        for i in range(self.w):
            for j in range(self.h):
                if (i + j) % 2 == 1:
                    x.append((i * self.cell_w, j * self.cell_h))
        for loc in x:
            window_surface.blit(self.area, loc)


# 初始化
pygame.init()
# 建立 window 視窗畫布
window_surface = pygame.display.set_mode((app_config.app.screen.width, app_config.app.screen.height))
# 設置視窗標題為 Hello World:)
pygame.display.set_caption(app_config.app.game.title)
# 清除畫面並填滿背景色
window_surface.fill((255, 255, 255))

clock = pygame.time.Clock()

# # 宣告 font 文字物件
# head_font = pygame.font.SysFont(None, 60)
# # 渲染方法會回傳 surface 物件
# text_surface = head_font.render('Hello World!', True, (0, 0, 0))
# # blit 用來把其他元素渲染到另外一個 surface 上，這邊是 window 視窗
# window_surface.blit(text_surface, (10, 10))

map = Map(app_config.app.game.tiles, app_config.app.game.tiles)
c = Chess(100, 100)
window_surface.blit(c.image, c.rect)

# 更新畫面，等所有操作完成後一次更新（若沒更新，則元素不會出現）
pygame.display.update()

# 事件迴圈監聽事件，進行事件處理
while True:
    # 迭代整個事件迴圈，若有符合事件則對應處理
    for event in pygame.event.get():
        # 當使用者結束視窗，程式也結束
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # window_surface.fill(bg_color)
    window_surface.blit(c.image, c.rect)

    clock.tick(app_config.app.game.fps)  # 控制循环刷新频率,每秒刷新FPS对应的值的次数
    pygame.display.update()
