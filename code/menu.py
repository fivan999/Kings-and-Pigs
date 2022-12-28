import sys
import pygame
from settings import SCREEN_SIZE


class StaticMenuItem(pygame.sprite.Sprite):
    def __init__(self, position, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)

    def set_text(self, text, font):
        text = font.render(text, True, "#ffffff")
        self.image.blit(text, (self.image.get_width() // 2 - text.get_width() // 2,
                               self.image.get_height() // 2 - text.get_height() // 2))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class BaseMenu:
    def __init__(self, background, screen):
        self.screen = screen
        self.background = background
        self.background.rect.x = SCREEN_SIZE[0] // 2 - self.background.image.get_width() // 2
        self.background.rect.y = SCREEN_SIZE[1] // 2 - self.background.image.get_height() // 2
        self.callbacks = list()
        self.callback_buttons = list()
        self.option_index = 0
        self.font = pygame.font.Font('../fonts/ARCADEPI.TTF', 20)

    def get_event(self, event):
        if event.key == pygame.K_UP:
            self.switch(-1)
        if event.key == pygame.K_DOWN:
            self.switch(1)
        if event.key == pygame.K_RETURN:
            self.callbacks[self.option_index]()

    def render_buttons(self):
        for button_ind, button in enumerate(self.callback_buttons):
            button.draw(self.screen)
            if self.option_index == button_ind:
                pygame.draw.rect(self.screen, pygame.Color("#8d3607"),
                                 (button.rect.left, button.rect.top, button.image.get_width(),
                                  button.image.get_height()), width=5)

    def create_button(self, text, y_pos, callback):
        button_surface = pygame.Surface((80, 40))
        button_surface.fill(pygame.Color("brown"))
        button = StaticMenuItem((SCREEN_SIZE[0] // 2 - button_surface.get_width() // 2, y_pos),
                                button_surface)
        button.set_text(text, self.font)
        self.callback_buttons.append(button)
        self.callbacks.append(callback)

    def switch(self, direction):
        self.option_index = (self.option_index + direction) % len(self.callback_buttons)
        self.render()

    def render(self):
        self.background.draw(self.screen)
        self.render_buttons()


class MainMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(StaticMenuItem((0, 0), pygame.image.load("../graphics/menu/background1.png").convert_alpha()),
                         screen)
        self.game_started = False
        self.setup_menu()
        self.render()

    def setup_menu(self):
        logo_image = pygame.image.load("../graphics/menu/logo.png")
        self.logo = StaticMenuItem((SCREEN_SIZE[0] // 2 - logo_image.get_width() // 2, self.background.rect.top + 75),
                                   logo_image)

        self.create_button("PLAY", SCREEN_SIZE[1] // 2 - 40,
                           self.start_game)
        self.create_button("EXIT", SCREEN_SIZE[1] // 2 + 10, self.exit_game)

    def start_game(self):
        self.game_started = True

    @staticmethod
    def exit_game():
        sys.exit()

    def render(self):
        super().render()
        self.logo.draw(self.screen)


class WinLoseMenu(BaseMenu):
    def __init__(self, screen, status, set_main_menu):
        super().__init__(StaticMenuItem((0, 0), pygame.image.load("../graphics/menu/background2.png").convert_alpha()),
                         screen)
        self.set_main_menu = set_main_menu
        self.setup_menu(status)
        self.render()

    def setup_menu(self, status):
        if status == "win":
            text = "YOU WIN!"
        else:
            text = "YOU LOSE!"
        self.status_surface = self.font.render(text, True, "#ffffff")
        self.create_button("MENU", SCREEN_SIZE[1] // 2 - 20,
                           self.main_menu)

    def main_menu(self):
        self.set_main_menu()

    def render(self):
        super().render()
        self.background.image.blit(self.status_surface, (self.background.image.get_width() // 2 -
                                                         self.status_surface.get_width() // 2, 40))
