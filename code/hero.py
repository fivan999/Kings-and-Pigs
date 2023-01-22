import pygame
from support import load_images, make_path
from sounds import JUMP_SOUND, HERO_DAMAGE_SOUND, ATTACK_SOUND


# игрок
class Hero(pygame.sprite.Sprite):
    def __init__(self, position: tuple):
        super().__init__()
        self.import_animation_images()  # загрузка всех картинок для анимации
        self.image_index = 0  # текущая картинка
        self.animation_speed = 0.15  # скорость анимации
        self.image = self.animations["idle"][self.image_index]
        self.rect = self.image.get_rect(topleft=position)  # устанавливаем позицию
        # для столкновений с клетками нам нужен другой квадрат, потому что часть предыдущего это кувалда
        self.terrain_collision_rect = pygame.Rect((self.rect.left + 24, self.rect.top), (50, self.rect.height))
        # для атаки нужен другой квадрат, так как атакуем мы только кувалдой
        self.attack_rect = None

        # основные механики
        self.direction = pygame.math.Vector2(0, 0)  # направление игрока по x и y
        self.speed = 6  # горизонтальная скорость
        self.gravity = 0.55  # усиление гравитации
        self.jump_speed = -12  # скорость прыжка
        self.health = 3  # здоровье
        self.damage_time = 0  # время до получения следующего урона
        self.invibility_index = 0  # определяет индекс эффекта невидимости

        # флаги
        self.status = "idle"  # текущее состояние (на месте, бег, прыжок, падение, атака)
        self.facing_right = True  # смотрит вправо
        self.on_ground = False  # на земле
        self.finished_level = False  # закончил уровень
        self.died = False  # закончилась анимация смерти

    # загрузка всех картинок для анимации
    def import_animation_images(self) -> None:
        self.animations = {"idle": list(), "jump": list(),
                           "run": list(), "fall": list(),
                           "attack": list(), "die": list()}

        for condition in self.animations:
            self.animations[condition] = load_images(make_path("../graphics/character/" + condition + '/'))

    # атака
    def attack(self) -> None:
        self.status = "attack"
        self.image_index = 0
        left_shift = 49 * int(self.facing_right)
        self.attack_rect = pygame.Rect((self.terrain_collision_rect.left + left_shift, self.terrain_collision_rect.top),
                                       (50, self.terrain_collision_rect.height))
        ATTACK_SOUND.play()

    # прыжок
    def jump(self) -> None:
        self.direction.y = self.jump_speed
        JUMP_SOUND.play()

    # падение за счет гравитации
    def use_gravity(self) -> None:
        self.direction.y += self.gravity
        self.terrain_collision_rect.y += self.direction.y

    # получение урона
    def get_damage(self) -> None:
        if not self.finished_level:
            self.damage_time = 2
            self.health = max(self.health - 1, 0)
            self.jump()
            self.direction.x = -1
            self.invisible_image_loops = 6
            HERO_DAMAGE_SOUND.play()

    # обновление текущего состояния игрока
    def get_status(self) -> None:
        if self.status in ("attack", "die"):
            return

        if self.health == 0:
            self.status = "die"
            self.image_index = 0
            self.animation_speed = 0.05
        elif self.direction.y < 0:
            self.status = "jump"
        elif self.direction.y > 0.85:
            self.status = "fall"
        elif self.direction.x != 0:
            self.status = "run"
        else:
            self.status = "idle"

    # обновление времени до следующего получения урона
    def pass_damage_time(self) -> None:
        self.damage_time = max(self.damage_time - 0.02, 0)
        self.make_invivible()

    # изменяем невидимость игрока
    def make_invivible(self) -> None:
        # если игрок получил урон и индекс невидидимости в нужном диапазоне, делаем игрока прозрачным
        if self.invibility_index > 0 and self.damage_time > 0 and self.status != "die":
            transparency = 80
        else:
            transparency = 255
        self.image.set_alpha(transparency)

        # изменяем индекс невидимости
        self.invibility_index -= 1
        if self.invibility_index <= -6:
            self.invibility_index = 6

    # обновляем положение игрока
    def update_rect(self) -> None:
        # у картинки атаки ширина больше, поэтому нужно располагать игрока по другому, если он атакует
        if self.facing_right:
            if self.status == "attack":
                self.rect.bottomleft = self.terrain_collision_rect.bottomleft
            else:
                self.rect.bottomright = self.terrain_collision_rect.bottomright
        else:
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
            if self.status == "attack":
                self.rect.bottomright = self.terrain_collision_rect.bottomright
            else:
                self.rect.bottomleft = self.terrain_collision_rect.bottomleft

        # выравниваем
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        if self.status == "die":
            self.rect.top += 10

    # анимация
    def animate(self) -> None:
        self.get_status()
        animation = self.animations[self.status]

        if self.status == "attack":
            self.image_index = self.image_index + 0.1
        else:
            self.image_index = self.image_index + self.animation_speed
        if self.image_index >= len(animation):
            if self.status == 'attack':
                self.status = None
                self.get_status()
                self.image_index = 0
                self.attack_rect = None
            elif self.status == "die":
                self.died = True
                self.image_index -= 1
            else:
                self.image_index %= len(animation)

        self.image = animation[int(self.image_index)]
        self.update_rect()

    # обновляем игрока
    def update(self) -> None:
        self.animate()
        self.pass_damage_time()
