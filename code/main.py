import sys
import pygame
from settings import *
from level import Level
from game_data import level_1


def main():
    pygame.init()
    pygame.display.set_caption("Kings & Pigs")

    screen = pygame.display.set_mode(SCREEN_SIZE)

    clock = pygame.time.Clock()
    level = Level(level_1, screen)

    running = True
    while running:
        time = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        level.render()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
