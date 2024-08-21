from enum import Enum

import pygame

from game.map import Map
from game.units import Unit, Character, Tile


class Situation(Enum):
    NOTHING = 1
    SELECTED = 2
    MOVING = 3


class EventHandler:
    _instance = None
    situation = Situation.NOTHING
    selected_unit = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    class ClickEvent:
        def __init__(self, x, y, game_map: Map):
            self.x = x
            self.y = y
            self.game_map = game_map

        @classmethod
        def execute(self):
            pass

    class Select(ClickEvent):
        def __init__(self, unit: Unit, game_map: Map):
            EventHandler.ClickEvent.__init__(self, unit.tile.x, unit.tile.y, game_map)
            self.unit = unit

        def execute(self):
            # check type of selected_unit
            if type(EventHandler.selected_unit) is Character:
                self.game_map.remove_move_range()
                EventHandler.selected_unit.unselected()

            if self.unit == EventHandler.selected_unit:
                EventHandler.selected_unit = None
                return

            EventHandler.selected_unit = self.unit

            if type(EventHandler.selected_unit) is Character and not EventHandler.selected_unit.is_moving:
                reachable_tiles_with_path = self.game_map.reachable_tiles_with_path(self.unit)
                EventHandler.selected_unit.update_reachable_tiles_with_path(reachable_tiles_with_path)
                self.game_map.mark_move_range([tile[0] for tile in reachable_tiles_with_path])
                EventHandler.selected_unit.selected()

    class Move(ClickEvent):
        def __init__(self, x, y, game_map: Map):
            EventHandler.ClickEvent.__init__(self, x, y, game_map)

        def execute(self):
            EventHandler.selected_unit.unselected()
            if type(EventHandler.selected_unit) is Character:
                for data in EventHandler.selected_unit.reachable_tiles_with_path:
                    if data[0] == Tile(x=self.x, y=self.y):
                        EventHandler.selected_unit.update_move_path(data[1])
            self.game_map.remove_move_range()
            EventHandler.situation = Situation.NOTHING
            EventHandler.selected_unit = None

    class Attack(ClickEvent):
        def __init__(self, unit: Unit, game_map: Map):
            EventHandler.ClickEvent.__init__(self, unit.tile.x, unit.tile.y, game_map)
            self.unit = unit

        def execute(self):
            if type(self.unit) is Character:
                self.unit.on_hit()

    def click(self, game_map: Map):
        x, y = pygame.mouse.get_pos()
        tile_x, tile_y = int(x / Tile.width), int(y / Tile.height)
        click_event = self.get_click_event(game_map, tile_x, tile_y)
        click_event.execute()

    def get_click_event(self, game_map, tile_x, tile_y):
        click_event = EventHandler.ClickEvent(tile_x, tile_y, game_map)
        click_result = game_map[(tile_x, tile_y)]
        if click_result:
            self.situation = Situation.SELECTED
            # click_event = EventHandler.Select(click_result, game_map)
            click_event = EventHandler.Attack(click_result, game_map)
        else:
            if self.situation == Situation.SELECTED:
                self.situation = Situation.MOVING
                click_event = EventHandler.Move(tile_x, tile_y, game_map)
        return click_event
