import pygame
from settings import SCREEN_SIZE


class Camera:
    def __init__(self, target, world_size):
        self.world_size = world_size  # размер самой карты из Tiled
        self.target = target  # на что ориентируемся (игрок)
        self.camera = pygame.Vector2(0, 0)  # само смещение

        # некоторые уровни имеют ширину или высоту меньше экранной
        # поэтому, чтобы такой уровень находился примерно посередине экрана, нам нужны сдвиги
        self.x_shift = max((SCREEN_SIZE[0] - self.world_size[0]) // 2, 0)
        self.y_shift = max((SCREEN_SIZE[1] - self.world_size[1]) // 2, 0)

    # передвинуть объект target
    def apply(self, target):
        return target.rect.move((self.camera.x, self.camera.y))

    # обновить смещение
    def update(self):
        x = -self.target.rect.center[0] + SCREEN_SIZE[0] / 2
        y = -self.target.rect.center[1] + SCREEN_SIZE[1] / 2
        self.camera += (pygame.Vector2((x, y)) - self.camera) * 0.05
        self.camera.x = max(-(self.world_size[0] - SCREEN_SIZE[0]), min(0, self.camera.x)) - self.x_shift
        self.camera.y = max(-(self.world_size[1] - SCREEN_SIZE[1]), min(0, self.camera.y)) - self.y_shift
