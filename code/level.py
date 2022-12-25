import pygame
from tile import *
from settings import TILE_SIZE
from hero import Hero
from settings import SCREEN_SIZE
from support import *
from enemy import *
from camera import Camera
from ui import UI
from door import Door
from effects import EnemyDestroyEffect


class Level:
    def __init__(self, level, screen):
        self.screen = screen
        self.camera = Camera()
        self.setup_level(level)
        self.cur_x = None
        self.ui = UI(self.screen)
        self.cur_diamonds = 0
        self.finished_level = False

    def setup_level(self, level):
        self.hero = None
        self.hero_group = pygame.sprite.GroupSingle()
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
        self.backgroud_door_sprite = self.create_tile_group(import_csv(level["background_door"]),
                                                            "background_door")
        self.active_door_sprite = self.create_tile_group(import_csv(level["door"]),
                                                         "door")
        self.enemy_block = pygame.sprite.Group()
        self.enemies_sprites = self.create_tile_group(import_csv(level["pigs"]),
                                                      "pigs")

    def get_all_sprites(self):
        return self.hero_group.sprites() + self.terrain_sprites.sprites() + self.background_sprites.sprites() + \
               self.decoration_sprites.sprites() + self.box_sprites.sprites() + self.diamond_sprites.sprites() + \
               self.platform_sprites.sprites() + self.backgroud_door_sprite.sprites() + self.effects_sprites.sprites() + \
               self.active_door_sprite.sprites() + self.enemy_block.sprites() + self.enemies_sprites.sprites()

    @staticmethod
    def define_tile_type(graphics_type):
        tiles = list()

        if graphics_type == "terrain" or graphics_type == "background":
            tiles = import_graphics("../graphics/terrain/terrain.png")
        elif graphics_type == "decorations":
            tiles = import_graphics("../graphics/decorations/decorations.png")
        elif graphics_type == "default_platforms":
            tiles = import_graphics("../graphics/decorations/default_platforms.png", y_size=15)

        return tiles

    def create_tile_group(self, csv_data, graphics_type):
        sprite_group = pygame.sprite.Group()
        tiles = self.define_tile_type(graphics_type)

        for row_ind, row in enumerate(csv_data):
            for col_ind, col in enumerate(row):
                if col == -1:
                    continue
                x, y = col_ind * TILE_SIZE, row_ind * TILE_SIZE
                if graphics_type == "hero":
                    tile = Hero((x, y))
                    self.hero = tile
                    self.hero_group.add(tile)
                    return
                elif graphics_type == "box":
                    tile = Box((x, y))
                    sprite_group.add(tile)
                elif graphics_type == "diamonds":
                    tile = Diamond((x, y), "../graphics/stuff/animate_diamonds/")
                    sprite_group.add(tile)
                elif graphics_type == "background_door":
                    tile = Door((x, y), False)
                    sprite_group.add(tile)
                elif graphics_type == "door":
                    tile = Door((x, y), True)
                    sprite_group.add(tile)
                elif graphics_type == "pigs":
                    if col:
                        tile = Pig((x, y))
                        sprite_group.add(tile)
                    else:
                        tile = Tile((x, y), tile_size=TILE_SIZE)
                        self.enemy_block.add(tile)
                else:
                    tile = tiles[col]
                    sprite_group.add(StaticTile((x, y), tile))

        return sprite_group

    def enemy_block_collision(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.enemy_block, dokill=False):
                enemy.reverse()

    def enemy_hero_collision(self):
        hero = self.hero

        for enemy in self.enemies_sprites.sprites():
            if enemy.rect.colliderect(hero):
                if hero.status == 'attack':
                    enemy.kill()
                elif hero.damage_time == 0:
                    if enemy.rect.top < hero.rect.bottom < enemy.rect.centery and hero.direction.y > 0:
                        enemy.kill()
                        # self.effects_sprites.add(EnemyDestroyEffect(enemy.rect.topleft))
                        hero.jump()
                    else:
                        hero.get_damage()

    def door_collision(self):
        if pygame.sprite.spritecollide(self.hero, self.active_door_sprite, dokill=False):
            self.hero.colliding_door = self.active_door_sprite
        else:
            self.hero.colliding_door = None

    def diamond_collision(self):
        hero = self.hero

        for diamond in self.diamond_sprites.sprites():
            if diamond.rect.colliderect(hero):
                diamond.kill()
                self.cur_diamonds += 1

    def check_end_level(self):
        if self.hero.finished_level:
            self.finished_level = True

    def scroll(self):
        self.camera.update(self.hero)
        for sprite in self.get_all_sprites():
            self.camera.apply(sprite)

    def horizontal_move(self):
        hero = self.hero
        hero.rect.x += hero.direction.x * hero.speed

        tiles_group = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        for tile in tiles_group:
            if tile.rect.colliderect(hero.rect):
                if hero.direction.x < 0:
                    hero.rect.left = tile.rect.right
                    hero.on_left = True
                    self.cur_x = hero.rect.left
                elif hero.direction.x > 0:
                    hero.rect.right = tile.rect.left
                    hero.on_right = True
                    self.cur_x = hero.rect.right

        if hero.on_left and (hero.rect.left < self.cur_x or hero.direction.x >= 0):
            hero.on_left = False
        if hero.on_right and (hero.rect.right > self.cur_x or hero.direction.x <= 0):
            hero.on_right = False

    def vertical_move(self):
        hero = self.hero
        hero.use_gravity()

        tiles_group = self.terrain_sprites.sprites() + self.box_sprites.sprites() + self.platform_sprites.sprites()
        for tile in tiles_group:
            if tile.rect.colliderect(hero.rect):
                if hero.direction.y > 0:
                    hero.rect.bottom = tile.rect.top
                    hero.on_ground = True
                    hero.on_ceiling = False
                elif hero.direction.y < 0:
                    hero.rect.top = tile.rect.bottom
                    hero.on_ceiling = True
                    hero.on_ground = False
                hero.direction.y = 0

        if hero.on_ground and hero.direction.y < 0 or hero.direction.y > 1:
            hero.on_ground = False
        if hero.on_ceiling and hero.direction.y > 0:
            hero.on_ceiling = False

    def update_hero(self):
        self.hero.update()
        self.enemy_hero_collision()
        if self.hero.status != 'attack':
            self.horizontal_move()
            self.vertical_move()
        self.diamond_collision()
        self.door_collision()
        self.check_end_level()
        self.scroll()
        self.hero_group.draw(self.screen)

    def render(self):
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

        self.backgroud_door_sprite.update()
        self.backgroud_door_sprite.draw(self.screen)

        self.active_door_sprite.update()
        self.active_door_sprite.draw(self.screen)

        self.enemies_sprites.update()
        self.enemy_block_collision()
        self.enemies_sprites.draw(self.screen)

        self.enemy_block.update()

        self.box_sprites.update()
        self.box_sprites.draw(self.screen)

        self.ui.render_health(self.hero.health)
        self.ui.render_diamonds(self.cur_diamonds)

        self.update_hero()

        self.effects_sprites.update()
        self.effects_sprites.draw(self.screen)
