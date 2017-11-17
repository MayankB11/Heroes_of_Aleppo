#Heroes of Aleppo
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from moviepy.editor import *
from pygame.locals import *
import imageio
imageio.plugins.ffmpeg.download()

# HUD functions
img = pg.image.load('final.png')
img = pg.transform.scale(img, (WIDTH, 720))

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
		self.flag=0
		pg.init()
		pg.mixer.init()
		self.screen = pg.display.set_mode((WIDTH,HEIGHT))
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		pg.key.set_repeat(200,100)

		self.load_data()
		self.hostage_count=0
		self.score=0
		self.paused=False
		self.intro=False
	def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
		font = pg.font.Font(font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect(**{align: (x, y)})
		self.screen.blit(text_surface, text_rect)

	def load_data(self):
		game_folder = path.dirname(__file__)
		map_folder = path.join(game_folder,"Tmx_Files")
		img_folder = path.join(game_folder,"img")
		music_folder = path.join(game_folder, 'music')
		snd_folder = path.join(game_folder, 'snd')
		self.clip = (VideoFileClip("Intro_720p.mp4").fx(vfx.resize, width=960))
		self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
		self.dim_screen.fill((0, 0, 0, 180))
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
		self.gun_effect=pg.mixer.Sound(path.join(snd_folder,GUN_SOUND))
		self.gun_effect.set_volume(0.2)
		pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
	def new(self):
		#start a new game
		self.all_sprites = pg.sprite.Group()
		self.walls = pg.sprite.Group()
		self.mobs = pg.sprite.Group()
		self.mob_static=pg.sprite.Group()
		self.bullets = pg.sprite.Group()
		#self.clip.preview()
		self.hostages=pg.sprite.Group()
		for tile_object in self.map.tmxdata.objects:
			if tile_object.name == "Player":
				self.player = Player(self,tile_object.x, tile_object.y)
			elif tile_object.name == "Wall":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height,"Wall")
			elif tile_object.name == "Obstacle":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height,"Wall")
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
			elif tile_object.name=="NPCPlayer":
				self.support1 = Support(self,tile_object.x,tile_object.y,120)
			elif tile_object.name=="NPCPlayer1":
				self.support2 = Support(self,tile_object.x,tile_object.y,-120)
			elif tile_object.name == "Exit":
				Obstacle(self,tile_object.x,tile_object.y,tile_object.width,tile_object.height,"Exit")
	#		print(tile_object.x,tile_object.y);

		self.camera = Camera(self.map.width,self.map.height)

	def run(self):
		#start a new game
		if not self.intro:
		#	self.clip.preview()
			self.intro=True
		self.playing = True
		pg.mixer.music.play(loops=-1)
		while self.playing:
			self.dt = self.clock.tick(FPS)/1000
			self.events()
			if not self.paused:
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
			self.player.health=self.player.health-MOB_DAMAGE
			hit.vel=vec(0,0)
			if self.player.health<=0:
				self.flag=0
				self.playing = False
			elif self.player.health <= 30:
				self.support2.kill()
				if self.support2.isKilled == False:
					self.player.resources=self.player.resources-0.20*PLAYER_RESOURCES
				self.support2.isKilled = True
			elif self.player.health <= 60:
				self.support1.kill()
				if self.support1.isKilled == False:
					self.player.resources=self.player.resources-0.20*PLAYER_RESOURCES
				self.support1.isKilled = True
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
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					self.quit()
				#if event.key == pg.K_h:
				#	self.draw_debug = not self.draw_debug
				if event.key == pg.K_p:
					self.paused = not self.paused




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
		if self.paused:
			self.screen.blit(self.dim_screen, (0, 0))
			self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
		pg.display.flip()

	def show_start_screen(self):
		# Show start screen
		intro = True
		while intro:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					quit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_RETURN:
						intro = False
			#self.screen.fill(WHITE)
			self.screen.blit(img,(0,0))
			pg.display.update()
		
	def win_screen(self):
		#self.screen.fill(BLACK)
		self.screen.blit(self.dim_screen, (0, 0))
		self.draw_text("Score- "+str(self.score), self.title_font, 100, RED, WIDTH / 2, HEIGHT / 4, align="center")
		self.draw_text("You won", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
		self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
		pg.display.flip()
		self.hostage_count=0
		self.score=0
		#pg.display.update()
		self.wait_for_key()		
	def show_go_screen(self):
		#self.screen.fill(BLACK)
		self.screen.blit(self.dim_screen, (0, 0))
		self.draw_text("Score- "+str(self.score), self.title_font, 100, RED, WIDTH / 2, HEIGHT / 4, align="center")
		self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
		self.draw_text("Press a key to start", self.title_font, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
		pg.display.flip()
		self.hostage_count=0
		self.score=0
		#pg.display.update()
		self.wait_for_key()
		# Show screen
		pass
	def wait_for_key(self):
		pg.event.wait()
		waiting = True
		while waiting:
			self.clock.tick(FPS)
			for event in pg.event.get():
				if event.type == pg.QUIT:
					waiting = False
					self.quit()
				if event.type == pg.KEYUP:
					waiting = False	
# def start_game():
# 	intro = True
# 	while intro:
# 		for event in pg.event.get():
# 			if event.type == pg.QUIT:
# 				pg.quit()
# 				quit()
# 			if event.type == pg.KEYDOWN:
# 				if event.key == pg.K_RETURN:
# 					intro = False
# 		self.screen.fill(WHITE)
# 		self.screen.blit(img,(0,0))
# 		pg.display.update()
class initial:
	def __init__(self):
		pg.init()
		pg.mixer.init()
		self.screen = pg.display.set_mode((WIDTH,HEIGHT))
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
#		self.show_start()
	def show_start(self):
		intro = True
		clip = (VideoFileClip("Intro_720p.mp4").fx(vfx.resize, width=960))
		clip.preview()
		self.screen = pg.display.set_mode((WIDTH,HEIGHT))
		while intro:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					quit()
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_RETURN:
						intro = False
						break
			#self.screen.fill(WHITE)
			self.screen.blit(img,(0,0))
			pg.display.update()

#Start=initial()
#Start.show_start()
g = Game()
#g.show_start_screen()
while True:
	g.new()
	g.run()
	if g.flag==0:
		g.show_go_screen()
	else:
		g.win_screen()
pg.quit()
