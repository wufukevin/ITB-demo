from enum import Enum
from typing import TYPE_CHECKING

import pygame

from game.tile import Tile
from game.units import Character
from game.rounds import round_manager, RoundPhase, MoveAction

if TYPE_CHECKING:
    from game.units import Unit
    from game.map import Map


class ClickMode(Enum):
    NOTHING = 1
    SELECTED = 2
    MOVING = 3


class EventHandler:
    _instance = None
    click_mode = ClickMode.NOTHING
    selected_unit = None

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
            # Only allow selection during planning phase
            if round_manager.current_phase != RoundPhase.PLAYER_PLANNING:
                return

            # check type of selected_unit
            if type(EventHandler.selected_unit) is Character:
                self.game_map.remove_move_range()
                EventHandler.selected_unit.unselected()

            if self.unit == EventHandler.selected_unit:
                EventHandler.selected_unit = None
                return

            EventHandler.selected_unit = self.unit

            if type(EventHandler.selected_unit) is Character and not EventHandler.selected_unit.is_moving:
                # Check if this character can still act this round
                if round_manager.can_actor_act(self.unit):
                    reachable_tiles = self.game_map.reachable_tiles(self.unit.tile, self.unit.move_distance)
                    self.game_map.mark_move_range(reachable_tiles)
                else:
                    # Show existing planned action
                    planned_action = round_manager.get_action_for_actor(self.unit)
                    if planned_action and isinstance(planned_action, MoveAction):
                        self.game_map.mark_move_range([planned_action.target_tile])

    class Move(ClickEvent):
        def __init__(self, tile: 'Tile', game_map: 'Map'):
            EventHandler.ClickEvent.__init__(self, tile, game_map)

        def execute(self):
            # Only allow moves during planning phase
            if round_manager.current_phase != RoundPhase.PLAYER_PLANNING:
                return

            selected_unit = EventHandler.selected_unit
            if not selected_unit or type(selected_unit) is not Character:
                return

            # Check if unit can act this round
            if not round_manager.can_actor_act(selected_unit):
                # Unit already has an action, replace it
                round_manager.remove_action(selected_unit)

            # Find path to target tile
            reachable_tiles_with_path = self.game_map.find_path(selected_unit.tile,
                                                                selected_unit.move_distance)
            for tile_data in reachable_tiles_with_path:
                if tile_data[0] == self.tile:
                    # Create and queue the move action
                    move_action = MoveAction(selected_unit, self.tile, tile_data[1])
                    round_manager.add_action(move_action)
                    break

            selected_unit.unselected()
            self.game_map.remove_move_range()
            EventHandler.click_mode = ClickMode.NOTHING
            EventHandler.selected_unit = None

    class Attack(ClickEvent):
        def __init__(self, unit: 'Unit', game_map: 'Map', tile: 'Tile'):
            EventHandler.ClickEvent.__init__(self, tile, game_map)
            self.unit = unit

        def execute(self):
            if type(self.unit) is Character:
                self.unit.on_hit(1)

    def click(self, game_map: 'Map'):
        tile = Tile.from_screen_coordinate(*pygame.mouse.get_pos())
        click_event = self.get_click_event(game_map, tile)
        click_event.execute()

    def handle_end_turn(self):
        if round_manager.current_phase == RoundPhase.PLAYER_PLANNING:
            round_manager.end_turn()

    def get_click_event(self, game_map: 'Map', tile: 'Tile'):
        click_event = EventHandler.ClickEvent(tile, game_map)
        clicked_unit = game_map[tile]
        if clicked_unit:
            self.click_mode = ClickMode.SELECTED
            click_event = EventHandler.Select(clicked_unit, game_map)
            # click_event = EventHandler.Attack(clicked_unit, game_map, tile)
        else:
            if self.click_mode == ClickMode.SELECTED:
                self.click_mode = ClickMode.MOVING
                click_event = EventHandler.Move(tile, game_map)
        return click_event
