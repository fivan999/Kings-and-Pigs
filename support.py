import os
import pygame


def load_images(path):
    images = sorted([name for _, __, names in os.walk(path) for name in names])
    return [pygame.image.load(path + name).convert_alpha() for name in images]
