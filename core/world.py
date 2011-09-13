#
# world.py
# a simple container of sprites, which are all rendered in order each frame
# subclass for your own scenes to actually do things

import pygame
from virus import *
from agents import *

class World(object):
    def __init__(self,engine):
        self.engine = engine
        self.objects = []
        self.start()
    def add(self,o):
        """Add an object to the scene"""
        self.objects.append(o)
    def start(self):
        """Code that runs when a world starts, base world
        doesn't need to do anything"""
    def update(self):
        """self.sprites starts empty, any object added to the list during
        update() is going to be rendered"""
        self.sprites = []
        for o in self.objects:
            o.update(self)
            if o.visible:
                self.sprites.append(o)
    def draw(self):
        """Iterate sprites and draw them"""
        [s.draw(self.engine) for s in self.sprites]
    def input(self,controller):
        """As controller gets functions to check the state of things, input
        can be put here"""
        
class CityDrawer(Agent):
    def draw(self,engine):
        self.world.over = None
        for c in self.world.cities:
            pygame.draw.circle(engine.surface,[0,255,0],c.pos,4)
            x,y = pygame.mouse.get_pos()
            if x>=c.pos[0]-8 and x<=c.pos[0]+8 and y>=c.pos[1]-8 and y<=c.pos[1]+8:
                self.world.over = c
        if self.world.over:
            c = self.world.over
            cname = engine.font.render(c.name,1,[0,0,0])
            s = cname.copy()
            s.fill([0,255,0])
            s.blit(cname,[0,0])
            px,py = [c.pos[0]-s.get_width()//2+10,c.pos[1]-s.get_height()//2-10]
            if px<0:
                px = 0
            if py<0:
                py = 0
            engine.surface.blit(s,[px,py])

class Panel(Agent):
    def update(self,world):
        if not hasattr(self,"turnon"):
            self.turnon = None
        if self.turnon:
            if self.turnon<640//2:
                d = 640-200
                if self.pos[0]<d:
                    self.pos[0]=640
                if self.pos[0]>d:
                    self.pos[0]-=10
            else:
                d = 0
                if self.pos[0]>d:
                    self.pos[0]=-200
                if self.pos[0]<d:
                    self.pos[0]+=10
        
class MapWorld(World):
    def play_music(self):
        pygame.mixer.music.load("music/gurdonark_-_Glow.ogg")
        pygame.mixer.music.play(-1)
    def start(self):
        self.offset = [0,0]
        self.add(Agent(art="art/americalowres.png",pos=[0,0]))
        c = CityDrawer()
        c.world = self
        self.add(c)
        self.panel = Panel(pos=[-200,0])
        self.panel.surface = pygame.Surface([200,480])
        self.add(self.panel)
        self.load_cities()
        self.play_music()
        self.over = None
    def load_cities(self):
        self.cities = []
        f = open("dat/cities.txt")
        for l in f.read().split("\n"):
            if l.endswith("*"):
                stuff = [x.strip() for x in l.split("  ") if x.strip()]
                code,lat,long,city = stuff
                city = city[:-1]
                city,state = city.split(",")
                if "/" in city:
                    city = city.split("/",1)[0]
                lat = float(lat)
                long = float(long)
                width=64
                height=20
                px = (-long+123)/float(width)*640+25
                py = (-lat+48)/float(height)*480
                self.cities.append(Location(name=city+", "+state,lat=lat,long=long,pos=[px,py]))
    def input(self,controller):
        if controller.mbdown and self.over:
            self.panel.turnon = self.over.pos[0]
            self.panel.pos[0] = -200
        
def make_world(engine):
    """This makes the starting world"""
    w = MapWorld(engine)
    return w