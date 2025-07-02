from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    from game.units import Unit
    from game.tile import Tile


class RoundPhase(Enum):
    PLAYER_PLANNING = 1  # Player selects actions
    EXECUTION = 2        # Actions execute in order
    RESOLUTION = 3       # Effects resolve, advance round


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    effects: List[Any] = None

    def __post_init__(self):
        if self.effects is None:
            self.effects = []


class Action(ABC):
    def __init__(self, actor: 'Unit', priority: int = 0):
        self.actor = actor
        self.priority = priority  # Lower values execute first
        self.executed = False

    @abstractmethod
    def can_execute(self) -> bool:
        pass

    @abstractmethod
    def execute(self) -> ActionResult:
        pass

    def __lt__(self, other):
        return self.priority < other.priority


class MoveAction(Action):
    def __init__(self, actor: 'Unit', target_tile: 'Tile', path: List['Tile'], priority: int = 10):
        super().__init__(actor, priority)
        self.target_tile = target_tile
        self.path = path

    def can_execute(self) -> bool:
        return not self.actor.is_moving and len(self.path) > 0

    def execute(self) -> ActionResult:
        if not self.can_execute():
            return ActionResult(False, "Cannot execute move action")
        
        # Set the movement path for the character
        if hasattr(self.actor, 'update_move_path'):
            self.actor.update_move_path(self.path[1:])  # Skip current position
            self.executed = True
            return ActionResult(True, f"{self.actor.__class__.__name__} moving to {self.target_tile}")
        
        return ActionResult(False, "Actor cannot move")


class RoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        
        self.current_round = 1
        self.current_phase = RoundPhase.PLAYER_PLANNING
        self.action_queue: List[Action] = []
        self.executed_actions: List[Action] = []
        self._observers: List[Any] = []

    def add_action(self, action: Action) -> bool:
        if self.current_phase != RoundPhase.PLAYER_PLANNING:
            return False
        
        # Remove any existing action from the same actor
        self.action_queue = [a for a in self.action_queue if a.actor != action.actor]
        
        # Add new action
        self.action_queue.append(action)
        self.notify_observers()
        return True

    def remove_action(self, actor: 'Unit') -> bool:
        if self.current_phase != RoundPhase.PLAYER_PLANNING:
            return False
        
        initial_count = len(self.action_queue)
        self.action_queue = [a for a in self.action_queue if a.actor != actor]
        
        if len(self.action_queue) < initial_count:
            self.notify_observers()
            return True
        return False

    def get_action_for_actor(self, actor: 'Unit') -> Optional[Action]:
        for action in self.action_queue:
            if action.actor == actor:
                return action
        return None

    def can_actor_act(self, actor: 'Unit') -> bool:
        if self.current_phase != RoundPhase.PLAYER_PLANNING:
            return False
        
        # Check if actor already has an action queued
        return self.get_action_for_actor(actor) is None

    def advance_phase(self):
        if self.current_phase == RoundPhase.PLAYER_PLANNING:
            self.current_phase = RoundPhase.EXECUTION
            self._execute_actions()
        elif self.current_phase == RoundPhase.EXECUTION:
            self.current_phase = RoundPhase.RESOLUTION
            self._resolve_round()
        elif self.current_phase == RoundPhase.RESOLUTION:
            self._start_new_round()

        self.notify_observers()

    def _execute_actions(self):
        # Sort actions by priority
        self.action_queue.sort()
        
        results = []
        for action in self.action_queue:
            if action.can_execute():
                result = action.execute()
                results.append(result)
                if result.success:
                    self.executed_actions.append(action)

        # Clear action queue after execution
        self.action_queue.clear()

    def _resolve_round(self):
        # Handle any end-of-round effects here
        # For now, just advance to next round
        pass

    def _start_new_round(self):
        self.current_round += 1
        self.current_phase = RoundPhase.PLAYER_PLANNING
        self.executed_actions.clear()
        
        # Reset unit action states
        # This would be handled by notifying units to reset their round state

    def end_turn(self):
        if self.current_phase == RoundPhase.PLAYER_PLANNING:
            self.advance_phase()

    def subscribe(self, observer: Any):
        self._observers.append(observer)

    def unsubscribe(self, observer: Any):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            if hasattr(observer, 'on_round_update'):
                observer.on_round_update(self)

    def get_round_info(self) -> dict:
        return {
            'round': self.current_round,
            'phase': self.current_phase,
            'queued_actions': len(self.action_queue),
            'can_act': self.current_phase == RoundPhase.PLAYER_PLANNING
        }


# Global instance
round_manager = RoundManager()