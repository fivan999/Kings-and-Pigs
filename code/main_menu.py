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


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.callbacks = []
        self.surfaces = []
        self.option_index = 0
        self.font = pygame.font.Font('../fonts/ARCADEPI.TTF', 20)
        self.level_started = False
        self.setup_menu()

    def setup_menu(self):
        logo_image = pygame.image.load("../graphics/menu/logo.png")
        self.logo = StaticMenuItem((SCREEN_SIZE[0] // 2 - logo_image.get_width() // 2, 10),
                                   logo_image)

        self.background = StaticMenuItem((0, 0), pygame.image.load("../graphics/menu/background.png"))

        self.create_button("PLAY", SCREEN_SIZE[1] // 2 - 50,
                           self.start_level)
        self.create_button("EXIT", SCREEN_SIZE[1] // 2, self.exit_game)

    def switch(self, direction):
        self.option_index = (self.option_index + direction) % len(self.surfaces)

    def create_button(self, text, y_pos, callback):
        button_surface = pygame.Surface((80, 40))
        button_surface.fill(pygame.Color("brown"))
        button = StaticMenuItem((SCREEN_SIZE[0] // 2 - button_surface.get_width() // 2, y_pos),
                                button_surface)
        button.set_text(text, self.font)
        self.surfaces.append(button)
        self.callbacks.append(callback)

    def start_level(self):
        self.level_started = True

    @staticmethod
    def exit_game():
        sys.exit()

    def get_event(self, event):
        if event.key == pygame.K_UP:
            self.switch(-1)
        if event.key == pygame.K_DOWN:
            self.switch(1)
        if event.key == pygame.K_RETURN:
            self.callbacks[self.option_index]()

    def render_buttons(self):
        for button_ind, button in enumerate(self.surfaces):
            button.draw(self.screen)
            if self.option_index == button_ind:
                pygame.draw.rect(self.screen, pygame.Color("#8d3607"),
                                 (button.rect.left, button.rect.top, button.image.get_width(),
                                  button.image.get_height()), width=5)

    def render(self):
        self.background.draw(self.screen)
        self.logo.draw(self.screen)

        self.render_buttons()
