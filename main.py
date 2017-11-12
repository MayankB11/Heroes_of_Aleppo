<<<<<<< HEAD
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
		self.map = Map(path.join(game_folder, 'map.txt'))

	def new(self):
		#start a new game
		self.all_sprites = pg.sprite.Group()
		self.walls = pg.sprite.Group()
		for row, tiles in enumerate(self.map.data):
			for col, tile in enumerate(tiles):
				if tile == '1':
					Wall(self, col, row)
				if tile == 'P':
					self.player = Player(self, col, row)
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
		self.screen.fill(BLACK)
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
=======
import pygame

pygame.init()
width = height = 1000
screen = pygame.display.set_mode((width, height))
done = False

while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        
        pygame.display.flip()
>>>>>>> 6bc5b83848e5adfbabcda715e7b73fee05e2f414
