import pygame
from tile import AnimatedTile
from settings import TILE_SIZE


class Pig(AnimatedTile):
    def __init__(self, position):
        super().__init__(position, "../graphics/enemies/run/")
        self.rect = self.image.get_rect(topleft=position)
        self.rect.y += TILE_SIZE - self.image.get_height() - 1
        self.speed = -1
        self.back_move = False

    def reverse(self):
        self.speed *= -1
        if self.speed > 0:
            self.rect.x += 5
        else:
            self.rect.x -= 5
        self.back_move = not self.back_move

    def move(self):
        self.rect.x += self.speed

    def update(self):
        super().update()
        if self.back_move:
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
        self.move()
