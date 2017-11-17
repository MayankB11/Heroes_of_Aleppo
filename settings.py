import pygame as pg
vec = pg.math.Vector2

TITLE = "Heroes of Aleppo"

WIDTH = 960
HEIGHT = 800
FPS = 60
TILESIZE = 32

#Player properties
#PLAYER_ACC = 0.5
#PLAYER_FRICTION = -0.12
PLAYER_SPEED = 200
PLAYER_ROT_SPEED = 120
PLAYER_IMG = 'stationary_right.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 18, 18)
BARREL_OFFSET = vec(10, 0)
PLAYER_HEALTH=100
PLAYER_RESOURCES=100
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
#Mob Properties

MOB_IMG = 'mob.png'
MOB_SPEED = 150
MOB_HIT_RECT = pg.Rect(0, 0, 18, 18)
MOB_HEALTH = 100
MOB_DAMAGE = 3
MOB_KNOCKBACK = 20
MOB_LOOKAHEAD=5/60
AVOID_RADIUS=50
DETECT_RADIUS=256
# Gun settings
BULLET_IMG = 'new_bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 200
BULLET_RATE = 150
KICKBACK = 200
GUN_SPREAD = 5
BULLET_DAMAGE = 10
# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1


# Hostage Values
START_TIME=30
HOSTAGE_RESCUE=10
HOSTAGE_COUNT=6

#Music

BG_MUSIC="bg.mp3"
GUN_SOUND="pistol.wav"
            