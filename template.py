import pygame as pg 
import random
from settings import *

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption(TITLE)
clock = pg.time.Clock()


all_sprites = pg.sprite.Group()

running = True 
while running:
  clock.tick(FPS)

    #Process input
  for event in pg.event.get():
    if event.type == pg.QUIT:
      running = False 


    #Update
  all_sprites.update()


    #Render
  screen.fill(BLACK)
  all_sprites.draw(screen)
    #FLIP
  pg.display.flip()

pg.quit()