import pygame
from tile import Tile
from settings import TILE_SIZE
from hero import Hero
from settings import SCREEN_SIZE


class Level:
    def __init__(self, level, screen):
        self.screen = screen
        self.level = level
        self.tiles_group = pygame.sprite.Group()
        self.hero = pygame.sprite.GroupSingle()
        self.world_shift = 0
        self.cur_x = 0
        self.setup_level()

    def setup_level(self):
        for y in range(len(self.level)):
            for x in range(len(self.level[0])):
                cell = self.level[y][x]
                x_pos, y_pos = x * TILE_SIZE, y * TILE_SIZE
                if cell == "X":
                    self.tiles_group.add(Tile((x_pos, y_pos), TILE_SIZE))
                elif cell == "P":
                    self.hero.add(Hero((x_pos, y_pos)))

    def scroll(self):
        hero = self.hero.sprite
        hero_x = hero.rect.centerx
        direction_x = hero.direction.x

        if hero_x < SCREEN_SIZE[0] * 0.3 and direction_x < 0:
            self.world_shift = 8
            hero.speed = 0
        elif hero_x > SCREEN_SIZE[0] * 0.7 and direction_x > 0:
            self.world_shift = -1
            hero.speed = 0
        else:
            self.world_shift = 0
            hero.speed = 8

    def horizontal_move(self):
        hero = self.hero.sprite
        hero.rect.x += hero.direction.x * hero.speed

        for tile in self.tiles_group.sprites():
            if tile.rect.colliderect(hero.rect):
                if hero.direction.x < 0:
                    hero.rect.left = tile.rect.right
                    hero.on_left = True
                    self.cur_x = hero.rect.left
                elif hero.direction.x > 0:
                    hero.rect.right = tile.rect.left
                    hero.on_right = True
                    self.cur_x = hero.rect.right

        if hero.on_left and (hero.rect.left < self.cur_x or hero.direction.x >= 0):
            hero.on_left = False
        if hero.on_right and (hero.rect.right > self.cur_x or hero.direction.x <= 0):
            hero.on_right = False

    def vertical_move(self):
        hero = self.hero.sprite
        hero.use_gravity()

        for tile in self.tiles_group.sprites():
            if tile.rect.colliderect(hero.rect):
                if hero.direction.y > 0:
                    hero.rect.bottom = tile.rect.top
                    hero.on_ground = True
                elif hero.direction.y < 0:
                    hero.rect.top = tile.rect.bottom
                    hero.on_ceiling = True
                hero.direction.y = 0

        if hero.on_ground and hero.direction.y < 0 or hero.direction.y > 1:
            hero.on_ground = False
        if hero.on_ceiling and hero.direction.y > 0:
            hero.on_ceiling = False

    def render(self):
        self.tiles_group.update(delta_x=self.world_shift)
        self.tiles_group.draw(self.screen)

        self.hero.update()
        self.horizontal_move()
        self.vertical_move()
        self.hero.draw(self.screen)
        self.scroll()
