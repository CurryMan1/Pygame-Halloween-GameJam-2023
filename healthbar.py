import pygame
from utils import *

class Healthbar:
    WIDTH = 130
    HEIGHT = 20
    BORDER = 3

    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.hp = max_hp

    def draw(self, surf, center):
        border = pygame.surface.Surface((self.WIDTH + self.BORDER * 2, self.HEIGHT + self.BORDER * 2))
        border.fill(BLACK)
        redbar = pygame.surface.Surface((self.WIDTH, self.HEIGHT))
        redbar.fill(RED)
        greenbar = pygame.surface.Surface((self.WIDTH * (self.hp / self.max_hp), self.HEIGHT))
        greenbar.fill(GREEN)

        redbar.blit(greenbar, (0, 0))
        border.blit(redbar, (self.BORDER, self.BORDER))
        surf.blit(border, (center[0] - self.WIDTH / 2, center[1]-70))