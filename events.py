from enum import Enum
from typing import TYPE_CHECKING

import pygame

from game.tile import Tile
from game.units import Character

if TYPE_CHECKING:
    from game.units import Unit
    from game.map import Map


class Situation(Enum):
    NOTHING = 1
    SELECTED_TO_MOVE = 2
    SELECTED_TO_ATTACK = 3


def reset_situation():
    EventHandler.situation = Situation.NOTHING
    EventHandler.selected_unit.reset_action()
    EventHandler.selected_unit = None


class EventHandler:
    _instance = None
    situation = Situation.NOTHING
    selected_unit = None
    action_range = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    class ClickEvent:
        def __init__(self, tile: 'Tile', game_map: 'Map'):
            self.tile = tile
            self.game_map = game_map

        @classmethod
        def execute(cls):
            pass

    class Select(ClickEvent):
        def __init__(self, unit: 'Unit', game_map: 'Map'):
            EventHandler.ClickEvent.__init__(self, unit.tile, game_map)
            self.unit = unit

        def execute(self):
            # check type of selected_unit
            if type(EventHandler.selected_unit) is Character:
                self.game_map.remove_action_range()
                EventHandler.selected_unit.unselected()
                EventHandler.action_range = []

            if self.unit == EventHandler.selected_unit:
                EventHandler.selected_unit.change_move_mode()
                EventHandler.situation = Situation.SELECTED_TO_MOVE \
                    if EventHandler.selected_unit.is_move_mode() else Situation.SELECTED_TO_ATTACK
            else:
                pass

            EventHandler.selected_unit = self.unit

            if type(EventHandler.selected_unit) is Character and not EventHandler.selected_unit.is_moving:
                reachable_tiles = self.unit.current_action().reachable_tiles(self.unit.tile, self.game_map)
                EventHandler.action_range = [tile for tile in reachable_tiles]
                self.game_map.mark_action_range(EventHandler.action_range, EventHandler.selected_unit.is_move_mode())

    class Move(ClickEvent):
        def __init__(self, tile: 'Tile', game_map: 'Map'):
            EventHandler.ClickEvent.__init__(self, tile, game_map)

        def execute(self):
            selected_unit = EventHandler.selected_unit
            selected_unit.unselected()
            if type(selected_unit) is Character:
                reachable_tiles_with_path = selected_unit.move_action.find_path(selected_unit.tile,
                                                                                self.game_map)
                for data in reachable_tiles_with_path:
                    if data[0] == self.tile:
                        selected_unit.update_move_path(data[1])
            self.game_map.remove_action_range()
            reset_situation()

    class Attack(ClickEvent):
        def __init__(self, unit: 'Unit', game_map: 'Map', tile: 'Tile'):
            EventHandler.ClickEvent.__init__(self, tile, game_map)
            self.unit = unit

        def execute(self):
            selected_unit = EventHandler.selected_unit
            selected_unit.unselected()

            if type(selected_unit) is Character:
                reachable_tiles = EventHandler.selected_unit.attack_action.reachable_tiles(selected_unit.tile,
                                                                                           self.game_map)
                for tile in reachable_tiles:
                    if tile == self.unit.tile:
                        self.unit.on_hit(EventHandler.selected_unit.attack_damage)

                self.game_map.remove_action_range()
                reset_situation()

    def click(self, game_map: 'Map'):
        tile = Tile.from_screen_coordinate(*pygame.mouse.get_pos())
        click_event = self.get_click_event(game_map, tile)
        click_event.execute()

    def is_repeat_selected(self, tile: Tile):
        return self.selected_unit and self.selected_unit.tile == tile

    def get_click_event(self, game_map: 'Map', tile: 'Tile'):
        click_event = EventHandler.ClickEvent(tile, game_map)
        click_result = game_map[tile]
        if EventHandler.situation == Situation.NOTHING:
            if click_result:
                EventHandler.situation = Situation.SELECTED_TO_MOVE
                click_event = EventHandler.Select(click_result, game_map)
        elif EventHandler.situation == Situation.SELECTED_TO_MOVE:
            if click_result and self.is_repeat_selected(tile):
                EventHandler.situation = Situation.SELECTED_TO_ATTACK
                click_event = EventHandler.Select(click_result, game_map)
            else:
                click_event = EventHandler.Move(tile, game_map)
        elif EventHandler.situation == Situation.SELECTED_TO_ATTACK:
            if click_result:
                if self.is_repeat_selected(tile):
                    EventHandler.situation = Situation.SELECTED_TO_MOVE
                    click_event = EventHandler.Select(click_result, game_map)
                else:
                    click_event = EventHandler.Attack(click_result, game_map, tile)
        else:
            pass
        return click_event
