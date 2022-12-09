import sys
import pygame
from settings import *
from level import Level


def main():
    pygame.init()
    pygame.display.set_caption("The Bebra Game")

    screen = pygame.display.set_mode(SCREEN_SIZE)

    clock = pygame.time.Clock()
    level = Level(level_map, screen)

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
