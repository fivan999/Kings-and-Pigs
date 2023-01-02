import os
import pygame
import csv
from settings import TILE_SIZE


# подгрузить все файлы из нужной директории
def load_files(path):
    return sorted([name for _, __, names in os.walk(path) for name in names])


# подгрузить картинки из нужной директории
def load_images(path):
    return [pygame.image.load(path + name).convert_alpha() for name in load_files(path)]


# подгрузить звуки из нужной директории
def load_audio(path):
    return [pygame.mixer.Sound(path + name) for name in load_files(path)]


# подгрузить конфигурацию уровня из csv-файла
def import_csv(path):
    with open(path, encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=",", quoting=csv.QUOTE_NONE)
        return [list(map(int, row)) for row in reader]


# нарезать мелкие картинки из большой
def cut_images(path, x_size=TILE_SIZE, y_size=TILE_SIZE):
    tiles = list()
    surface = pygame.image.load(path).convert_alpha()
    cnt_x_tiles = surface.get_width() // x_size
    cnt_y_tiles = surface.get_height() // y_size

    for row_ind in range(cnt_y_tiles):
        for col_ind in range(cnt_x_tiles):
            x, y = col_ind * x_size, row_ind * y_size
            square = pygame.Surface((x_size, y_size), pygame.SRCALPHA)
            square.blit(surface, (0, 0), pygame.Rect(x, y, x_size, y_size))
            tiles.append(square)

    return tiles
