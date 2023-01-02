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
        if target.status == "idle":
            delta_height = target.rect.height % target.fixed_height
        else:
            delta_height = 0
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_SIZE[0] // 2)
        self.dy = -((target.rect.y + delta_height) + (target.rect.h - delta_height) // 2 - SCREEN_SIZE[1] // 2)
        target.terrain_collision_rect.x += self.dx
        target.terrain_collision_rect.y += self.dy
