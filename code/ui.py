import pygame
from settings import SCREEN_SIZE


class UI:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # для отображения здоровья
        self.health_bar = pygame.image.load('../graphics/health and diamonds/bar.png').convert_alpha()
        self.heart = pygame.image.load('../graphics/health and diamonds/heart.png').convert_alpha()
        self.heart_pos = 56, 48

        # для отображения алмазов
        self.font = pygame.font.Font('../fonts/ARCADEPI.TTF', 26)
        self.numbers_bar = pygame.image.load('../graphics/health and diamonds/num_bar.png').convert_alpha()
        self.numbers_pos = SCREEN_SIZE[0] - 150, 20

        # для отображения текста
        self.text_time_remains = 0
        self.current_text = None

    # рендеринг сердечек
    def render_health(self, cur_health: int) -> None:
        self.screen.blit(self.health_bar, (20, 20))
        cur_r_shift = 0
        for _ in range(cur_health):
            self.screen.blit(self.heart, (self.heart_pos[0] + cur_r_shift, self.heart_pos[1]))
            cur_r_shift += 22

    # рендеринг алмазов
    def render_diamonds(self, cur_diamonds: int) -> None:
        x, y = self.numbers_pos
        self.screen.blit(self.numbers_bar, (x, y))
        diamond_cnt_surface = self.font.render(str(cur_diamonds), True, "#000000")
        x_pos = self.numbers_bar.get_width() // 2 - diamond_cnt_surface.get_width() // 2 + x + 10
        self.screen.blit(diamond_cnt_surface, (x_pos, y + 22))

    # обновление текста
    def set_current_text(self, text: str) -> None:
        self.text_time_remains = 5
        self.current_text = self.font.render(text, True, "#ffffff")

    # рендеринг текста
    def render_text(self) -> None:
        if self.text_time_remains > 0:  # если время отображения текста не закончилось
            x_pos = SCREEN_SIZE[0] // 2 - self.current_text.get_width() // 2
            self.screen.blit(self.current_text, (x_pos, 20))
        self.text_time_remains = max(0, self.text_time_remains - 0.01)
