import sys
import pygame
from settings import SCREEN_SIZE
from game import Game
from game_data import levels


# базовая инициализация pygame
def main():
    pygame.init()
    pygame.display.set_caption("Kings and Pigs")

    screen = pygame.display.set_mode(SCREEN_SIZE)

    # надпись загрузки
    font = pygame.font.Font("../fonts/ARCADEPI.TTF", 20)
    loading_text = font.render("loading...", True, "#ffffff")
    screen.blit(loading_text, (SCREEN_SIZE[0] // 2 - loading_text.get_width() // 2,
                               SCREEN_SIZE[1] // 2 - loading_text.get_height() // 2))
    pygame.display.flip()

    clock = pygame.time.Clock()
    game = Game(levels, screen)  # экземпляр класса самой игры

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            game.get_event(event)  # ловим события через класс игры

        game.render()  # рендер игры
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
