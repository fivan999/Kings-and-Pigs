import pygame
from random import randint, choice
from settings import TILE_SIZE
from tiles import Tile, StaticTile
from stuff_tiles import Diamond, Box
from hero import Hero
from support import import_csv, cut_images
from enemy import Pig
from camera import Camera
from ui import UI
from door import Door
from cannon import Cannon, CannonBall
from effects import EnemyDestroyEffect, BombExplosionEffect
from menu import WinLoseMenu, PauseMenu
from sounds import (DIAMOND_SOUND, PIG_DIE_SOUND, PIG_SAY_SOUND,
                    CANNON_SHOT_SOUND, BOMB_BOOM_SOUND, LOSE_SOUND)
from typing import Callable


# класс уровня
# тут происходит обработка всех событий от игрока, если находится в уровне
class Level:
    def __init__(self, level: dict, screen: pygame.Surface, set_main_menu: Callable, cur_diamonds: Callable):
        self.screen = screen
        self.ui = UI(self.screen)  # отображение здоровья и алмазов
        self.total_pigs = 0  # количество свиней в уровне
        self.setup_level(level)
        self.camera = Camera(self.hero, level["size"])  # камера, которая следит за игроком

        # функция для установки главного меню, передается от класса Game при инициализации уровня
        self.set_main_menu = set_main_menu
        self.is_last = level["is_last"]  # последний уровень или нет
        self.viewing_final_menu = False  # отображается финальное меню или нет
        self.paused = False  # на паузе или нет
        self.level_menu = None  # текущее меню

        self.cnt_killed_pigs = 0  # количество убитых свиней
        self.cur_diamonds = cur_diamonds  # количество собранных алмазов
        self.colliding_door = False  # игрок рядом с выходом или нет
        self.finished_level = False  # финальная дверь закончила открываться

    # загрузка всех спрайтов
    def setup_level(self, level: dict) -> None:
        self.hero = None
        self.create_tile_group(import_csv(level["hero"]), "hero")
        self.terrain_sprites = self.create_tile_group(import_csv(level["terrain"]),
                                                      "terrain")
        self.background_sprites = self.create_tile_group(import_csv(level["background"]),
                                                         "background")
        self.decoration_sprites = self.create_tile_group(import_csv(level["decorations"]),
                                                         "decorations")
        self.box_sprites = self.create_tile_group(import_csv(level["box"]), "box")
        self.diamond_sprites = self.create_tile_group(import_csv(level["diamonds"]),
                                                      "diamonds")
        self.platform_sprites = self.create_tile_group(import_csv(level["default_platforms"]),
                                                       "default_platforms")
        self.start_door_sprite = self.create_tile_group(import_csv(level["start_door"]),
                                                        "start_door")
        self.final_door_sprite = self.create_tile_group(import_csv(level["final_door"]),
                                                        "final_door")
        self.enemy_block = pygame.sprite.Group()
        self.enemies_sprites = self.create_tile_group(import_csv(level["pigs"]),
                                                      "pigs")
        self.cannon_balls_sprites = pygame.sprite.Group()
        self.cannon_sprites = self.create_tile_group(import_csv(level["cannon"]),
                                                     "cannon")
        self.effects_sprites = pygame.sprite.Group()

    # возвращает все спрайты, нужно для фокусирования камеры
    def get_all_sprites(self) -> list[pygame.sprite.Sprite]:
        return self.terrain_sprites.sprites() + self.background_sprites.sprites() + \
            self.decoration_sprites.sprites() + self.box_sprites.sprites() + self.diamond_sprites.sprites() + \
            self.platform_sprites.sprites() + self.start_door_sprite.sprites() + \
            self.effects_sprites.sprites() + self.cannon_sprites.sprites() + self.cannon_balls_sprites.sprites() + \
            self.final_door_sprite.sprites() + self.enemy_block.sprites() + self.enemies_sprites.sprites()

    # нарезает спрайты из картинок
    @staticmethod
    def define_tile_type(graphics_type) -> list[pygame.Surface]:
        tiles = list()

        if graphics_type == "terrain" or graphics_type == "background":
            tiles = cut_images("../graphics/terrain/terrain.png")
        elif graphics_type == "decorations":
            tiles = cut_images("../graphics/decorations/decorations.png")
        elif graphics_type == "default_platforms":
            tiles = cut_images("../graphics/decorations/default_platforms.png", y_size=30)

        return tiles

    # создание отдельной группы спрайтов
    def create_tile_group(self, csv_data: list, graphics_type: str) -> pygame.sprite.Group:
        sprite_group = pygame.sprite.Group()
        tiles = self.define_tile_type(graphics_type)

        for row_ind, row in enumerate(csv_data):
            for col_ind, col in enumerate(row):
                if col == -1:
                    continue
                x, y = col_ind * TILE_SIZE, row_ind * TILE_SIZE  # позиция клетки
                if graphics_type == "hero":
                    self.hero = Hero((x, y))
                elif graphics_type == "box":  # коробка
                    sprite_group.add(Box((x, y)))
                elif graphics_type == "diamonds":  # алмаз
                    sprite_group.add(Diamond((x, y)))
                elif graphics_type == "start_door":  # стартовая дверь
                    sprite_group.add(Door((x, y), False))
                elif graphics_type == "final_door":  # финальная дверь (выход с уровня)
                    sprite_group.add(Door((x, y), True))
                elif graphics_type == "pigs":  # свинья (враг)
                    # если col == 1, то это именно враг, иначе это блок, ограничивающий движение врага
                    if col:
                        sprite_group.add(Pig((x, y)))
                        self.total_pigs += 1
                    else:
                        self.enemy_block.add(Tile((x, y), tile_size=TILE_SIZE))
                elif graphics_type == "cannon":  # пушка
                    sprite_group.add(Cannon((x, y)))
                else:  # иначе это просто статичный блок, например terrain или default_platform
                    # они уже подгружены в функции define_tile_type
                    sprite_group.add(StaticTile((x, y), tiles[col]))

        return sprite_group

    # уничтожаем свинью со спрайтом pig
    def kill_pig(self, pig: pygame.sprite.Sprite) -> None:
        self.cnt_killed_pigs += 1
        self.effects_sprites.add(EnemyDestroyEffect(pig.rect.bottomleft))
        PIG_DIE_SOUND.play()
        pig.kill()

    # уничтожаем пушку или пушечный шар
    def kill_cannon_or_ball(self, sprite: pygame.sprite.Sprite) -> None:
        self.effects_sprites.add(BombExplosionEffect(sprite.rect.center))
        BOMB_BOOM_SOUND.play()
        sprite.kill()

    # прыгает ли игрок на спрайт
    def check_jump_destruction(self, sprite: pygame.sprite.Sprite) -> None:
        return sprite.rect.top < self.hero.terrain_collision_rect.bottom <= sprite.rect.bottom \
               and self.hero.direction.y > 4

    # столкновение врагов с блоками-ограничителями движения
    def enemy_block_collision(self) -> None:
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.enemy_block, dokill=False):
                enemy.reverse()  # разворачиваем врага

    # столкновение игрока со свиньей
    def pig_hero_collision(self) -> None:
        hero = self.hero

        for pig in self.enemies_sprites.sprites():
            if hero.status == "attack" and hero.attack_rect.colliderect(pig.rect):
                self.kill_pig(pig)
            elif hero.terrain_collision_rect.colliderect(pig.rect):
                if self.check_jump_destruction(pig):
                    self.kill_pig(pig)
                    hero.jump()
                elif hero.damage_time == 0:
                    hero.get_damage()

    # столкновение игрока с пушкой
    def cannon_hero_collision(self) -> None:
        hero = self.hero

        for cannon in self.cannon_sprites.sprites():
            if hero.status == "attack" and hero.attack_rect.colliderect(cannon.rect):
                self.kill_cannon_or_ball(cannon)
            elif hero.terrain_collision_rect.colliderect(cannon.rect):
                if self.check_jump_destruction(cannon):
                    self.kill_cannon_or_ball(cannon)
                    hero.jump()

    # столкновение игрока и шара от пушки
    # или столкновение шара от пушки и стены
    def cannon_ball_hero_collision(self) -> None:
        if self.finished_level:  # если игрок дошел до конца уровня, больше не проверяем
            return

        hero = self.hero
        for ball in self.cannon_balls_sprites.sprites():
            collide_hero = hero.terrain_collision_rect.colliderect(ball) and hero.status != "die"
            collide_terrain = pygame.sprite.spritecollideany(ball, self.terrain_sprites)
            if collide_terrain or (collide_hero and not self.viewing_final_menu):
                if collide_hero:  # если он сталкивается с игроком, игрок получает урон
                    hero.get_damage()
                # эффект взрыва шара
                self.kill_cannon_or_ball(ball)

    # игрок находится рядом с финальной дверью
    def door_collision(self) -> None:
        if pygame.sprite.spritecollide(self.hero, self.final_door_sprite, dokill=False):
            self.colliding_door = self.final_door_sprite.sprites()[0]
        else:
            self.colliding_door = False

    # игрок собирает алмазы
    def diamond_collision(self) -> None:
        hero = self.hero

        for diamond in self.diamond_sprites.sprites():
            if diamond.rect.colliderect(hero.rect):
                diamond.kill()
                self.cur_diamonds += 1
                DIAMOND_SOUND.play()

    # проверка, стреляет ли пушка
    def check_cannon_shoot(self) -> None:
        for cannon in self.cannon_sprites.sprites():
            if int(cannon.image_index) == 2 and not cannon.shot:
                # если сейчас нужный нам индекс анимации, и пушка еще не стреляла на текущей анимации
                position = cannon.rect.topleft
                cannon.shot = True
                self.cannon_balls_sprites.add(CannonBall(position))
                CANNON_SHOT_SOUND.play()

    # проверка, прошел ли игрок уровень
    def check_win(self) -> None:
        # если игрок рядом с дверью и дверь открыта
        self.finished_level = self.colliding_door and self.colliding_door.finished_animation
        # если игрок прошел игру (последний уровень завершен)
        if self.is_last and self.finished_level and not self.viewing_final_menu:
            self.level_menu = WinLoseMenu(self.screen, "win", self.set_main_menu, self.cur_diamonds)
            self.viewing_final_menu = True

    # если игрок умер
    def check_lose(self) -> None:
        if self.hero.health == 0 and self.hero.died and not self.viewing_final_menu:
            self.level_menu = WinLoseMenu(self.screen, "lose", self.set_main_menu, self.cur_diamonds)
            self.viewing_final_menu = True
            self.update_ui()
            LOSE_SOUND.play()

    # фокусировка камеры
    def draw_by_camera(self, group: pygame.sprite.Group) -> None:
        for sprite in group.sprites():
            self.screen.blit(sprite.image, self.camera.apply(sprite))

    # хрюканье свиньи
    def make_pig_sound(self) -> None:
        chance = 70
        cnt_enemies = self.total_pigs - self.cnt_killed_pigs
        if cnt_enemies and randint(1, chance // cnt_enemies) == 3:
            choice(PIG_SAY_SOUND).play()

    # движение игрока по горизонтали
    def horizontal_move(self) -> None:
        hero = self.hero
        tiles_groups = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        delta_x = hero.direction.x * hero.speed
        if hero.status == "attack":
            delta_x *= 0.5
        hero.terrain_collision_rect.x += delta_x

        for tile in tiles_groups:
            if tile.rect.colliderect(hero.terrain_collision_rect):
                if hero.direction.x < 0:  # если игрок столкнулся с чем то, пока шел влево
                    hero.terrain_collision_rect.left = tile.rect.right
                    hero.on_left = True
                elif hero.direction.x > 0:  # пока шел вправо
                    hero.terrain_collision_rect.right = tile.rect.left
                    hero.on_right = True

    # движение игрока по вертикали
    def vertical_move(self) -> None:
        hero = self.hero
        tiles_groups = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        hero.use_gravity()

        for tile in tiles_groups:
            if tile.rect.colliderect(hero.terrain_collision_rect):
                if hero.direction.y > 0:  # столкнулся пока падал
                    hero.terrain_collision_rect.bottom = tile.rect.top
                    hero.on_ground = True
                elif hero.direction.y < 0:  # столкнулся, пока был в прыжке
                    hero.terrain_collision_rect.top = tile.rect.bottom
                    hero.on_ground = False
                hero.direction.y = 0

        if hero.on_ground and hero.direction.y < 0 or hero.direction.y > 1:
            hero.on_ground = False

    # состояния, когда игрок уже не может контролировать героя
    def check_level_finished(self) -> bool:
        return self.finished_level or self.viewing_final_menu or self.paused or \
               (self.colliding_door and self.colliding_door.animation_started) or \
               self.hero.status == "die"

    # отлавливаем нажатия клавиш
    def get_key_press_event(self, event: pygame.event) -> None:
        if self.check_level_finished():
            return

        key = event.key
        if key == pygame.K_UP and self.colliding_door:  # завершение уровня
            if self.total_pigs == self.cnt_killed_pigs:
                self.colliding_door.start_animation()
            else:
                self.ui.set_current_text("kill all pigs to finish level")
        elif key == pygame.K_f:  # атака
            self.hero.attack()
        if key == pygame.K_ESCAPE and not self.paused:  # пауза
            self.set_pause()

    # отлавливаем события с зажатой клавишей
    def get_key_hold_event(self) -> None:
        if self.check_level_finished():
            return

        keys = pygame.key.get_pressed()

        # движение по горизонтали
        if keys[pygame.K_RIGHT]:
            self.hero.direction.x = 1
            self.hero.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.hero.direction.x = -1
            self.hero.facing_right = False
        else:
            self.hero.direction.x = 0

        if keys[pygame.K_SPACE] and self.hero.on_ground:  # прыжок
            self.hero.jump()

    # ставим игру на паузу
    def set_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.level_menu = PauseMenu(self.screen, self.set_pause, self.set_main_menu)

    # обновляем игрока
    def update_hero(self) -> None:
        self.check_lose()
        self.check_win()
        self.hero.update()
        self.screen.blit(self.hero.image, self.camera.apply(self.hero))
        self.cannon_ball_hero_collision()
        self.vertical_move()
        if not self.viewing_final_menu and not self.hero.status == "die":
            self.horizontal_move()
            self.pig_hero_collision()
            self.cannon_hero_collision()
            self.get_key_hold_event()
            self.diamond_collision()
            self.door_collision()

    # обновляем отображение здоровья и алмазов
    def update_ui(self) -> None:
        self.ui.render_health(self.hero.health)
        self.ui.render_text()
        self.ui.render_diamonds(self.cur_diamonds)

    # обновление и отрисовка всех спрайтов
    def render_level_events(self) -> None:
        self.screen.fill((63, 56, 81))
        self.camera.update()

        self.enemy_block.update()
        self.draw_by_camera(self.enemy_block)

        self.background_sprites.update()
        self.draw_by_camera(self.background_sprites)

        self.decoration_sprites.update()
        self.draw_by_camera(self.decoration_sprites)

        self.terrain_sprites.update()
        self.draw_by_camera(self.terrain_sprites)

        self.diamond_sprites.update()
        self.draw_by_camera(self.diamond_sprites)

        self.platform_sprites.update()
        self.draw_by_camera(self.platform_sprites)

        self.start_door_sprite.update()
        self.draw_by_camera(self.start_door_sprite)

        self.final_door_sprite.update()
        self.draw_by_camera(self.final_door_sprite)

        self.enemies_sprites.update()
        self.enemy_block_collision()
        self.draw_by_camera(self.enemies_sprites)
        self.make_pig_sound()

        self.box_sprites.update()
        self.draw_by_camera(self.box_sprites)

        self.effects_sprites.update()
        self.draw_by_camera(self.effects_sprites)

        self.cannon_sprites.update()
        self.draw_by_camera(self.cannon_sprites)

        self.check_cannon_shoot()
        self.cannon_balls_sprites.update()
        self.draw_by_camera(self.cannon_balls_sprites)

        self.update_hero()
        self.update_ui()

    # рендеринг уровня в зависимости от состояния
    def render(self) -> None:
        if not self.paused:
            self.render_level_events()
            if self.viewing_final_menu:
                self.level_menu.render()
