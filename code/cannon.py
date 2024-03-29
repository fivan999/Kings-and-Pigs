import pygame
from random import randint
from tiles import StaticTile
from settings import TILE_SIZE
from support import load_images, make_path


class Cannon(StaticTile):
    path = make_path("../graphics/cannon/idle/idle.png")

    def __init__(self, position: tuple):
        super().__init__(position, pygame.image.load(Cannon.path).convert_alpha())
        self.idle_image = pygame.Surface((self.image.get_width(), self.image.get_height()),
                                         pygame.SRCALPHA)  # картинка для не стреляющей пушки
        self.idle_image.blit(self.image, (0, 0))
        self.time_before_shoot = randint(6, 14)  # время до анимации выстрела
        self.image_index = -1  # индекс картинки для анимации
        self.speed_shoot_time = 0.03  # скорость
        self.animation_started = False  # началась ли анимация
        self.shot = False  # произошел ли выстрел на текущей анимации
        self.images = load_images(make_path("../graphics/cannon/shoot/"))  # картинки для анимации

        # немного изменим позицию
        self.rect.y += TILE_SIZE - self.image.get_height()
        self.rect.x += TILE_SIZE - self.image.get_width()

    # начинаем анимацию выстрела
    def start_animation(self) -> None:
        if not self.animation_started:
            self.animation_started = True
            self.shot = False
            self.image_index = 0
            self.animation_speed = 0.15
            self.image = self.images[self.image_index]

    # сама анимация
    def animate(self) -> None:
        self.image_index = min(self.image_index + self.animation_speed,
                               len(self.images) - 1)

        # если анимация закончилась
        if self.image_index == len(self.images) - 1:
            self.time_before_shoot = 5
            self.image = self.idle_image
            self.animation_started = False
            self.image_index = -1
            self.shot = False
        else:
            self.image = self.images[int(self.image_index)]

    # обновляем время до выстрела
    def pass_shoot_time(self) -> None:
        self.time_before_shoot = max(self.time_before_shoot - self.speed_shoot_time, 0)
        if self.time_before_shoot == 0:
            self.start_animation()

    def update(self) -> None:
        self.pass_shoot_time()
        if self.animation_started:
            self.animate()


class CannonBall(StaticTile):
    path = make_path("../graphics/cannon/ball.png")

    def __init__(self, position: tuple):
        super().__init__(position, pygame.image.load(CannonBall.path).convert_alpha())
        self.speed = randint(8, 14)  # скорость летящего шара

    # двигаем шар
    def move(self) -> None:
        self.rect.x -= self.speed

    def update(self) -> None:
        self.move()
