import pygame
from settings import TILE_SIZE
from support import load_images


class Cannon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.

        self.time_before_shoot = 5
        self.finished_animation = False
