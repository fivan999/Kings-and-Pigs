import pygame
from tile import *
from settings import TILE_SIZE
from hero import Hero
from settings import SCREEN_SIZE
from support import *


class Level:
    def __init__(self, level, screen):
        self.screen = screen

        self.terrain_sprites = self.create_tile_group(import_csv(level["terrain"]),
                                                      "terrain")
        self.background_sprites = self.create_tile_group(import_csv(level["background"]),
                                                         "background")
        self.box_sprites = self.create_tile_group(import_csv(level["box"]), "box")

        self.world_shift = 0

    def create_tile_group(self, csv_data, graphics_type):
        sprite_group = pygame.sprite.Group()
        if graphics_type == "terrain" or graphics_type == "background":
            tiles = import_graphics("../graphics/terrain/terrain.png")
        elif graphics_type == "box":
            tiles = import_graphics("../graphics/decorations/box.png")

        for row_ind, row in enumerate(csv_data):
            for col_ind, col in enumerate(row):
                if col == -1:
                    continue
                x, y = col_ind * TILE_SIZE, row_ind * TILE_SIZE
                tile = tiles[col]
                sprite_group.add(StaticTIle((x, y), tile))

        return sprite_group

    def render(self):
        self.terrain_sprites.draw(self.screen)
        self.terrain_sprites.update(self.world_shift)

        self.background_sprites.update(self.world_shift)
        self.background_sprites.draw(self.screen)

        self.box_sprites.update(self.world_shift)
        self.box_sprites.update(self.screen)