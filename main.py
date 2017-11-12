#Heroes of Aleppo
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *

# HUD functions

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
		self.hostage_count=0
		self.score=0
	def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
		font = pg.font.Font(font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect(**{align: (x, y)})
		self.screen.blit(text_surface, text_rect)

	def load_data(self):
		game_folder = path.dirname(__file__)
		map_folder = path.join(game_folder,"Tmx_Files")
		img_folder = path.join(game_folder,"img")
		self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
		self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
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
		self.mob_static=pg.sprite.Group()
		self.bullets = pg.sprite.Group()
		self.hostages=pg.sprite.Group()
		for tile_object in self.map.tmxdata.objects:
			if tile_object.name == "Player":
				self.player = Player(self,tile_object.x, tile_object.y)
			elif tile_object.name == "Wall":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height)
			elif tile_object.name == "Obstacle":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height)
			elif tile_object.name == "mob":
				Mob(self,tile_object.x,tile_object.y)
			elif tile_object.name=="mobstatic":
				staticMobs(self,tile_object.x,tile_object.y)
			elif tile_object.name=="Hostage1":
				Hostage(self,tile_object.x,tile_object.y,1)
			elif tile_object.name=="Hostage2":
				Hostage(self,tile_object.x,tile_object.y,3)
			elif tile_object.name=="Hostage3":
				Hostage(self,tile_object.x,tile_object.y,5)
			print(tile_object.x,tile_object.y);

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
		hits = pg.sprite.spritecollide(self.player, self.hostages, False, collide_hit_rect)
		for hit in hits:
			self.player.resources-=HOSTAGE_RESCUE
			hit.kill()
			self.hostage_count=self.hostage_count+1
			self.score+=100
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
			elif isinstance(sprite,staticMobs):
				sprite.draw_health()
			elif isinstance(sprite,Hostage):
				sprite.draw_timer()
			self.screen.blit(sprite.image, self.camera.apply(sprite))
		draw_player_health(self.screen, 10, 30, self.player.health/PLAYER_HEALTH)
		draw_player_resources(self.screen, 10, 80, self.player.resources/PLAYER_RESOURCES)        
		self.draw_text('Hostages: {}'.format(str(self.hostage_count)+"/"+str(HOSTAGE_COUNT)), self.hud_font, 30, WHITE, WIDTH - 10, 10, align="topright")		
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
