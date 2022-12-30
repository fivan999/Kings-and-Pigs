import sys
import pygame
from settings import SCREEN_SIZE


# класс для создания статичных штук в менюшке
# например, кнопка или фон
class StaticMenuItem(pygame.sprite.Sprite):
    def __init__(self, position, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)

    # зададим текст
    def set_text(self, text, font):
        text = font.render(text, True, "#ffffff")
        self.image.blit(text, (self.image.get_width() // 2 - text.get_width() // 2,
                               self.image.get_height() // 2 - text.get_height() // 2))

    # отрисовка
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class BaseMenu:
    def __init__(self, background, screen):
        self.screen = screen
        self.background = background  # фон

        # зададим позицию фона
        self.background.rect.x = SCREEN_SIZE[0] // 2 - self.background.image.get_width() // 2
        self.background.rect.y = SCREEN_SIZE[1] // 2 - self.background.image.get_height() // 2

        self.callbacks = list()  # функции для ответа на эвенты
        self.callback_buttons = list()  # кнопки
        self.option_index = 0  # индекс текущей кнопки
        self.font = pygame.font.Font('../fonts/ARCADEPI.TTF', 20)

    # ловим евенты от менюшки
    def get_event(self, event):
        if event.key == pygame.K_UP:
            self.switch(-1)
        if event.key == pygame.K_DOWN:
            self.switch(1)
        if event.key == pygame.K_RETURN:
            self.callbacks[self.option_index]()

    # отрисовка кнопки
    def render_buttons(self):
        for button_ind, button in enumerate(self.callback_buttons):
            button.draw(self.screen)
            if self.option_index == button_ind:
                # если мы сфокусировались на кнопке, нарисуем квадратик вокруг нее
                pygame.draw.rect(self.screen, pygame.Color("#8d3607"),
                                 (button.rect.left - 5, button.rect.top - 5, button.image.get_width() + 10,
                                  button.image.get_height() + 10), width=5)

    # создание кнопки
    def create_button(self, text, y_pos, callback):
        button_surface = pygame.Surface((80, 40))
        button_surface.fill(pygame.Color("brown"))
        button = StaticMenuItem((SCREEN_SIZE[0] // 2 - button_surface.get_width() // 2, y_pos),
                                button_surface)
        button.set_text(text, self.font)
        self.callback_buttons.append(button)
        self.callbacks.append(callback)

    # переключение текущей кнопки
    def switch(self, direction):
        self.option_index = (self.option_index + direction) % len(self.callback_buttons)
        self.render()

    # отрисовка меню
    def render(self):
        self.background.draw(self.screen)
        self.render_buttons()


# главное меню, при вхоже в игру
class MainMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(StaticMenuItem((0, 0), pygame.image.load("../graphics/menu/background1.png").convert_alpha()),
                         screen)
        self.game_started = False  # началась ли игра
        self.setup_menu()
        self.render()

    # создание кнопок и надписей
    def setup_menu(self):
        logo_image = pygame.image.load("../graphics/menu/logo.png")
        self.logo = StaticMenuItem((SCREEN_SIZE[0] // 2 - logo_image.get_width() // 2, self.background.rect.top + 75),
                                   logo_image)  # логотип игры

        self.create_button("PLAY", SCREEN_SIZE[1] // 2 - 40,
                           self.start_game)  # кнопка "играть"
        self.create_button("EXIT", SCREEN_SIZE[1] // 2 + 10, self.exit_game)  # кнопка "выйти"

    # начать игру
    def start_game(self):
        self.game_started = True

    # выйти из игры
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
        self.set_main_menu = set_main_menu  # функция для перехода в главное меню
        self.setup_menu(status)
        self.render()

    # создание кнопок и надписей
    def setup_menu(self, status):
        if status == "win":
            text = "YOU WIN!"
        else:
            text = "YOU LOSE!"
        self.status_text_surface = self.font.render(text, True, "#ffffff")  # текст (победа или проигрыш)
        self.create_button("MENU", SCREEN_SIZE[1] // 2 - 20,
                           self.set_main_menu)  # кнопка "в меню"

    def render(self):
        self.background.image.blit(self.status_text_surface, (self.background.image.get_width() // 2 -
                                                              self.status_text_surface.get_width() // 2, 40))
        super().render()


class PauseMenu(BaseMenu):
    def __init__(self, screen, set_pause, set_main_menu):
        super().__init__(StaticMenuItem((0, 0), pygame.image.load("../graphics/menu/background2.png").convert_alpha()),
                         screen)
        self.set_pause = set_pause  # функция для ставки игры на паузу
        self.set_main_menu = set_main_menu  # функция для перехода в главное меню
        self.setup_menu()
        self.render()

    # создание кнопок и надписей
    def setup_menu(self):
        self.pause_text_surface = self.font.render("PAUSE", True, "#ffffff")  # надпись "пауза"
        self.create_button("GO", SCREEN_SIZE[1] // 2 - 30,
                           self.set_pause)  # кнопка "продолжить"
        self.create_button("MENU", SCREEN_SIZE[1] // 2 + 20,
                           self.set_main_menu)  # кнопка "в меню"

    def render(self):
        self.background.image.blit(self.pause_text_surface, (self.background.image.get_width() // 2 -
                                                             self.pause_text_surface.get_width() // 2, 40))
        super().render()
