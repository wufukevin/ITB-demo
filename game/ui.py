import pygame
from pygame import Color, Surface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.rounds import RoundManager


class RoundUI:
    def __init__(self, surface: Surface):
        self.surface = surface
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def draw_round_info(self, round_manager: 'RoundManager'):
        round_info = round_manager.get_round_info()
        
        # Draw round number
        round_text = self.font.render(f"Round {round_info['round']}", True, Color('white'))
        self.surface.blit(round_text, (10, 10))
        
        # Draw phase indicator
        phase_color = self._get_phase_color(round_info['phase'])
        phase_name = round_info['phase'].name.replace('_', ' ').title()
        phase_text = self.small_font.render(phase_name, True, phase_color)
        self.surface.blit(phase_text, (10, 50))
        
        # Draw queued actions count
        if round_info['queued_actions'] > 0:
            actions_text = self.small_font.render(f"Actions: {round_info['queued_actions']}", True, Color('yellow'))
            self.surface.blit(actions_text, (10, 75))
        
        # Draw instructions
        if round_info['can_act']:
            instruction_text = self.small_font.render("SPACE: End Turn", True, Color('white'))
            self.surface.blit(instruction_text, (10, self.surface.get_height() - 30))
        else:
            executing_text = self.small_font.render("Executing Actions...", True, Color('orange'))
            self.surface.blit(executing_text, (10, self.surface.get_height() - 30))
    
    def _get_phase_color(self, phase):
        from game.rounds import RoundPhase
        
        color_map = {
            RoundPhase.PLAYER_PLANNING: Color('green'),
            RoundPhase.EXECUTION: Color('orange'), 
            RoundPhase.RESOLUTION: Color('red')
        }
        return color_map.get(phase, Color('white'))