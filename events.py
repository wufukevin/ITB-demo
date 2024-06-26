from enum import Enum

import pygame

from config.loader import app_config
from game.map import Map
from game.units import Unit, Character, Tile

each_tile_width = app_config.app.screen.width / app_config.app.game.tiles.width
each_tile_height = app_config.app.screen.height / app_config.app.game.tiles.height


class Situation(Enum):
    NOTHING = 1
    SELECTED = 2
    MOVING = 3


situation = Situation.NOTHING
selected_unit = None


class ClickEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def execute(self):
        pass


class Select(ClickEvent):
    def __init__(self, unit: Unit):
        ClickEvent.__init__(self, unit.tile.x, unit.tile.y)
        self.unit = unit

    def execute(self):
        global selected_unit
        # check type of selected_unit
        if type(selected_unit) is Character:
            selected_unit.unselected()

        selected_unit = self.unit

        if type(selected_unit) is Character:
            selected_unit.selected()


class Move(ClickEvent):
    def __init__(self, x, y):
        ClickEvent.__init__(self, x, y)

    def execute(self):
        global selected_unit
        global situation
        if type(selected_unit) is Character:
            selected_unit.update_pos(Tile(x=self.x, y=self.y))
        situation = Situation.NOTHING
        selected_unit = None


def click(game_map: Map):
    global situation
    x, y = pygame.mouse.get_pos()
    x1, y1 = int(x / each_tile_width), int(y / each_tile_height)
    click_event = ClickEvent(x1, y1)
    click_result = game_map[(x1, y1)]
    if click_result:
        situation = Situation.SELECTED
        click_event = Select(click_result)
    else:
        if situation == Situation.SELECTED:
            situation = Situation.MOVING
            click_event = Move(x1, y1)
    click_event.execute()
