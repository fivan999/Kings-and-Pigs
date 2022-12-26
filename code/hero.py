import pygame
from support import load_images


class Hero(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.import_animation_images()
        self.image_index = 0
        self.animation_speed = 0.15
        self.image = self.animations["idle"][self.image_index]
        self.rect = self.image.get_rect(topleft=position)

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 6
        self.gravity = 0.7
        self.jump_speed = -10
        self.health = 3
        self.damage_time = 0

        self.status = "idle"
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_right = False
        self.on_left = False
        self.finished_level = False

    def import_animation_images(self):
        self.animations = {"idle": list(), "jump": list(),
                           "run": list(), "fall": list(),
                           "attack": list()}

        for condition in self.animations:
            self.animations[condition] = load_images("../graphics/character/" + condition + '/')

    def jump(self):
        self.direction.y = self.jump_speed

    def use_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def get_damage(self):
        if not self.finished_level:
            self.damage_time = 2
            self.health = max(self.health - 1, 0)
            self.jump()
            self.direction.x = -1

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

    def pass_damage_time(self):
        self.damage_time = max(self.damage_time - 0.02, 0)

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
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, flip_x=True, flip_y=False)

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
