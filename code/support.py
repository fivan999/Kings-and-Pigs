import os
import pygame
import csv
from settings import TILE_SIZE


def load_images(path):
    images = sorted([name for _, __, names in os.walk(path) for name in names])
    return [pygame.image.load(path + name).convert_alpha() for name in images]


def import_csv(path):
    with open(path, encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",", quoting=csv.QUOTE_NONE)
        return [list(map(int, row)) for row in reader]


def import_graphics(path):
    tiles = list()
    surface = pygame.image.load(path).convert_alpha()
    cnt_x_tiles = surface.get_width() // TILE_SIZE
    cnt_y_tiles = surface.get_height() // TILE_SIZE

    for row_ind in range(cnt_y_tiles):
        for col_ind in range(cnt_x_tiles):
            x, y = col_ind * TILE_SIZE, row_ind * TILE_SIZE
            square = pygame.Surface((TILE_SIZE, TILE_SIZE))
            square.blit(surface, (0, 0), pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
            tiles.append(square)

    return tiles
