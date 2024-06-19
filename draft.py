import pygame

from config.loader import app_config
from main import window_surface


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


class Map:
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
