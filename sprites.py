from settings import *
import pygame as pg
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self,game,x,y): #x and y are the spawn co-ordinates
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE,TILESIZE)) #create a player of TILESIZE*TILESIZE size
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y)

    def get_keys(self):
        self.vel =vec(0,0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN]:
            self.vel.y = PLAYER_SPEED
        if self.vel.x!=0 and self.vel.y!=0:
            self.vel.x = 0.7071*self.vel.x
            self.vel.y = 0.7071*self.vel.y


    def collide_with_walls(self,dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x <0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y <0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

    def update(self):
        self.get_keys()
        self.pos.x += self.vel.x * self.game.dt
        self.pos.y += self.vel.y * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

class Wall(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x*TILESIZE
        self.rect.y = y*TILESIZE

class Obstacle(pg.sprite.Sprite):
    def __init__(self,game,x,y,w,h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x,y,w,h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
