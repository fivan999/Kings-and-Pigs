import pygame
from settings import TILE_SIZE
from support import load_images


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, tile_size=1):
        super().__init__()
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=position)


class StaticTile(Tile):
    def __init__(self, position, surface):
        super().__init__(position)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)


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

    def update(self):
        self.animate()


class Diamond(AnimatedTile):
    path = "../graphics/stuff/animate_diamonds/"

    def __init__(self, position):
        super().__init__(position, Diamond.path)
        self.rect.x += TILE_SIZE // 2 - self.image.get_width() // 2
        self.rect.y += TILE_SIZE // 2 - self.image.get_height() // 2


class Box(StaticTile):
    path = "../graphics/decorations/box.png"

    def __init__(self, position):
        super().__init__(position, pygame.image.load(self.path).convert_alpha())
        self.rect.y += TILE_SIZE - self.image.get_height()
        self.rect.x += TILE_SIZE - self.image.get_width()
