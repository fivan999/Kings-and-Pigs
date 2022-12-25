from tile import StaticTile
import pygame
from support import load_images
from settings import TILE_SIZE


class Door(StaticTile):
    path = "../graphics/door/idle/door.png"

    def __init__(self, position, is_active):
        super().__init__(position, pygame.image.load(self.path).convert_alpha())
        self.is_active = is_active
        self.rect.y -= self.image.get_height() - TILE_SIZE
        self.animation_started = False
        self.finished_animation = False

    def start_animation(self):
        if not self.animation_started:
            self.animation_started = True
            self.images = load_images("../graphics/door/opening/")

            self.image_index = 0
            self.animation_speed = 0.15
            self.image = self.images[self.image_index]

    def animate(self):
        self.image_index = min(self.image_index + self.animation_speed,
                               len(self.images) - 1)
        if self.image_index == len(self.images) - 1:
            self.finished_animation = True
        self.image = self.images[int(self.image_index)]

    def update(self):
        if self.animation_started:
            self.animate()
