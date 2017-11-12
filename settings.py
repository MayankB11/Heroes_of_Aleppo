import pygame as pg
TITLE = "Heroes of Aleppo"

WIDTH = 960
HEIGHT = 800
FPS = 60
TILESIZE = 32

#Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_SPEED = 200
PLAYER_ROT_SPEED = 120
PLAYER_IMG = 'stationary_right.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

#Mob Properties

MOB_IMG = 'mob.png'
MOB_SPEED = 150
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)