import pygame
from support import load_images


class EnemyDestroyEffect(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image_index = 0
        self.animation_speed = 0.3
        self.images = load_images('../graphics/explosion/')
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(topleft=position)

    def animate(self):
        if self.image_index >= len(self.images):
            self.kill()
            return

        self.image = self.images[int(self.image_index)]
        self.image_index += self.animation_speed

    def update(self):
        self.animate()
