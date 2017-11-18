#Heroes of Aleppo
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from bfs import *
vec = pg.math.Vector2

# HUD functions

import math


class Graph:
	def __init__(self):
		self.nodes = []
		self.edges = []
		self.obstacles = []

	def wall_avoided(self,i,j):
		node1 = self.nodes[i]
		node2 = self.nodes[j]
		for obstacle in self.obstacles:
			if self.distance_to_line(node1,node2,obstacle) < TILESIZE:
				return False
		return True

	def distance_to_line(self, p1, p2 , p3):
	    x_diff = p2.x - p1.x
	    y_diff = p2.y - p1.y
	    num = abs(y_diff*p3.x - x_diff*p3.y + p2.x*p1.y - p2.y*p1.x)
	    den = math.sqrt(y_diff**2 + x_diff**2)+0.01
	    return num / den

	def computeEdges(self):
		for i in range(len(self.nodes)):
			for j in range(i,len(self.nodes)):
				if self.wall_avoided(i,j) == True:
					self.edges.append(vec(self.nodes[i],self.nodes[j]))


def draw_player_health(surf, x, y, pct): #Adds the player health bar
	fontfile = pg.font.get_default_font()
	myfont = pg.font.Font(fontfile, 15)
	textsurface = myfont.render('HEALTH', False, (0, 0, 0))
	surf.blit(textsurface,(10,10))
	if pct < 0:
	    pct = 0
	BAR_LENGTH = 100
	BAR_HEIGHT = 20
	fill = pct * BAR_LENGTH
	outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
	if pct > 0.6:
	    col = GREEN
	elif pct > 0.3:
	    col = YELLOW
	else:
	    col = RED
	pg.draw.rect(surf, col, fill_rect)
	pg.draw.rect(surf, WHITE, outline_rect, 2)

def draw_player_resources(surf, x, y, pct):	#Adds the player health bar
	fontfile = pg.font.get_default_font()
	myfont = pg.font.Font(fontfile, 15)
	textsurface = myfont.render('RESOURCES', False, (0, 0, 0))
	surf.blit(textsurface,(10,60))
	if pct < 0:
	    pct = 0
	BAR_LENGTH = 100
	BAR_HEIGHT = 20
	fill = pct * BAR_LENGTH
	outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
	if pct > 0.6:
	    col = BLUE
	elif pct > 0.3:
	    col = YELLOW
	else:
	    col = RED
	pg.draw.rect(surf, col, fill_rect)
	pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
	def __init__(self):
		#initialize game window etc.
		pg.init()
		pg.mixer.init()
		self.screen = pg.display.set_mode((WIDTH,HEIGHT))
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		pg.key.set_repeat(200,100)
		self.load_data()
		self.graph = None
		self.stepsMap = {}

	def load_data(self):
		game_folder = path.dirname(__file__)
		map_folder = path.join(game_folder,"Tmx_Files")
		img_folder = path.join(game_folder,"img")
		self.map = TiledMap(path.join(map_folder, 'level1.tmx'))
		self.map_img = self.map.make_map()
		self.map_rect = self.map_img.get_rect()
		self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
		self.player_img = pg.image.load(path.join(img_folder,PLAYER_IMG)).convert_alpha()
		self.mob_img = pg.image.load(path.join(img_folder,MOB_IMG)).convert_alpha()
		self.player_img = pg.transform.scale(self.player_img, (TILESIZE,TILESIZE))
		self.mob_img = pg.transform.scale(self.mob_img, (TILESIZE,TILESIZE))

	def new(self):
		#start a new game
		self.all_sprites = pg.sprite.Group()
		self.walls = pg.sprite.Group()
		self.mobs = pg.sprite.Group()
		self.bullets = pg.sprite.Group()
		for tile_object in self.map.tmxdata.objects:
			if tile_object.name == "Player":
				self.player = Player(self,tile_object.x, tile_object.y)
			elif tile_object.name == "Wall":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height)
			elif tile_object.name == "Obstacle":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height)
			elif tile_object.name == "mob":
				Mob(self,tile_object.x,tile_object.y)

		self.camera = Camera(self.map.width,self.map.height)

	def run(self):
		#start a new game
		self.playing = True
		while self.playing:
			self.dt = self.clock.tick(FPS)/1000
			self.events()
			self.update()
			self.draw()

	def quit(self):
		self.playing = False
		pg.quit()
		sys.exit()

	def update(self):
		#Game loop update
		self.all_sprites.update()
		self.camera.update(self.player)
		hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
		for hit in hits:
			self.player.health-=MOB_DAMAGE
			hit.vel=vec(0,0)
			if self.player.health<=0:
				self.playing = False
		if hits:
			self.player.pos+=vec(MOB_KNOCKBACK,0).rotate(-hits[0].rot)
		hits=pg.sprite.groupcollide(self.mobs,self.bullets,False,True)
		for hit in hits:
			 hit.health-=BULLET_DAMAGE
			 hit.vel=vec(0,0)

	def events(self):
		#Game Loop events
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.quit()




	def draw(self):
		#Game Loop draw
		#self.screen.fill(BLACK)
		self.screen.blit(self.map_img,self.camera.apply_rect(self.map_rect))
		for sprite in self.all_sprites:
			if isinstance(sprite, Mob):
				sprite.draw_health()
			self.screen.blit(sprite.image, self.camera.apply(sprite))
		draw_player_health(self.screen, 10, 30, self.player.health/PLAYER_HEALTH)
		draw_player_resources(self.screen, 10, 80, self.player.resources/PLAYER_RESOURCES)        
		#FLIP
		pg.display.flip()

	def show_start_screen(self):
		# Show start screen
		pass

	def makeSSG(self):
		g = Graph()
		for tile_object in self.map.tmxdata.objects:
			if tile_object.name == "Subgoal":
				g.nodes.append (vec(tile_object.x, tile_object.y))
			if tile_object.name == "Wall":
				g.obstacles.append (vec(tile_object.x, tile_object.y))
			if tile_object.name == "Obstacle":
				g.obstacles.append (vec(tile_object.x, tile_object.y))
		g.computeEdges()
		return g

	def show_go_screen(self):
		# Show screen
		pass

g = Game()
g.show_start_screen()
g.graph = g.makeSSG()
while True:
	g.new()
	g.run()
	g.show_go_screen()

pg.quit()
