#
# world.py
# a simple container of sprites, which are all rendered in order each frame
# subclass for your own scenes to actually do things

import pygame
import random
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
            for near in c.travelmap:
                pygame.draw.line(engine.surface,[50,150,50],c.pos,near[1].pos)
        for c in self.world.cities:
            color = [0,255,0]
            if c.get_infected():
                color = [255,0,0]
            pygame.draw.circle(engine.surface,color,c.pos,4)
            x,y = pygame.mouse.get_pos()
            if x>=c.pos[0]-8 and x<=c.pos[0]+8 and y>=c.pos[1]-8 and y<=c.pos[1]+8:
                self.world.over = c
        c = None
        if self.world.over:
            c = self.world.over
        elif self.world.panel.city:
            c = self.world.panel.city
        if c:
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
            
class Text(Agent):
    def set_text(self,text):
        self.text = text
        return self
    def draw(self,engine):
        t = engine.font.render(self.text,1,[0,255,0])
        engine.surface.blit(t,self.pos)

class Panel(Agent):
    def init(self):
        self.turnon = None
        self.city = None
        self.objects = []
    def update(self,world):
        self.objects = []
        px = 10
        py = 10
        if self.city:
            self.objects.append(Text(pos=[px,py]).set_text(self.city.name))
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
    def draw(self,engine):
        self.surface.fill([0,0,0])
        pygame.draw.rect(self.surface,[0,255,0],[[0,0],[200,480]],2)
        super(Panel,self).draw(engine)
        for o in self.objects:
            p = o.pos[:]
            o.pos[0]+=self.pos[0]
            o.pos[1]+=self.pos[1]
            o.draw(engine)
            o.pos = p
        
        
class MapWorld(World):
    def play_music(self):
        pygame.mixer.music.load("music/gurdonark_-_Glow.ogg")
        pygame.mixer.music.play(-1)
    def start(self,num_viruses=1):
        self.offset = [0,0]
        self.add(Agent(art="art/americalowres.png",pos=[0,0]))
        c = CityDrawer()
        c.world = self
        self.add(c)
        self.panel = Panel(pos=[-200,0])
        self.panel.surface = pygame.Surface([200,480])
        self.add(self.panel)
        self.num_viruses = num_viruses
        self.load_cities()
        self.play_music()
        self.over = None
        self.turn_time = 60
        self.next_turn = self.turn_time
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
        for c in self.cities:
            c.travel_table(self.cities)
            for x in range(random.randint(4,14)):
                c.add(gen_random_population())
        for i in range(self.num_viruses):
            random.shuffle(self.cities)
            zero = self.cities[0]
            p = random.choice(zero.people)
            infect(badvirus,p)
    def input(self,controller):
        if controller.mbdown:
            if self.over:
                self.panel.turnon = self.over.pos[0]
                self.panel.pos[0] = -200
                self.panel.city = self.over
            else:
                self.panel.pos[0] = -200
                self.panel.turnon = None
    def update(self):
        super(MapWorld,self).update()
        self.next_turn -= 1
        if self.next_turn <=0:
            self.next_turn = self.turn_time
            self.turn()
    def turn(self):
        [c.turn({}) for c in self.cities]
        
def make_world(engine):
    """This makes the starting world"""
    w = MapWorld(engine)
    return w