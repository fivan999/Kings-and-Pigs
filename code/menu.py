import sys
import pygame
from settings import SCREEN_SIZE
from typing import Callable
from support import make_path


class MenuBackground(pygame.sprite.Sprite):
    def __init__(self, position: tuple, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.rect = self.surface.get_rect(topleft=position)

    # отрисовка
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.surface, self.rect)


class MenuOptionItem(pygame.sprite.Sprite):
    def __init__(self, y_position: int, text: str):
        super().__init__()
        self.text = text
        self.y_position = y_position

    # рендерим текст
    def render(self, screen: pygame.Surface, is_active: bool, font: pygame.font.Font) -> None:
        if is_active:
            color = pygame.Color("brown")
        else:
            color = pygame.Color("white")
        text_surface = font.render(self.text, True, color)
        position = screen.get_width() // 2 - text_surface.get_width() // 2, self.y_position
        screen.blit(text_surface, position)


class BaseMenu:
    def __init__(self, background: MenuBackground, screen: pygame.Surface):
        self.screen = screen
        self.background = background  # фон

        # зададим позицию фона
        self.background.rect.x = SCREEN_SIZE[0] // 2 - self.background.surface.get_width() // 2
        self.background.rect.y = SCREEN_SIZE[1] // 2 - self.background.surface.get_height() // 2

        self.callbacks = list()  # функции для ответа на эвенты
        self.options = list()  # варианты выбора
        self.option_index = 0  # индекс текущей кнопки
        self.big_font = pygame.font.Font(make_path("../fonts/ARCADEPI.TTF"), 40)
        self.small_font = pygame.font.Font(make_path("../fonts/ARCADEPI.TTF"), 28)

    # ловим евенты от менюшки
    def get_event(self, event: pygame.event) -> None:
        if event.key == pygame.K_UP:
            self.switch(-1)
        if event.key == pygame.K_DOWN:
            self.switch(1)
        if event.key == pygame.K_RETURN:
            self.callbacks[self.option_index]()

    # отрисовка кнопки
    def render_buttons(self) -> None:
        for option_ind, option in enumerate(self.options):
            option.render(self.screen, self.option_index == option_ind, self.big_font)

    # создание кнопки
    def create_option(self, text: str, y_position: int, callback) -> None:
        option = MenuOptionItem(y_position, text)
        self.options.append(option)
        self.callbacks.append(callback)

    # переключение текущей кнопки
    def switch(self, direction: int) -> None:
        self.option_index = (self.option_index + direction) % len(self.options)
        self.render()

    # отрисовка меню
    def render(self) -> None:
        self.background.draw(self.screen)
        self.render_buttons()


# главное меню, при вхоже в игру
class MainMenu(BaseMenu):
    menu_image = make_path("../graphics/menu/menu_images/main_menu.png")
    logo_image = make_path("../graphics/menu/logos/big_logo.png")

    def __init__(self, screen: pygame.Surface):
        super().__init__(MenuBackground((0, 0), pygame.image.load(MainMenu.menu_image).convert_alpha()),
                         screen)
        self.game_started = False  # началась ли игра
        self.setup_menu()
        self.render()

    # создание кнопок и надписей
    def setup_menu(self) -> None:
        logo_image = pygame.image.load(MainMenu.logo_image).convert_alpha()
        self.logo = MenuBackground((SCREEN_SIZE[0] // 2 - logo_image.get_width() // 2, self.background.rect.top + 170),
                                   logo_image)  # логотип игры

        self.create_option("PLAY", SCREEN_SIZE[1] // 2 - 40, self.start_game)  # надпись "играть"
        self.create_option("EXIT", SCREEN_SIZE[1] // 2 + 40, self.exit_game)  # надпись "выйти"

    # начать игру
    def start_game(self) -> None:
        self.game_started = True

    # выйти из игры
    @staticmethod
    def exit_game() -> None:
        sys.exit()

    def render(self) -> None:
        super().render()
        self.logo.draw(self.screen)


class WinLoseMenu(BaseMenu):
    win_menu_image = make_path("../graphics/menu/menu_images/win_menu.png")
    lose_menu_image = make_path("../graphics/menu/menu_images/lose_menu.png")

    def __init__(self, screen: pygame.Surface, status: str, set_main_menu: Callable, total_diamonds: int):
        if status == "win":
            menu_image = pygame.image.load(WinLoseMenu.win_menu_image)
        else:
            menu_image = pygame.image.load(WinLoseMenu.lose_menu_image)
        super().__init__(MenuBackground((0, 0), menu_image.convert_alpha()),
                         screen)
        self.total_diamonds = total_diamonds
        self.set_main_menu = set_main_menu  # функция для перехода в главное меню
        self.setup_menu(status)
        self.render()

    # создание кнопок и надписей
    def setup_menu(self, status: str) -> None:
        if status == "win":
            text = "YOU WIN!"
        else:
            text = "YOU LOSE!"
        self.status_text_surface = self.big_font.render(text, True, "#ffffff")  # текст (победа или проигрыш)
        self.create_option("MENU", SCREEN_SIZE[1] // 2 - 10,
                           self.set_main_menu)  # надпись "в меню"
        self.total_diamonds_text_surface = self.small_font.render(f"total diamonds: {self.total_diamonds}",
                                                                  True, "#ffffff")

    def render(self) -> None:
        self.background.surface.blit(self.status_text_surface, (self.background.surface.get_width() // 2 -
                                                                self.status_text_surface.get_width() // 2, 80))
        self.background.surface.blit(self.total_diamonds_text_surface,
                                     (self.background.surface.get_width() // 2 -
                                      self.total_diamonds_text_surface.get_width() // 2, 140))
        super().render()


class PauseMenu(BaseMenu):
    menu_image = make_path("../graphics/menu/menu_images/pause_menu.png")

    def __init__(self, screen: pygame.Surface, set_pause: Callable, set_main_menu: Callable):
        super().__init__(MenuBackground((0, 0), pygame.image.load(PauseMenu.menu_image).convert_alpha()),
                         screen)
        self.set_pause = set_pause  # функция для ставки игры на паузу
        self.set_main_menu = set_main_menu  # функция для перехода в главное меню
        self.setup_menu()
        self.render()

    # создание кнопок и надписей
    def setup_menu(self) -> None:
        self.pause_text_surface = self.big_font.render("PAUSE", True, "#ffffff")  # надпись "пауза"
        self.create_option("CONTINUE", SCREEN_SIZE[1] // 2 - 40,
                           self.set_pause)  # надпись "продолжить"
        self.create_option("MENU", SCREEN_SIZE[1] // 2 + 40,
                           self.set_main_menu)  # надпись "в меню"

    def render(self) -> None:
        self.background.surface.blit(self.pause_text_surface, (self.background.surface.get_width() // 2 -
                                                               self.pause_text_surface.get_width() // 2, 80))
        super().render()
