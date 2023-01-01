import pygame
from level import Level
from menu import MainMenu


# основной игровой класс
# предназначен для связи между уровнями и менюшками
# ловит события и направляет их куда надо
class Game:
    def __init__(self, levels, screen):
        self.screen = screen
        self.levels = levels  # все уровни
        self.set_menu()

    # подгрузка звуковых эффектов для игры
    def setup_audio(self):
        self.main_menu_music = pygame.mixer.Sound("../sounds/main_menu.mp3")
        self.main_menu_music.set_volume(0.6)
        self.win_sound = pygame.mixer.Sound("../sounds/win.wav")
        self.played_win_sound = False

    # установить состояние на главное меню
    def set_menu(self):
        self.setup_audio()
        self.cur_level_index = 0  # текущий индекс уровня
        self.status = "menu"  # текущее состояние игры (уровень или меню)
        self.main_menu = MainMenu(self.screen)  # главное меню
        self.main_menu_music.play(-1)

    # создание и переключение уровней
    def set_level(self):
        level_is_last = self.cur_level_index == len(self.levels) - 1  # является ли уровень последним
        self.cur_level = Level(self.levels[self.cur_level_index], self.screen, level_is_last, self.set_menu)
        self.cur_level_index += 1
        self.status = "level"

    # отлавливаем эвенты от игрока
    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.status == "menu":
                self.main_menu.get_event(event)  # эвент идет в главное меню
            if self.status == "level" and (self.cur_level.viewing_final_menu or self.cur_level.paused):
                self.cur_level.level_menu.get_event(event)  # эвент идет в меню уровня

    # рендеринг игры в зависимости от текущего ее состояния
    def render(self):
        if self.status == "level":
            self.cur_level.render()
            # если уровень не последний, переключаем на следующий
            if self.cur_level.finished_level and not self.cur_level.is_last:
                self.set_level()
            elif self.cur_level.finished_level and not self.played_win_sound:
                self.win_sound.play()
                self.played_win_sound = True
        elif self.status == "menu":
            if self.main_menu.game_started:
                self.set_level()
                self.main_menu_music.stop()
