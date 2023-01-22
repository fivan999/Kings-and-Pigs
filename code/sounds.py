import pygame.mixer
from pygame.mixer import Sound
from support import load_audio, make_path


pygame.mixer.init()

# все звуки для игры
DIAMOND_SOUND = Sound(make_path("../sounds/diamond.wav"))
PIG_DIE_SOUND = Sound(make_path("../sounds/pig/die.mp3"))
PIG_SAY_SOUND = load_audio(make_path("../sounds/pig/say/"))
CANNON_SHOT_SOUND = Sound(make_path("../sounds/cannon_shot.wav"))
BOMB_BOOM_SOUND = Sound(make_path("../sounds/bomb_boom_sound.wav"))
BOMB_BOOM_SOUND.set_volume(0.5)
JUMP_SOUND = Sound(make_path("../sounds/hero/jump.mp3"))
HERO_DAMAGE_SOUND = Sound(make_path("../sounds/hero/get_damage.mp3"))
ATTACK_SOUND = Sound(make_path("../sounds/hero/attack.mp3"))
MAIN_MENU_MUSIC = Sound(make_path("../sounds/main_menu.mp3"))
WIN_SOUND = Sound(make_path("../sounds/win.wav"))
LOSE_SOUND = Sound(make_path("../sounds/lose.mp3"))
