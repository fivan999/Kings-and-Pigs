import pygame
from settings import TILE_SIZE
from support import load_images


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, tile_size=1):
        super().__init__()
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=position)

    def update(self, delta_x=0):
        self.rect.x += delta_x


class StaticTile(Tile):
    def __init__(self, position, surface):
        super().__init__(position)
        self.image = surface


class Box(StaticTile):
    path = "../graphics/decorations/box.png"

    def __init__(self, position):
        super().__init__(position, pygame.image.load(self.path).convert_alpha())
        self.rect.y += TILE_SIZE - self.image.get_height()
        self.rect.x += TILE_SIZE - self.image.get_width()


class Door(StaticTile):
    path = "../graphics/decorations/door.png"

    def __init__(self, position, is_active):
        super().__init__(position, pygame.image.load(self.path).convert_alpha())
        self.is_active = is_active
        self.rect.y -= self.image.get_height() - TILE_SIZE


class AnimatedTile(Tile):
    def __init__(self, position, path):
        super().__init__(position)
        self.images = load_images(path)

        self.image_index = 0
        self.animation_speed = 0.15
        self.image = self.images[self.image_index]

    def animate(self):
        self.image_index = (self.image_index + self.animation_speed) % len(self.images)
        self.image = self.images[int(self.image_index)]

    def update(self, delta_x=0):
        super().update(delta_x)
        self.animate()


class Diamond(AnimatedTile):
    def __init__(self, position, path):
        super().__init__(position, path)
        self.rect.x += TILE_SIZE // 2 - self.image.get_width() // 2
        self.rect.y += TILE_SIZE // 2 - self.image.get_height() // 2
