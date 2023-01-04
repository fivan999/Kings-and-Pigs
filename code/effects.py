import pygame
from support import load_images


# базовый эффект, уничтожающийся после окончания анимации
class BaseEffect(pygame.sprite.Sprite):
    def __init__(self, position, path):
        super().__init__()
        self.image_index = 0  # текущая картинка
        self.animation_speed = 0.3  # скорость анимации
        self.images = load_images(path)  # картинки для анимации
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=position)  # позиция эффекта
        self.killed = False  # закончилась ли анимация

    # анимация
    def animate(self):
        if self.image_index >= len(self.images):  # если анимация закончилась
            self.killed = True
            return
        self.image = self.images[int(self.image_index)]
        self.image_index += self.animation_speed

    def update(self):
        self.animate()


class EnemyDestroyEffect(BaseEffect):
    path = '../graphics/enemies/die/'

    def __init__(self, position):
        super().__init__(position, EnemyDestroyEffect.path)
        self.animation_speed = 0.05
        self.rect = self.image.get_rect(bottomleft=position)
        self.rect.y += 8


class BombExplosionEffect(BaseEffect):
    path = "../graphics/explosion/bomb/"

    def __init__(self, position):
        super().__init__(position, BombExplosionEffect.path)

    def update(self):
        super().update()
        if self.killed:
            self.kill()
