import pygame
from settings import SCREEN_SIZE


class UI:
    def __init__(self, screen):
        self.screen = screen

        self.health_bar = pygame.image.load('../graphics/health and diamonds/bar.png').convert_alpha()
        self.heart = pygame.image.load('../graphics/health and diamonds/heart.png').convert_alpha()
        self.heart_pos = 28, 24

        self.font = pygame.font.Font('../fonts/ARCADEPI.TTF', 12)
        self.numbers_bar = pygame.image.load('../graphics/health and diamonds/num_bar.png').convert_alpha()
        self.numbers_pos = 425, 10

        self.text_time_remains = 0
        self.current_text = None

    def render_health(self, cur_health):
        self.screen.blit(self.health_bar, (10, 10))
        cur_r_shift = 0
        for _ in range(cur_health):
            self.screen.blit(self.heart, (self.heart_pos[0] + cur_r_shift, self.heart_pos[1]))
            cur_r_shift += 11

    def render_diamonds(self, cur_diamonds):
        x, y = self.numbers_pos
        self.screen.blit(self.numbers_bar, (x, y))
        diamond_cnt_surface = self.font.render(str(cur_diamonds), True, "#000000")
        x_pos = self.numbers_bar.get_width() // 2 - diamond_cnt_surface.get_width() // 2 + x + 5
        self.screen.blit(diamond_cnt_surface, (x_pos, y + 11))

    def set_current_text(self, text):
        self.text_time_remains = 5
        self.current_text = self.font.render(text, True, "#ffffff")

    def render_text(self):
        if self.text_time_remains > 0:
            x_pos = SCREEN_SIZE[0] // 2 - self.current_text.get_width() // 2
            self.screen.blit(self.current_text, (x_pos, 10))
        self.text_time_remains = max(0, self.text_time_remains - 0.01)
