from settings import SCREEN_SIZE


class Camera:
    # начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_SIZE[0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - SCREEN_SIZE[1] // 2)
