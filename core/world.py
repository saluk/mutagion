#
# world.py
# a simple container of sprites, which are all rendered in order each frame
# subclass for your own scenes to actually do things

import pygame
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
        
def make_world(engine):
    """This makes the starting world"""
    w = World(engine)
    #Just put an icon somewhere
    w.add(Agent(art="art/icons/ico.png",pos=[50,50]))
    return w