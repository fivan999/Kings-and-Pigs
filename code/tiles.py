import pygame
from support import load_images


# обычная клетка без картинки
class Tile(pygame.sprite.Sprite):
    def __init__(self, position: tuple, tile_size: int = 1):
        super().__init__()
        self.image = pygame.Surface((tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=position)


# клетка с картинкой
class StaticTile(Tile):
    def __init__(self, position: tuple, surface: pygame.Surface):
        super().__init__(position)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)


# класс для анимированной клетки
class AnimatedTile(Tile):
    def __init__(self, position: tuple, path: str):
        super().__init__(position)
        self.images = load_images(path)  # картинки для анимации

        self.image_index = 0  # текущая картинка
        self.animation_speed = 0.15  # скорость анимации
        self.image = self.images[self.image_index]

    # анимация
    def animate(self) -> None:
        self.image_index = (self.image_index + self.animation_speed) % len(self.images)
        self.image = self.images[int(self.image_index)]

    def update(self) -> None:
        self.animate()
