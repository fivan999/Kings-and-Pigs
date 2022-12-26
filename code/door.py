from tile import StaticTile
import pygame
from support import load_images
from settings import TILE_SIZE


class Door(StaticTile):
    path_closed = "../graphics/door/idle/closed.png"
    path_opened = "../graphics/door/idle/opened.png"

    def __init__(self, position, is_active):
        if is_active:
            img = pygame.image.load(Door.path_closed).convert_alpha()
            self.images = load_images("../graphics/door/opening/")
        else:
            img = pygame.image.load(Door.path_opened).convert_alpha()
            self.images = load_images("../graphics/door/closing/")

        super().__init__(position, img)
        self.is_active = is_active
        self.time_before_closing = 5
        self.rect.y -= self.image.get_height() - TILE_SIZE
        self.animation_started = False
        self.finished_animation = False

    def start_animation(self):
        if not self.animation_started:
            self.animation_started = True
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
        elif not self.finished_animation and not self.is_active and self.time_before_closing == 0:
            self.start_animation()
        else:
            self.time_before_closing = max(self.time_before_closing - 0.1, 0)
