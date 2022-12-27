from tile import *
from hero import Hero
from support import *
from enemy import *
from camera import Camera
from ui import UI
from door import Door
from cannon import Cannon, CannonBall
from effects import EnemyDestroyEffect, BombExplosionEffect


class Level:
    def __init__(self, level, screen):
        self.screen = screen
        self.camera = Camera()
        self.ui = UI(self.screen)
        self.total_pigs = 0
        self.setup_level(level)

        self.cur_x = None
        self.killed_pigs = 0
        self.cur_diamonds = 0
        self.colliding_door = False
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
        self.cannon_balls_sprites = pygame.sprite.Group()
        self.cannon_sprites = self.create_tile_group(import_csv(level["cannon"]),
                                                     "cannon")

    def get_all_sprites(self):
        return self.hero_group.sprites() + self.terrain_sprites.sprites() + self.background_sprites.sprites() + \
               self.decoration_sprites.sprites() + self.box_sprites.sprites() + self.diamond_sprites.sprites() + \
               self.platform_sprites.sprites() + self.backgroud_door_sprite.sprites() + \
               self.effects_sprites.sprites() + self.cannon_sprites.sprites() + self.cannon_balls_sprites.sprites() + \
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
                    tile = Diamond((x, y))
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
                        self.total_pigs += 1
                    else:
                        tile = Tile((x, y), tile_size=TILE_SIZE)
                        self.enemy_block.add(tile)
                elif graphics_type == "cannon":
                    tile = Cannon((x, y))
                    sprite_group.add(tile)
                else:
                    tile = tiles[col]
                    sprite_group.add(StaticTile((x, y), tile))

        return sprite_group

    def enemy_block_collision(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.enemy_block, dokill=False):
                enemy.reverse()

    def enemy_cannon_hero_collision(self):
        hero = self.hero

        collide_sprites = self.enemies_sprites.sprites() + self.cannon_sprites.sprites()
        for sprite in collide_sprites:
            if sprite.rect.colliderect(hero):
                if hero.status == 'attack':
                    if type(sprite) == Pig:
                        self.killed_pigs += 1
                    else:
                        self.effects_sprites.add(BombExplosionEffect(sprite.rect.center))
                    sprite.kill()
                elif hero.damage_time == 0:
                    if sprite.rect.top < hero.rect.bottom <= sprite.rect.centery and hero.direction.y > 0:
                        hero.jump()
                        if type(sprite) == Pig:
                            self.killed_pigs += 1
                        else:
                            self.effects_sprites.add(BombExplosionEffect(sprite.rect.center))
                        sprite.kill()
                    elif type(sprite) == Pig:
                        hero.get_damage()

    def cannon_ball_hero_collision(self):
        if self.finished_level:
            return

        hero = self.hero
        for ball in self.cannon_balls_sprites.sprites():
            collide_hero = hero.rect.colliderect(ball)
            collide_terrain = pygame.sprite.spritecollideany(ball, self.terrain_sprites)
            if collide_terrain or collide_hero:
                if collide_hero:
                    hero.get_damage()
                self.effects_sprites.add(BombExplosionEffect(ball.rect.center))
                ball.kill()

    def door_collision(self):
        if pygame.sprite.spritecollide(self.hero, self.active_door_sprite, dokill=False):
            self.colliding_door = self.active_door_sprite.sprites()[0]
        else:
            self.colliding_door = False

    def diamond_collision(self):
        hero = self.hero

        for diamond in self.diamond_sprites.sprites():
            if diamond.rect.colliderect(hero):
                diamond.kill()
                self.cur_diamonds += 1

    def check_cannon_shoot(self):
        for cannon in self.cannon_sprites.sprites():
            if int(cannon.image_index) == 2 and not cannon.shot:
                position = cannon.rect.topleft
                cannon.shot = True
                self.cannon_balls_sprites.add(CannonBall(position))

    def check_finished_level(self):
        self.finished_level = self.colliding_door and \
                              self.colliding_door.finished_animation

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

    def get_events(self):
        if self.finished_level:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.hero.direction.x = 1
            self.hero.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.hero.direction.x = -1
            self.hero.facing_right = False
        else:
            self.hero.direction.x = 0

        if keys[pygame.K_SPACE] and self.hero.on_ground:
            self.hero.jump()

        if keys[pygame.K_e] and self.hero.on_ground:
            self.hero.status = "attack"

        if keys[pygame.K_q] and self.colliding_door:
            if self.total_pigs == self.killed_pigs:
                self.colliding_door.start_animation()
            else:
                self.ui.set_current_text("kill all pigs to finish level")

    def update_hero(self):
        self.get_events()
        self.hero.update()
        self.enemy_cannon_hero_collision()
        self.cannon_ball_hero_collision()
        if self.hero.status != 'attack':
            self.horizontal_move()
            self.vertical_move()
        self.diamond_collision()
        self.door_collision()
        self.scroll()
        self.hero_group.draw(self.screen)
        self.check_finished_level()

    def update_ui(self):
        self.ui.render_health(self.hero.health)
        self.ui.render_text()
        self.ui.render_diamonds(self.cur_diamonds)

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

        self.cannon_sprites.update()
        self.cannon_sprites.draw(self.screen)
        self.check_cannon_shoot()

        self.cannon_balls_sprites.update()
        self.cannon_balls_sprites.draw(self.screen)

        self.box_sprites.update()
        self.box_sprites.draw(self.screen)

        self.update_ui()

        self.update_hero()

        self.effects_sprites.update()
        self.effects_sprites.draw(self.screen)
