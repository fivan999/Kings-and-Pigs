import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect(topleft=position)

    def update(self, delta_x=0):
        self.rect.x += delta_x


class StaticTIle(Tile):
    def __init__(self, position, surface):
        super().__init__(position)
        self.image = surface
