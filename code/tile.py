import pygame
from settings import TILE_SIZE


class Tile(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((1, 1))
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
        super().__init__(position, pygame.image.load(self.path))
        self.rect.y += TILE_SIZE - self.image.get_height()


class Platform(StaticTile):
    def __init__(self, position, surface):
        super().__init__(position, surface)
        self.image = pygame.Surface(self.image, pygame.SRCALPHA)
