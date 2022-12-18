import pygame
from tile import *
from settings import TILE_SIZE
from hero import Hero
from settings import SCREEN_SIZE
from support import *
from enemy import *


class Level:
    def __init__(self, level, screen):
        self.screen = screen

        self.hero = pygame.sprite.GroupSingle()
        self.create_tile_group(import_csv(level["hero"]), "hero")

        self.terrain_sprites = self.create_tile_group(import_csv(level["terrain"]),
                                                      "terrain")
        self.background_sprites = self.create_tile_group(import_csv(level["background"]),
                                                         "background")
        self.decoration_sprites = self.create_tile_group(import_csv(level["decorations"]),
                                                         "decorations")
        self.box_sprites = self.create_tile_group(import_csv(level["box"]), "box")
        self.diamond_sprites = self.create_tile_group(import_csv(level["diamonds"]),
                                                      "diamonds")
        self.platform_sprites = self.create_tile_group(import_csv(level["default_platforms"]),
                                                       "default_platforms")
        self.backgroud_door_sprite = self.create_tile_group(import_csv(level["background_door"]),
                                                            "background_door")
        self.active_door_sprite = self.create_tile_group(import_csv(level["door"]),
                                                         "door")
        self.enemy_block = pygame.sprite.Group()
        self.enemies_sprites = self.create_tile_group(import_csv(level["pigs"]),
                                                      "pigs")

        self.world_shift = 0
        self.cur_x = None

    @staticmethod
    def define_tile_type(graphics_type):
        tiles = list()

        if graphics_type == "terrain" or graphics_type == "background":
            tiles = import_graphics("../graphics/terrain/terrain.png")
        elif graphics_type == "decorations":
            tiles = import_graphics("../graphics/decorations/decorations.png")
        elif graphics_type == "default_platforms":
            tiles = import_graphics("../graphics/decorations/default_platforms.png", y_size=15)

        return tiles

    def create_tile_group(self, csv_data, graphics_type):
        sprite_group = pygame.sprite.Group()
        tiles = self.define_tile_type(graphics_type)

        for row_ind, row in enumerate(csv_data):
            for col_ind, col in enumerate(row):
                if col == -1:
                    continue
                x, y = col_ind * TILE_SIZE, row_ind * TILE_SIZE
                if graphics_type == "hero":
                    self.hero.add(Hero((x, y)))
                    return
                elif graphics_type == "box":
                    sprite_group.add(Box((x, y)))
                elif graphics_type == "diamonds":
                    sprite_group.add(Diamond((x, y), "../graphics/stuff/animate_diamonds/"))
                elif graphics_type == "background_door":
                    sprite_group.add(Door((x, y), False))
                elif graphics_type == "door":
                    sprite_group.add(Door((x, y), True))
                elif graphics_type == "pigs":
                    if col:
                        sprite_group.add(Pig((x, y)))
                    else:
                        self.enemy_block.add(Tile((x, y), tile_size=TILE_SIZE))
                else:
                    tile = tiles[col]
                    sprite_group.add(StaticTile((x, y), tile))

        return sprite_group

    def enemy_collision(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.enemy_block, dokill=False):
                enemy.reverse()

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

        tiles_group = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        for tile in tiles_group:
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

        tiles_group = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        for tile in tiles_group:
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
        self.background_sprites.update(self.world_shift)
        self.background_sprites.draw(self.screen)

        self.decoration_sprites.update(self.world_shift)
        self.decoration_sprites.draw(self.screen)

        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.screen)

        self.diamond_sprites.update(self.world_shift)
        self.diamond_sprites.draw(self.screen)

        self.platform_sprites.update(self.world_shift)
        self.platform_sprites.draw(self.screen)

        self.backgroud_door_sprite.update(self.world_shift)
        self.backgroud_door_sprite.draw(self.screen)

        self.active_door_sprite.update(self.world_shift)
        self.active_door_sprite.draw(self.screen)

        self.enemies_sprites.update(self.world_shift)
        self.enemy_collision()
        self.enemies_sprites.draw(self.screen)

        self.enemy_block.update(self.world_shift)

        self.box_sprites.update(self.world_shift)
        self.box_sprites.draw(self.screen)

        self.hero.update()
        self.horizontal_move()
        self.vertical_move()
        self.scroll()
        self.hero.draw(self.screen)
