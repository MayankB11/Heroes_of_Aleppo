from settings import *
import pygame as pg
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False)
        if hits:
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.rect.width
            if sprite.vel.x <0:
                sprite.pos.x = hits[0].rect.right
            sprite.vel.x = 0
            sprite.rect.x = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False)
        if hits:
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.rect.height
            if sprite.vel.y <0:
                sprite.pos.y = hits[0].rect.bottom
            sprite.vel.y = 0
            sprite.rect.y = sprite.pos.y

class Player(pg.sprite.Sprite):
    def __init__(self,game,x,y): #x and y are the spawn co-ordinates
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.player_img
        self.angle = 90
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.vel = vec(0,0)
        self.pos = vec(x,y)

    def get_keys(self):
        self.vel =vec(0,0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.vel.x = -PLAYER_SPEED
            self.image = pg.transform.rotate(self.image,180-self.angle)
            self.angle = 180
        if keys[pg.K_RIGHT]:
            self.vel.x = PLAYER_SPEED
            self.image = pg.transform.rotate(self.image,-self.angle)
            self.angle = 0
        if keys[pg.K_UP]:
            self.vel.y = -PLAYER_SPEED
            self.image = pg.transform.rotate(self.image,90-self.angle)
            self.angle = 90
        if keys[pg.K_DOWN]:
            self.vel.y = PLAYER_SPEED
            self.image = pg.transform.rotate(self.image,-90-self.angle)
            self.angle = -90
        if self.vel.x!=0 and self.vel.y!=0:
            self.vel = 0.7071*self.vel
            #TO DO make angle in multiples of 45

    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.y = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

class Mob(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.vel = vec(0,0)
        self.angle = 90
        self.pos = vec(x,y)

    def update(self):
        self.rot = (self.game.player.pos-self.pos).angle_to(vec(1,0))
        self.rect =  self.image.get_rect()
        self.image = pg.transform.rotate(self.game.mob_img,self.rot-self.angle)
        self.pos += self.vel * self.game.dt
        self.rect.x = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.y = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

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
