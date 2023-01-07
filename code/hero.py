import pygame
from support import load_images


# игрок
class Hero(pygame.sprite.Sprite):
    def __init__(self, position):
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
        self.fixed_height = 52  # высоты картинок разные, для камеры используем эту

        # флаги
        self.status = "idle"  # текущее состояние (на месте, бег, прыжок, падение, атака)
        self.facing_right = True  # смотрит вправо
        self.on_ground = False  # на земле
        self.finished_level = False  # закончил уровень
        self.died = False  # закончилась анимация смерти

        # звуки
        self.jump_sound = pygame.mixer.Sound("../sounds/hero/jump.mp3")
        self.get_damage_sound = pygame.mixer.Sound("../sounds/hero/get_damage.mp3")
        self.attack_sound = pygame.mixer.Sound("../sounds/hero/attack.mp3")

    # загрузка всех картинок для анимации
    def import_animation_images(self):
        self.animations = {"idle": list(), "jump": list(),
                           "run": list(), "fall": list(),
                           "attack": list(), "die": list()}

        for condition in self.animations:
            self.animations[condition] = load_images("../graphics/character/" + condition + '/')

    # атака
    def attack(self):
        if self.on_ground and self.status == "idle":
            self.status = "attack"
            self.image_index = 0
            if self.facing_right:
                self.attack_rect = pygame.Rect((self.terrain_collision_rect.left + 49, self.terrain_collision_rect.top),
                                               (50, self.terrain_collision_rect.height))
            else:
                self.attack_rect = pygame.Rect((self.terrain_collision_rect.left - 49, self.terrain_collision_rect.top),
                                               (50, self.terrain_collision_rect.height))
            self.attack_sound.play()

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
    def pass_damage_time(self):
        self.damage_time = max(self.damage_time - 0.02, 0)

    # обновляем положение игрока
    def update_rect(self):
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
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        if self.status == "die":
            self.rect.top += 10

    # анимация
    def animate(self):
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

    def update(self):
        self.pass_damage_time()
        self.animate()

    # отрисовка игрока
    def draw(self, screen):
        screen.blit(self.image, self.rect)
