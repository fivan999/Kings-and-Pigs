import sys
import pygame
from settings import *
from game import Game
from game_data import levels


def main():
    pygame.init()
    pygame.display.set_caption("Kings & Pigs")

    screen = pygame.display.set_mode(SCREEN_SIZE)

    clock = pygame.time.Clock()
    game = Game(levels, screen)

    running = True
    while running:
        time = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            game.get_event(event)

        game.render()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
