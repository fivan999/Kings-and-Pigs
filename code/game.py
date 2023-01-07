import pygame
from level import Level
from menu import MainMenu
from sounds import MAIN_MENU_MUSIC, WIN_SOUND


# основной игровой класс
# предназначен для связи между уровнями и меню
# ловит события и направляет их куда надо
class Game:
    def __init__(self, levels, screen):
        self.screen = screen
        self.levels = levels  # все уровни
        self.set_menu()
        self.played_win_sound = False  # был ли звук победы

    # установить состояние на главное меню
    def set_menu(self):
        self.cur_level = None
        self.cur_diamonds = 0  # текущее количество алмазов (для результата)
        self.cur_level_index = 0  # текущий индекс уровня
        self.status = "menu"  # текущее состояние игры (уровень или меню)
        self.main_menu = MainMenu(self.screen)  # главное меню
        MAIN_MENU_MUSIC.play(-1)

    # создание и переключение уровней
    def set_level(self):
        if self.cur_level:
            self.cur_diamonds = self.cur_level.cur_diamonds
        self.cur_level = Level(self.levels[self.cur_level_index], self.screen,
                               self.set_menu, self.cur_diamonds)
        self.cur_level_index += 1
        self.status = "level"

    # отлавливаем события от игрока
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.status == "menu":
                self.main_menu.get_event(event)  # событие идет в главное меню
            if self.status == "level" and (self.cur_level.viewing_final_menu or self.cur_level.paused):
                self.cur_level.level_menu.get_event(event)  # событие идет в меню уровня
            elif self.status == "level":
                self.cur_level.get_key_press_event(event)

    # рендеринг игры в зависимости от текущего ее состояния
    def render(self):
        if self.status == "level":
            self.cur_level.render()
            # если уровень не последний, переключаем на следующий
            if self.cur_level.finished_level and not self.cur_level.is_last:
                self.set_level()
            elif self.cur_level.finished_level and not self.played_win_sound:
                WIN_SOUND.play()
                self.played_win_sound = True
        elif self.status == "menu":
            if self.main_menu.game_started:
                self.set_level()
                MAIN_MENU_MUSIC.stop()
