from settings import *
from tilemap import collide_hit_rect
import pygame as pg
vec = pg.math.Vector2
from random import uniform


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(pg.sprite.Sprite):
    def __init__(self,game,x,y): #x and y are the spawn co-ordinates
        self._layer=PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.player_img
        self.angle = 90
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0,0)
        self.pos = vec(x,y)
        self.rot = 0 
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.resources=PLAYER_RESOURCES

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                for i in range(-2,3):
                    dir_temp=dir.rotate(i*20)   
                    Bullet(self.game, pos, dir_temp)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)
                s=self.game.gun_effect
                s.play()
    def collide_with_wall(self,sprite, group, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].name == "Exit":
                    self.game.score+=self.health*15
                    if self.game.hostage_count>=3:
                        self.game.flag=1
                    else:   
                        self.game.flag=0
                    
                    self.game.playing = False
                elif hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                elif hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].name == "Exit":
                    self.game.score+=self.health*15
                    if self.game.hostage_count>=3:
                        self.game.flag=1
                    else:
                        self.game.flag=0
                    
                    self.game.playing = False
                elif hits[0].rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                elif hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y


    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        self.collide_with_wall(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        self.collide_with_wall(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = (x,y)
        self.hit_rect.center = self.rect.center
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed=MOB_SPEED

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def getCollision(self):
#         rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
# #        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
# #        self.rect = self.image.get_rect()
# #        self.rect.center = self.pos
#         acc = vec(MOB_SPEED, 0).rotate(-rot)
#         acc += self.vel * -1
#         vel=self.vel + acc*self.game.dt;
#         vel=vel.normalize()
#         vel*=MOB_LOOKAHEAD
#         rect_temp=pg.Rect((0,0),(TILESIZE,TILESIZE))
#         rect_temp.center=self.pos+vel
#         pos_temp = vec(rect_temp.center[0],rect_temp.center[1])
#         for wall in self.game.walls:
#             wall_rect=wall.rect
#             wall_pos = vec(wall.rect.center[0],wall.rect.center[1])
#             if not rect_temp.colliderect(wall_rect):
#                 pass
#             else:
#                 dz = wall_pos - pos_temp
#                 if dz.x > 0:
#                     if dz.y > 0:
#                         checkpt = wall.rect.bottomleft
#                     else:
#                         checkpt = wall.rect.topleft
#                 else:
#                     if dz.y > 0:
#                         checkpt = wall.rect.bottomright
#                     else:
#                         checkpt = wall.rect.topright
#                 checkvec = vec(checkpt[0],checkpt[1])
#                 theta = dz.angle_to(checkvec)
#                 if theta > 0:
#                     norm = vec(checkpt[0],0)
#                 else:
#                     norm = vec(0,checkpt[1])
#                 norm = norm.normalize()
#                 target = vec(wall.rect.center[0],wall.rect.center[1])
#                 target = target - norm*320
#                 return target
        return None

    def seek_and_update(self,target):
        targetDist=target-self.pos
        if targetDist.length_squared()<DETECT_RADIUS**2:
            self.rot = (target - self.pos).angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center

    def update(self):
#        pass
        target=self.getCollision()
        if self.getCollision()==None:
            self.seek_and_update(self.game.player.pos)
        else:
            self.seek_and_update(target)
        if self.health <= 0:
            self.kill()
            self.game.score+=50

    def draw_health(self):
        if self.health > 60:
            self.col = GREEN
        elif self.health > 30:
            self.col = YELLOW
        else:
            self.col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, self.col, self.health_bar)

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
    def __init__(self,game,x,y,w,h,name):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x,y,w,h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.name = name
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.image=pg.transform.scale(self.image,(10,10))
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()


class staticMobs(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = (x,y)
        self.hit_rect.center = self.rect.center
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed=MOB_SPEED

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def getCollision(self):
#         rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
# #        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
# #        self.rect = self.image.get_rect()
# #        self.rect.center = self.pos
#         acc = vec(MOB_SPEED, 0).rotate(-rot)
#         acc += self.vel * -1
#         vel=self.vel + acc*self.game.dt;
#         vel=vel.normalize()
#         vel*=MOB_LOOKAHEAD
#         rect_temp=pg.Rect((0,0),(TILESIZE,TILESIZE))
#         rect_temp.center=self.pos+vel
#         pos_temp = vec(rect_temp.center[0],rect_temp.center[1])
#         for wall in self.game.walls:
#             wall_rect=wall.rect
#             wall_pos = vec(wall.rect.center[0],wall.rect.center[1])
#             if not rect_temp.colliderect(wall_rect):
#                 pass
#             else:
#                 dz = wall_pos - pos_temp
#                 if dz.x > 0:
#                     if dz.y > 0:
#                         checkpt = wall.rect.bottomleft
#                     else:
#                         checkpt = wall.rect.topleft
#                 else:
#                     if dz.y > 0:
#                         checkpt = wall.rect.bottomright
#                     else:
#                         checkpt = wall.rect.topright
#                 checkvec = vec(checkpt[0],checkpt[1])
#                 theta = dz.angle_to(checkvec)
#                 if theta > 0:
#                     norm = vec(checkpt[0],0)
#                 else:
#                     norm = vec(0,checkpt[1])
#                 norm = norm.normalize()
#                 target = vec(wall.rect.center[0],wall.rect.center[1])
#                 target = target - norm*320
#                 return target
        return None

    def seek_and_update(self,target):
        self.rot = (target - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        #self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def update(self):
#        pass
        target=self.getCollision()
        if self.getCollision()==None:
            self.seek_and_update(self.game.player.pos)
        else:
            self.seek_and_update(target)
        if self.health <= 0:
            self.kill()

    def draw_health(self):
        if self.health > 60:
            self.col = GREEN
        elif self.health > 30:
            self.col = YELLOW
        else:
            self.col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, self.col, self.health_bar)

class Hostage(pg.sprite.Sprite):

    def __init__(self,game,x,y,factor):
        self.groups = game.all_sprites,game.hostages
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = (x,y)
        self.hit_rect.center = self.rect.center
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed=MOB_SPEED
        self.time=START_TIME*factor

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def getCollision(self):
#         rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
# #        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
# #        self.rect = self.image.get_rect()
# #        self.rect.center = self.pos
#         acc = vec(MOB_SPEED, 0).rotate(-rot)
#         acc += self.vel * -1
#         vel=self.vel + acc*self.game.dt;
#         vel=vel.normalize()
#         vel*=MOB_LOOKAHEAD
#         rect_temp=pg.Rect((0,0),(TILESIZE,TILESIZE))
#         rect_temp.center=self.pos+vel
#         pos_temp = vec(rect_temp.center[0],rect_temp.center[1])
#         for wall in self.game.walls:
#             wall_rect=wall.rect
#             wall_pos = vec(wall.rect.center[0],wall.rect.center[1])
#             if not rect_temp.colliderect(wall_rect):
#                 pass
#             else:
#                 dz = wall_pos - pos_temp
#                 if dz.x > 0:
#                     if dz.y > 0:
#                         checkpt = wall.rect.bottomleft
#                     else:
#                         checkpt = wall.rect.topleft
#                 else:
#                     if dz.y > 0:
#                         checkpt = wall.rect.bottomright
#                     else:
#                         checkpt = wall.rect.topright
#                 checkvec = vec(checkpt[0],checkpt[1])
#                 theta = dz.angle_to(checkvec)
#                 if theta > 0:
#                     norm = vec(checkpt[0],0)
#                 else:
#                     norm = vec(0,checkpt[1])
#                 norm = norm.normalize()
#                 target = vec(wall.rect.center[0],wall.rect.center[1])
#                 target = target - norm*320
#                 return target
        return None

    def seek_and_update(self,target):
        self.rot = (target - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1
        self.vel += self.acc * self.game.dt
        #self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def update(self):
#        pass
        self.time=self.time-(self.game.dt)
        target=self.getCollision()
        if self.getCollision()==None:
            self.seek_and_update(self.game.player.pos)
        else:
            self.seek_and_update(target)
        if self.health <= 0:
            self.kill()
        if self.time<=0:
            self.kill()

    def draw_timer(self):
        if self.time > 0.66*START_TIME:
            self.col = GREEN
        elif self.time > 0.33*START_TIME:
            self.col = YELLOW
        else:
            self.col = RED
        width = int(self.rect.width * self.time /START_TIME)
        self.time_bar = pg.Rect(0, 0, width, 7)
        #print (self.time)
        pg.draw.rect(self.image, self.col, self.time_bar)

class Support(pg.sprite.Sprite):
    def __init__(self, game, x, y, angle):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = (x,y)
        self.hit_rect.center = self.rect.center
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed=PLAYER_SPEED*1.25
        self.offset = angle
        self.isKilled = False

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def getTarget(self):
        dir = vec(1,0).rotate(-self.game.player.rot)
        dir_temp = dir.rotate(self.offset)
        slot_pos = self.game.player.pos -dir*5 + dir_temp*32
        return (slot_pos.x, slot_pos.y)

    def seek_and_update(self,target):
        targetDist=target-self.pos
        if targetDist.length_squared()<DETECT_RADIUS**2:
            rot = (target - self.pos).angle_to(vec(1, 0))
            self.rot = self.game.player.rot
            self.image = pg.transform.rotate(self.game.player_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center

    def update(self):
#        pass
        target=self.getTarget()
        self.seek_and_update(target)
        if self.health <= 0:
            self.kill()

    def draw_health(self):
        if self.health > 60:
            self.col = GREEN
        elif self.health > 30:
            self.col = YELLOW
        else:
            self.col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, self.col, self.health_bar)

