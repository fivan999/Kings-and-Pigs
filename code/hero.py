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

        self.status = "idle"
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_right = False
        self.on_left = False

    def import_animation_images(self):
        self.animations = {"idle": list(), "jump": list(),
                           "run": list(), "fall": list(),
                           "hit": list()}

        for condition in self.animations:
            self.animations[condition] = load_images("../graphics/character/" + condition + '/')

    def move_x(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()

        if keys[pygame.K_e] and self.status != "hit":
            self.status = "hit"

    def jump(self):
        self.direction.y = self.jump_speed

    def use_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def get_status(self):
        if self.direction.y < 0:
            self.status = "jump"
        elif self.direction.y > 0.85:
            self.status = "fall"
        elif self.direction.x != 0:
            self.status = "run"
        else:
            self.status = "idle"

    def animate(self):
        self.get_status()
        animation = self.animations[self.status]

        self.image_index = (self.image_index + self.animation_speed) % len(animation)

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
        self.move_x()
        self.animate()
