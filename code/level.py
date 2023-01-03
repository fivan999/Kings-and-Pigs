import pygame
from random import randint, choice
from settings import TILE_SIZE
from tile import Tile, StaticTile, Diamond, Box
from hero import Hero
from support import import_csv, cut_images, load_audio
from enemy import Pig
from camera import Camera
from ui import UI
from door import Door
from cannon import Cannon, CannonBall
from effects import EnemyDestroyEffect, BombExplosionEffect
from menu import WinLoseMenu, PauseMenu


# класс уровня
# тут происходит обработка всех событий от игрока, если находится в уровне
class Level:
    def __init__(self, level, screen, is_last, set_main_menu, cur_diamonds):
        self.screen = screen
        self.camera = Camera()  # камера, которая следит за игроком
        self.ui = UI(self.screen)  # отображение здоровья и алмазов
        self.total_pigs = 0  # количество свиней в уровне
        self.setup_level(level)
        self.setup_audio()
        # функция для установки главного меню, передается от класса Game при инициализации уровня
        self.set_main_menu = set_main_menu
        self.is_last = is_last  # последний уровень или нет
        self.viewing_final_menu = False  # отображается финальное меню или нет
        self.paused = False  # на паузе или нет
        self.level_menu = None  # текущее меню

        self.killed_pigs = 0  # количество убитых свиней
        self.cur_diamonds = cur_diamonds  # количество собранных алмазов
        self.colliding_door = False  # игрок рядом с выходом или нет
        self.finished_level = False  # закончил ли игрок прохождение уровня

    # подгрузка звуковых эффектов для уровня
    def setup_audio(self):
        self.diamond_sound = pygame.mixer.Sound("../sounds/diamond.wav")
        self.pig_die_sound = pygame.mixer.Sound("../sounds/pig/die.mp3")
        self.pig_say_sounds = load_audio("../sounds/pig/say/")
        self.cannon_shot_sound = pygame.mixer.Sound("../sounds/cannon_shot.wav")
        self.bomb_boom_sound = pygame.mixer.Sound("../sounds/bomb_boom_sound.wav")
        self.bomb_boom_sound.set_volume(0.5)

    # подгрузка всех спрайтов
    def setup_level(self, level):
        self.hero = None
        self.effects_sprites = pygame.sprite.Group()
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

    # возвращает все спрайты, нужно для фокусирования камеры
    def get_all_sprites(self):
        return self.terrain_sprites.sprites() + self.background_sprites.sprites() + \
            self.decoration_sprites.sprites() + self.box_sprites.sprites() + self.diamond_sprites.sprites() + \
            self.platform_sprites.sprites() + self.start_door_sprite.sprites() + \
            self.effects_sprites.sprites() + self.cannon_sprites.sprites() + self.cannon_balls_sprites.sprites() + \
            self.final_door_sprite.sprites() + self.enemy_block.sprites() + self.enemies_sprites.sprites()

    # нарезает спрайты из картинок
    @staticmethod
    def define_tile_type(graphics_type):
        tiles = list()

        if graphics_type == "terrain" or graphics_type == "background":
            tiles = cut_images("../graphics/terrain/terrain.png")
        elif graphics_type == "decorations":
            tiles = cut_images("../graphics/decorations/decorations.png")
        elif graphics_type == "default_platforms":
            tiles = cut_images("../graphics/decorations/default_platforms.png", y_size=30)

        return tiles

    # создание отдельной группы спрайтов
    def create_tile_group(self, csv_data, graphics_type):
        sprite_group = pygame.sprite.Group()
        tiles = self.define_tile_type(graphics_type)

        for row_ind, row in enumerate(csv_data):
            for col_ind, col in enumerate(row):
                if col == -1:
                    continue
                x, y = col_ind * TILE_SIZE, row_ind * TILE_SIZE  # позиция тайла
                if graphics_type == "hero":
                    tile = Hero((x, y))
                    self.hero = tile
                    return
                elif graphics_type == "box":  # коробка
                    tile = Box((x, y))
                    sprite_group.add(tile)
                elif graphics_type == "diamonds":  # алмаз
                    tile = Diamond((x, y))
                    sprite_group.add(tile)
                elif graphics_type == "start_door":  # стартовая дверь
                    tile = Door((x, y), False)
                    sprite_group.add(tile)
                elif graphics_type == "final_door":  # финальная дверь (выход с уровня)
                    tile = Door((x, y), True)
                    sprite_group.add(tile)
                elif graphics_type == "pigs":  # свинья (враг)
                    # если col == 1, то это именно враг, иначе это блок, ограничивающий движение врага
                    if col:
                        tile = Pig((x, y))
                        sprite_group.add(tile)
                        self.total_pigs += 1
                    else:
                        tile = Tile((x, y), tile_size=TILE_SIZE)
                        self.enemy_block.add(tile)
                elif graphics_type == "cannon":  # пушка
                    tile = Cannon((x, y))
                    sprite_group.add(tile)
                else:  # иначе это просто статичный блок, например terrain или default_platform
                    # они уже подгружены в функции define_tile_type
                    tile = tiles[col]
                    sprite_group.add(StaticTile((x, y), tile))

        return sprite_group

    # столкновение врагов с блоками-ограничителями движения
    def enemy_block_collision(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.enemy_block, dokill=False):
                enemy.reverse()  # разворачиваем врага

    # столкновение игрока с врагом или пушкой
    def enemy_cannon_hero_collision(self):
        hero = self.hero

        collide_sprites = self.enemies_sprites.sprites() + self.cannon_sprites.sprites()
        for sprite in collide_sprites:
            if sprite.rect.colliderect(hero.rect):
                sprite_type = type(sprite)
                # если игрок атакует, то разрушаем врага или пушку
                if hero.status == 'attack':
                    if sprite_type == Pig:
                        self.killed_pigs += 1
                        self.effects_sprites.add(EnemyDestroyEffect(sprite.rect.bottomleft))
                        self.pig_die_sound.play()
                    elif sprite_type == Cannon:
                        # эффект взрыва пушки
                        self.effects_sprites.add(BombExplosionEffect(sprite.rect.center))
                        self.bomb_boom_sound.play()
                    sprite.kill()
                elif hero.damage_time == 0:  # если игроку не наносили урон недавно
                    # проверяем, уничтожает ли игрок объект прыжком
                    if sprite.rect.top < hero.rect.bottom <= sprite.rect.bottom and hero.direction.y > 2:
                        hero.jump()
                        sprite.kill()
                        if sprite_type == Pig:
                            self.killed_pigs += 1
                            self.effects_sprites.add(EnemyDestroyEffect(sprite.rect.bottomleft))
                            self.pig_die_sound.play()
                        elif sprite_type == Cannon:
                            # опять эффект взрыва
                            self.effects_sprites.add(BombExplosionEffect(sprite.rect.center))
                            self.bomb_boom_sound.play()
                    elif sprite_type == Pig and sprite.rect.colliderect(hero.terrain_collision_rect):
                        hero.get_damage()

    # столкновение игрока и шара от пушки
    # или столкновение шара от пушки и стены
    def cannon_ball_hero_collision(self):
        if self.finished_level:  # если игрок дошел до конца уровня, больше не проверяем
            return

        hero = self.hero
        for ball in self.cannon_balls_sprites.sprites():
            collide_hero = hero.terrain_collision_rect.colliderect(ball) and hero.status != "die"
            collide_terrain = pygame.sprite.spritecollideany(ball, self.terrain_sprites)
            if collide_terrain or (collide_hero and not self.viewing_final_menu):
                if collide_hero:  # если он сталкивается с игроком, игрок получает урон
                    hero.get_damage()
                # ээфект взрыва шара
                self.effects_sprites.add(BombExplosionEffect(ball.rect.center))
                self.bomb_boom_sound.play()
                ball.kill()

    # игрок находится рядом с финальной дверью
    def door_collision(self):
        if pygame.sprite.spritecollide(self.hero, self.final_door_sprite, dokill=False):
            self.colliding_door = self.final_door_sprite.sprites()[0]
        else:
            self.colliding_door = False

    # игрок собирает алмазы
    def diamond_collision(self):
        hero = self.hero

        for diamond in self.diamond_sprites.sprites():
            if diamond.rect.colliderect(hero.rect):
                diamond.kill()
                self.cur_diamonds += 1
                self.diamond_sound.play()

    # проверка, стреляет ли пушка
    def check_cannon_shoot(self):
        for cannon in self.cannon_sprites.sprites():
            if int(cannon.image_index) == 2 and not cannon.shot:
                # если сейчас нужный нам индекс анимации, и пушка еще не стреляла на текущей анимации
                position = cannon.rect.topleft
                cannon.shot = True
                self.cannon_balls_sprites.add(CannonBall(position))
                self.cannon_shot_sound.play()

    # проверка, прошел ли игрок уровень
    def check_win(self):
        # если игрок рядом с дверью и дверь открыта
        self.finished_level = self.colliding_door and self.colliding_door.finished_animation
        if self.is_last and self.finished_level:  # если игрок прошел игру (последний уровень завершен)
            self.level_menu = WinLoseMenu(self.screen, "win", self.set_main_menu, self.cur_diamonds)
            self.viewing_final_menu = True

    # если игрок умер
    def check_lose(self):
        if self.hero.health == 0 and self.hero.died:
            self.level_menu = WinLoseMenu(self.screen, "lose", self.set_main_menu, self.cur_diamonds)
            self.viewing_final_menu = True
            self.update_ui()

    # фокусировка камеры
    def focus_camera(self):
        self.camera.update(self.hero)
        for sprite in self.get_all_sprites():
            self.camera.apply(sprite)

    # хрюканье свиньи
    def make_pig_sound(self):
        chance = 70
        cnt_enemies = self.total_pigs - self.killed_pigs
        if cnt_enemies and randint(1, chance // cnt_enemies) == 3:
            choice(self.pig_say_sounds).play()

    # движение игрока по горизонтали
    def horizontal_move(self):
        hero = self.hero
        tiles_groups = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        hero.terrain_collision_rect.x += hero.direction.x * hero.speed

        for tile in tiles_groups:
            if tile.rect.colliderect(hero.terrain_collision_rect):
                if hero.direction.x < 0:  # если игрок столкнулся с чем то, пока шел влево
                    hero.terrain_collision_rect.left = tile.rect.right
                    hero.on_left = True
                elif hero.direction.x > 0:  # пока шел вправо
                    hero.terrain_collision_rect.right = tile.rect.left
                    hero.on_right = True

    # движение игрока по вертикали
    def vertical_move(self):
        hero = self.hero
        tiles_groups = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        hero.use_gravity()

        for tile in tiles_groups:
            if tile.rect.colliderect(hero.terrain_collision_rect):
                if hero.direction.y > 0:  # столкнулся пока падал
                    hero.terrain_collision_rect.bottom = tile.rect.top
                    hero.on_ground = True
                elif hero.direction.y < 0:  # столкнулся пока был в прыжке
                    hero.terrain_collision_rect.top = tile.rect.bottom
                    hero.on_ground = False
                hero.direction.y = 0

        if hero.on_ground and hero.direction.y < 0 or hero.direction.y > 1:
            hero.on_ground = False

    # отлавливаем эвенты с зажатой клавишей
    def get_event(self):
        if self.finished_level or self.viewing_final_menu or self.paused or \
                (self.colliding_door and self.colliding_door.animation_started):
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
        elif keys[pygame.K_f] and self.hero.on_ground and self.hero.status == "idle":  # атака
            self.hero.status = "attack"
        if keys[pygame.K_UP] and self.colliding_door:  # завершение уровня
            if self.total_pigs == self.killed_pigs:
                self.colliding_door.start_animation()
            else:
                self.ui.set_current_text("kill all pigs to finish level")
        if keys[pygame.K_ESCAPE] and not self.paused:  # пауза
            self.set_pause()

    # ставим игру на паузу
    def set_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.level_menu = PauseMenu(self.screen, self.set_pause, self.set_main_menu)

    # обновляем игрока
    def update_hero(self):
        self.check_lose()
        self.check_win()
        self.focus_camera()
        self.hero.update()
        self.hero.draw(self.screen)
        self.cannon_ball_hero_collision()
        if self.hero.status != 'attack':
            self.vertical_move()
        if not self.viewing_final_menu and not self.hero.status == "die":
            self.horizontal_move()
            self.enemy_cannon_hero_collision()
            self.get_event()
            self.diamond_collision()
            self.door_collision()

    # обновляем отображение здоровья и алмазов
    def update_ui(self):
        self.ui.render_health(self.hero.health)
        self.ui.render_text()
        self.ui.render_diamonds(self.cur_diamonds)

    # обновление и отрисовка всех спрайтов
    def render_level_events(self):
        self.screen.fill((63, 56, 81))
        self.background_sprites.update()
        self.background_sprites.draw(self.screen)

        self.decoration_sprites.update()
        self.decoration_sprites.draw(self.screen)

        self.terrain_sprites.update()
        self.terrain_sprites.draw(self.screen)

        self.diamond_sprites.update()
        self.diamond_sprites.draw(self.screen)

        self.platform_sprites.update()
        self.platform_sprites.draw(self.screen)

        self.start_door_sprite.update()
        self.start_door_sprite.draw(self.screen)

        self.final_door_sprite.update()
        self.final_door_sprite.draw(self.screen)

        self.enemies_sprites.update()
        self.enemy_block_collision()
        self.enemies_sprites.draw(self.screen)
        self.enemy_block.update()
        self.make_pig_sound()

        self.box_sprites.update()
        self.box_sprites.draw(self.screen)

        self.effects_sprites.update()
        self.effects_sprites.draw(self.screen)

        self.cannon_sprites.update()
        self.cannon_sprites.draw(self.screen)
        self.check_cannon_shoot()

        self.cannon_balls_sprites.update()
        self.cannon_balls_sprites.draw(self.screen)

        self.update_hero()
        self.update_ui()

    # рендеринг уроавня в зависимости от состояния
    def render(self):
        if not self.paused:
            self.render_level_events()
            if self.viewing_final_menu:
                self.level_menu.render()
