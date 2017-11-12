import pygame as pg
from settings import *
import pytmx

class Map:
    def __init__(self,filename):
        self.data = []
        with open(filename,'rt') as f:
            for line in f:
                self.data.append(line.strip())
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth*TILESIZE
        self.height = self.tileheight*TILESIZE


class TiledMap:
    def __init__(self,filename):
        tm = pytmx.load_pygame(filename, pixelalpha = True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self,surface):
        ti = self.tmxdata.get_tile_image_by_gid
class Camera:
    def __init__(self,width,height):
        self.camera = pg.Rect(0,0,width,height)
        self.width = width
        self.height = height

    def apply(self,entity):
        return entity.rect.move(self.camera.topleft)

    def update(self,target):
        x = -target.rect.x + int(WIDTH/2)
        y = -target.rect.y + int(HEIGHT/2)

        #Limit scrolling to map size
        x = min(0,x) #left
        y = min(0,y) #top
        x = max(-(self.width-WIDTH),x)
        y = max(-(self.height-HEIGHT),y)

        self.camera = pg.Rect(x,y,self.width,self.height)
