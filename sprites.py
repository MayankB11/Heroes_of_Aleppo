from settings import *
from tilemap import collide_hit_rect
import pygame as pg
import math
vec = pg.math.Vector2
from random import uniform
from rrt import *

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
                Bullet(self.game, pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
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
        self.path = None
        self.pathNode = -1
        self.playerNode = None

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def should_replan(self):
        if (self.path == None or self.playerNode == None):
            return True
        nearestDistPlayer = math.inf
        nearestNodePlayer = self.game.graph.nodes[0]        
        for node in self.game.graph.nodes:
            if math.sqrt((node.x-self.game.player.pos.x)**2+(node.y-self.game.player.pos.y)**2) < nearestDistPlayer:
                nearestDistPlayer = math.sqrt((node.x-self.pos.x)**2+(node.y-self.pos.y)**2)
                nearestNodePlayer = node
        if self.playerNode != nearestNodePlayer :
            return True
        if self.pathNode + 1 == len(self.path):
            return True
        return False

    def getCollision(self):
        rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        acc = vec(MOB_SPEED, 0).rotate(-rot)
        acc += self.vel * -1
        vel=self.vel
        if self.vel.x == 0 and self.vel.y == 0:
            return None
        vel=vel.normalize()
        vel*=MOB_LOOKAHEAD
        rect_temp=pg.Rect((0,0),(TILESIZE,TILESIZE))
        rect_temp.center=self.pos+vel
        pos_temp = vec(rect_temp.center[0],rect_temp.center[1])
        for wall in self.game.walls:
            wall_rect=wall.rect
            wall_pos = vec(wall.rect.center[0],wall.rect.center[1])
            if not rect_temp.colliderect(wall_rect):
                pass
            else:
                dz = wall_pos - pos_temp
                if dz.x > 0:
                    if dz.y > 0:
                        checkpt = wall.rect.bottomleft
                    else:
                        checkpt = wall.rect.topleft
                else:
                    if dz.y > 0:
                        checkpt = wall.rect.bottomright
                    else:
                        checkpt = wall.rect.topright
                checkvec = vec(checkpt[0],checkpt[1])
                theta = dz.angle_to(checkvec)
                if theta > 0:
                    norm = vec(checkpt[0],0)
                else:
                    norm = vec(0,checkpt[1])
                norm = norm.normalize()
                target = vec(wall.rect.center[0],wall.rect.center[1])
                target = target - norm*320
                return target
        return None

    def getPath(self):
        nearestDistMob = math.inf
        nearestNodeMob = self.game.graph.nodes[0]
        nearestDistPlayer = math.inf
        nearestNodePlayer = self.game.graph.nodes[0]
        tempMob = 0 
        tempPlayer = 0 
        for node in self.game.graph.nodes:
            if math.sqrt((node.x-self.pos.x)**2+(node.y-self.pos.y)**2) < nearestDistMob:
                nearestDistMob = math.sqrt((node.x-self.pos.x)**2+(node.y-self.pos.y)**2)
                nearestNodeMob = node
                tempMob = self.game.graph.nodes.index(node)
            if math.sqrt((node.x-self.game.player.pos.x)**2+(node.y-self.game.player.pos.y)**2) < nearestDistPlayer:
                nearestDistPlayer = math.sqrt((node.x-self.pos.x)**2+(node.y-self.pos.y)**2)
                nearestNodePlayer = node
                tempPlayer = self.game.graph.nodes.index(node)
        if self.should_replan() == False:
            if math.sqrt((self.path[self.pathNode].x-self.pos.x)**2+(self.path[self.pathNode].y-self.pos.y)**2) < 1.2*TILESIZE:
                self.pathNode +=1
            return self.path[self.pathNode]

        dist = [math.inf]*(len(self.game.graph.nodes))
        parent = [None]*(len(self.game.graph.nodes))
        dist[tempMob] = 0
        nodes = self.game.graph.nodes


        while dist[tempPlayer] == math.inf :
            for i in range(len(nodes)):
                if dist[i] == math.inf :
                    continue
                for j in range(len(nodes)):
                    if dist[i]+ math.sqrt((nodes[i].x-nodes[j].x)**2+(nodes[i].y-nodes[j].y)**2) > dist[j] or i==j:
                        continue
                    if vec(nodes[i],nodes[j]) in self.game.graph.edges : 
                        dist[j] = dist[i]+ math.sqrt((nodes[i].x - nodes[j].x)**2+(nodes[i].y-nodes[j].y)**2) 
                        parent[j] = i
                    if vec(nodes[j],nodes[i]) in self.game.graph.edges :
                        dist[j] = dist[i]+ math.sqrt((nodes[i].x-nodes[j].x)**2+(nodes[i].y-nodes[j].y)**2) 
                        parent[j] = i
        if tempPlayer == tempMob :
            return self.game.player.pos

        temp_node = nodes[tempPlayer] 
        self.playerNode = temp_node
        temp_path = []
        temp_path.append(tempPlayer)              
        while tempMob != tempPlayer:
            tempMob = nodes.index(temp_node)
            for i in range(len(nodes)):
                if parent[i] == tempMob:
                    temp_path.append(i)
                    temp_node = nodes[i]
                    tempPlayer = i
        self.pathNode = 0
        self.path = []
        for i in range(len(temp_path)-1,-1,-1):
            self.path.append(nodes[temp_path[i]])
        return self.path[self.pathNode]



    def seek_and_update(self,target):
        #if target == self.game.player.pos and math.sqrt((self.pos.x-self.game.player.pos.x)**2+(self.pos.y-self.game.player.pos.y)**2) < SEEK_RADIUS:
         #   target = rrt(self.pos,self.game.player.pos,self.game.walls).point
        self.rot = (target- self.pos).angle_to(vec(1, 0))
        self.rot += 0.01
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
        if math.sqrt((self.pos.x-self.game.player.pos.x)**2+(self.pos.y-self.game.player.pos.y)**2) < SEEK_RADIUS:
            target = 5*(self.game.player.pos-self.pos)+self.pos
            self.seek_and_update(target)
        elif math.sqrt((self.pos.x-self.game.player.pos.x)**2+(self.pos.y-self.game.player.pos.y)**2) < DETECT_RADIUS :
            target = self.getPath()
            target = vec(target.x,target.y)
            self.seek_and_update(target)
        if self.health <= 0:
            self.kill()

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)

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