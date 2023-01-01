import pygame
from random import randint
from tile import AnimatedTile
from settings import TILE_SIZE


class Pig(AnimatedTile):
    def __init__(self, position):
        super().__init__(position, "../graphics/enemies/run/")
        # зададим позицию врага
        self.rect = self.image.get_rect(topleft=position)
        self.rect.y += TILE_SIZE - self.image.get_height() - 1

        self.direction = -1  # направление движения врага
        self.speed = randint(1, 2)
        self.back_move = False  # если враг направлен вправо

    # разворот
    def reverse(self):
        self.direction *= -1
        self.back_move = not self.back_move

    # перемещение врага
    def move(self):
        self.rect.x += self.direction * self.speed

    def update(self):
        super().update()
        if self.back_move:  # переворачиваем, если враг направлен вправо
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
        self.move()
