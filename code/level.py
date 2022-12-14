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
                if graphics_type == "box":
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

    def render(self):
        self.background_sprites.update(self.world_shift)
        self.background_sprites.draw(self.screen)

        self.decoration_sprites.update(self.world_shift)
        self.decoration_sprites.draw(self.screen)

        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.screen)

        self.box_sprites.update(self.world_shift)
        self.box_sprites.draw(self.screen)

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

        # self.enemy_block.update(self.world_shift)
        # self.enemy_block.draw(self.screen)
