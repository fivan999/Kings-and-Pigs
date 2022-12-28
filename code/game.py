import pygame
from level import Level
from menu import MainMenu


class Game:
    def __init__(self, levels, screen):
        self.screen = screen
        self.levels = levels
        self.set_menu()

    def set_menu(self):
        self.cur_level_index = 0
        self.status = "menu"
        self.main_menu = MainMenu(self.screen)

    def set_level(self):
        if self.cur_level_index == len(self.levels) - 1:
            level_num = "last"
        else:
            level_num = "notlast"
        self.cur_level = Level(self.levels[self.cur_level_index], self.screen, level_num, self.set_menu)
        self.cur_level_index += 1
        self.status = "level"

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.status == "menu":
                self.main_menu.get_event(event)
            if self.status == "level" and self.cur_level.viewing_menu:
                self.cur_level.get_menu_event(event)

    def render(self):
        if self.status == "level":
            self.cur_level.render()
            if self.cur_level.finished_level and self.cur_level.level_num != "last":
                self.set_level()
        elif self.status == "menu":
            if self.main_menu.game_started:
                self.set_level()
