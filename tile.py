import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect(topleft=position)

    def update(self, delta_x=0):
        self.rect.x += delta_x
