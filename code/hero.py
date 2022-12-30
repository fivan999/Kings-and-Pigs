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

        self.direction = pygame.math.Vector2(0, 0)  # направление игрока по x и y
        self.speed = 6  # горизонтальная скорость
        self.gravity = 0.7  # усиление гравитации
        self.jump_speed = -10  # скорость прыжка
        self.health = 3  # здоровье
        self.damage_time = 0  # время до получения следующего урона

        self.status = "idle"  # текущее состояние (на месте, бег, прыжок, падение)
        self.facing_right = True  # смотрит вправо
        self.on_ground = False  # на земле
        self.on_ceiling = False  # головой уперся в потолок
        self.on_right = False  # уперся вправо
        self.on_left = False  # уперся влево
        self.finished_level = False  # закончил уровень

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

    # падение за счет гравитации
    def use_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    # получение урона
    def get_damage(self):
        if not self.finished_level:
            self.damage_time = 2
            self.health = max(self.health - 1, 0)
            self.jump()
            self.direction.x = -1

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

        image = animation[int(self.image_index)]

        # переворачиваем, если смотрит влево
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, flip_x=True, flip_y=False)

        # картинки игрока имеют разную ширину и высоту
        # это нужно, чтобы спрайт игрока не заходил на статичные спрайты
        if self.on_ground:
            if self.on_right:
                self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
            elif self.on_left:
                self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
            else:
                self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.on_ceiling:
            if self.on_right:
                self.rect = self.image.get_rect(topright=self.rect.topright)
            elif self.on_left:
                self.rect = self.image.get_rect(topleft=self.rect.topleft)
            else:
                self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def update(self):
        self.pass_damage_time()
        self.animate()

    # отрисовка игрока
    def draw(self, screen):
        screen.blit(self.image, self.rect)
