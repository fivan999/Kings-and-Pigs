import pygame
from support import load_images


# игрок
class Hero(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.import_animation_images()  # подгрузка всех картинок для анимации
        self.image_index = 0  # текущая картинка
        self.animation_speed = 0.15  # скорость анимации
        self.image = self.animations["idle"][self.image_index]
        self.rect = self.image.get_rect(topleft=position)  # устанавляваем позицию
        # для столкновений с клетками нам нужен другой квадрат, потому что часть предыдущего это кувалда
        self.terrain_collision_rect = pygame.Rect((self.rect.left + 12, self.rect.top), (25, self.rect.height))

        # основные механики
        self.direction = pygame.math.Vector2(0, 0)  # направление игрока по x и y
        self.speed = 4  # горизонтальная скорость
        self.gravity = 0.7  # усиление гравитации
        self.jump_speed = -10  # скорость прыжка
        self.health = 3  # здоровье
        self.damage_time = 0  # время до получения следующего урона
        self.fixed_height = 26  # высоты картинок разные, для камеры используем эту

        # флаги
        self.status = "idle"  # текущее состояние (на месте, бег, прыжок, падение, атака)
        self.facing_right = True  # смотрит вправо
        self.on_ground = False  # на земле
        self.finished_level = False  # закончил уровень

        # звуки
        self.jump_sound = pygame.mixer.Sound("../sounds/hero/jump.mp3")
        self.get_damage_sound = pygame.mixer.Sound("../sounds/hero/get_damage.mp3")
        self.attack_sound = pygame.mixer.Sound("../sounds/hero/attack.mp3")

    # подгрузка всех картинок для анимации
    def import_animation_images(self):
        self.animations = {"idle": list(), "jump": list(),
                           "run": list(), "fall": list(),
                           "attack": list()}

        for condition in self.animations:
            self.animations[condition] = load_images("../graphics/character/" + condition + '/')

    # прыжок
    def jump(self):
        self.direction.y = self.jump_speed
        self.jump_sound.play()

    # падение за счет гравитации
    def use_gravity(self):
        self.direction.y += self.gravity
        self.terrain_collision_rect.y += self.direction.y

    # получение урона
    def get_damage(self):
        if not self.finished_level:
            self.damage_time = 2
            self.health = max(self.health - 1, 0)
            self.jump()
            self.direction.x = -1
            self.get_damage_sound.play()

    # обновление текущего состояния игрока
    def get_status(self):
        if self.status == 'attack':
            return

        if self.direction.y < 0:
            self.status = "jump"
        elif self.direction.y > 0.85:
            self.status = "fall"
        elif self.direction.x != 0:
            self.status = "run"
        else:
            self.status = "idle"

    # обновление времени до следующего получения урона
    def pass_damage_time(self):
        self.damage_time = max(self.damage_time - 0.02, 0)

    # анимация
    def animate(self):
        self.get_status()
        animation = self.animations[self.status]

        self.image_index = self.image_index + self.animation_speed
        if self.image_index > len(animation):
            if self.status == 'attack':
                self.status = None
                self.animate()
                return
            self.image_index %= len(animation)

        self.image = animation[int(self.image_index)]

        # переворачиваем, если смотрит влево
        if self.facing_right:
            self.rect.bottomright = self.terrain_collision_rect.bottomright
        else:
            self.image = pygame.transform.flip(self.image, flip_x=True, flip_y=False)
            self.rect.bottomleft = self.terrain_collision_rect.bottomleft

        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def update(self):
        self.pass_damage_time()
        self.animate()

    # отрисовка игрока
    def draw(self, screen):
        screen.blit(self.image, self.rect)
