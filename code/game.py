from level import Level


class Game:
    def __init__(self, levels, screen):
        self.screen = screen
        self.levels = levels
        self.cur_level_index = 0
        self.status = "level"
        self.cur_level = Level(self.levels[self.cur_level_index], self.screen)

    def set_next_level(self):
        if self.cur_level_index == len(self.levels) - 1:
            self.show_final_window()
            return

        self.cur_level_index += 1
        self.cur_level = Level(self.levels[self.cur_level_index], self.screen)

    def show_final_window(self):
        self.cur_level.ui.set_current_text("You WON!")

    def render(self):
        if self.status == "level":
            self.cur_level.render()
            if self.cur_level.finished_level:
                self.set_next_level()
