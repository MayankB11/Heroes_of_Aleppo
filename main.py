#Heroes of Aleppo
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *

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

	def load_data(self):
		game_folder = path.dirname(__file__)
		map_folder = path.join(game_folder,"Tmx_Files")
		img_folder = path.join(game_folder,"img")
		self.map = TiledMap(path.join(map_folder, 'level1.tmx'))
		self.map_img = self.map.make_map()
		self.map_rect = self.map_img.get_rect()
		self.player_img = pg.image.load(path.join(img_folder,PLAYER_IMG)).convert_alpha()
		self.mob_img = pg.image.load(path.join(img_folder,MOB_IMG)).convert_alpha()
		self.mob_img = pg.transform.scale(self.mob_img, (TILESIZE,TILESIZE))

	def new(self):
		#start a new game
		self.all_sprites = pg.sprite.Group()
		self.walls = pg.sprite.Group()
		self.mobs = pg.sprite.Group()
		# for row, tiles in enumerate(self.map.data):
		# 	for col, tile in enumerate(tiles):
		# 		if tile == '1':
		# 			Wall(self, col, row)
		# 		if tile == 'P':
		# 			self.player = Player(self, col, row)
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
			self.screen.blit(sprite.image, self.camera.apply(sprite))
		
		#FLIP
		pg.display.flip()

	def show_start_screen(self):
		# Show start screen
		pass

	def show_go_screen(self):
		# Show screen
		pass

g = Game()
g.show_start_screen()
while True:
	g.new()
	g.run()
	g.show_go_screen()

pg.quit()
