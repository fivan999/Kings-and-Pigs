import pygame
from support import load_images


class BaseEffect(pygame.sprite.Sprite):
    def __init__(self, position, path):
        super().__init__()
        self.image_index = 0
        self.animation_speed = 0.3
        self.images = load_images(path)
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=position)

    def animate(self):
        if self.image_index >= len(self.images):
            self.kill()
            return
        self.image = self.images[int(self.image_index)]
        self.image_index += self.animation_speed

    def update(self):
        self.animate()


class EnemyDestroyEffect(BaseEffect):
    path = '../graphics/explosion/'

    def __init__(self, position):
        super().__init__(position, EnemyDestroyEffect.path)


class BombExplosionEffect(BaseEffect):
    path = "../graphics/explosion/bomb/"

    def __init__(self, position):
        super().__init__(position, BombExplosionEffect.path)
