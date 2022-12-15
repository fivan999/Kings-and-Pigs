import pygame
from tile import AnimatedTile
from settings import TILE_SIZE


class Pig(AnimatedTile):
    def __init__(self, position):
        super().__init__(position, "../graphics/enemies/run/")
        self.rect.y += TILE_SIZE - self.image.get_height() - 1
        self.speed = -1
        self.back_move = False

    def reverse(self):
        self.speed *= -1
        self.back_move = not self.back_move

    def move(self):
        self.rect.x += self.speed

    def update(self, delta_x=0):
        super().update(delta_x)
        if self.back_move:
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
        self.move()
