import pygame
from random import randint
from tiles import AnimatedTile
from settings import TILE_SIZE
from support import make_path


class Pig(AnimatedTile):
    path = make_path("../graphics/enemies/run/")

    def __init__(self, position: tuple):
        super().__init__(position, Pig.path)
        # зададим позицию врага
        self.rect = self.image.get_rect(topleft=position)
        self.rect.y += TILE_SIZE - self.image.get_height() - 2

        self.direction = -1  # направление движения врага
        self.speed = randint(2, 4)
        self.back_move = False  # если враг направлен вправо

    # разворот
    def reverse(self) -> None:
        self.direction *= -1
        self.back_move = not self.back_move

    # перемещение врага
    def move(self) -> None:
        self.rect.x += self.direction * self.speed

    def update(self) -> None:
        super().update()
        if self.back_move:  # переворачиваем, если враг направлен вправо
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
        self.move()
