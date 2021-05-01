import json
import pygame, math
import random
from pygame.locals import *
import time
import pygame
from hxlr import *
from bosh import Rider
from typing import *

Point = hxlr_math_geom_Point

class LineType:
    BLUE = 0
    ACCEL = 1
    SCENERY = 2

line_colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 255, 0),
]

pygame.init()
pygame.display.init()
pygame.display.set_caption("HXLR Python")

grid = hxlr_engine_Grid()
riders = []


def loadTrack(name: str):
    with open(name) as f:
        data = json.load(f)
    
    for c, rider_data in enumerate(data["riders"]):
        rider = Rider(hxlr_Constants.defaultRider(), Point(*rider_data["startPosition"].values()), f"Bosh{c}")
        rider.startVel = Point(*rider_data["startVelocity"].values())
        riders.append(rider)
    
    for line_data in data["lines"]:
        if line_data["type"] == LineType.BLUE:
            line = hxlr_lines_Floor(
                Point(line_data["x1"], line_data["y1"]),
                Point(line_data["x2"], line_data["y2"]),
                line_data["flipped"]
            )
        elif line_data["type"] == LineType.ACCEL:
            line = hxlr_lines_Accel(
                Point(line_data["x1"], line_data["y1"]),
                Point(line_data["x2"], line_data["y2"]),
                line_data["flipped"]
            )
        elif line_data["type"] == LineType.SCENERY:
            line = hxlr_lines_Scenery(
                Point(line_data["x1"], line_data["y1"]),
                Point(line_data["x2"], line_data["y2"]),
                line_data["flipped"]
            )

        grid.register(line)
        

loadTrack("test.json")

class Renderer:
    def __init__(self, screen, size: Point):
        self.screen = screen
        self.SIZE = size
        self.zoom = 1
        self.pos = Point(self.SIZE.x/2,self.SIZE.y/2)

    def ToScreenPos(self, point: Point):
        return (point + self.pos) * self.zoom
    
    def drawLine(self, p1: Point, p2: Point, width, color):
        pygame.draw.line(
            self.screen, color,
            tuple(self.ToScreenPos(p1)), tuple(self.ToScreenPos(p2)),
            int(width*self.zoom)
        )
    
    def drawCircle(self, pos: Point, radius, color, width=1):
        radius = float(radius)

        pos = self.ToScreenPos(pos)

        pygame.draw.circle(
            self.screen, color,
            (int(pos.x), int(pos.y)),
            int(radius*self.zoom), int(width*self.zoom)
        )
    

class Simulation:
    def __init__(self, grid: hxlr_engine_Grid, riders: List[Rider]):
        self.SIZE = Point(600, 600)
        self.screen = pygame.display.set_mode(list(self.SIZE))
        self.running = True
        self.screen.fill((0, 0, 0))
        self.radius = 1
        self.points = []
        self.FPS = 40
        self.clock = pygame.time.Clock()
        self.dragging = False
        self.selecting = False
        self.grid = grid
        self.riders = riders
        self.renderer = Renderer(self.screen, self.SIZE)
        self.frame = 0
        self.playing = False
    
    def renderLines(self):
        for line in self.grid.lines:
            self.renderer.drawLine(line.start, line.end, 1, line_colors[line.type])
    
    def renderRiders(self):
        for rider in self.riders:
            for contactPoint in rider.contactPoints:
                self.renderer.drawCircle(contactPoint.pos, 1, (0, 0, 0))
    
    def stepSim(self):
        for rider in self.riders:
            rider.step()
        self.frame += 1
    
    def reset(self):
        for rider in self.riders:
            rider.reset()
        self.frame = 0


    def process(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.start_x,self.start_y = 0,0
            if event.button == 1:		
                self.dragging = True
                self.old_mouse_x, self.old_mouse_y = event.pos
                #print(event.pos)
                self.offset_x = 0
                self.offset_y = 0
            if event.button == 4:
                self.renderer.zoom += self.renderer.zoom * 0.1
            if event.button == 5:
                self.renderer.zoom += -(self.renderer.zoom * 0.1)
            if event.button == 3:
                self.start_x, self.start_y = event.pos
                self.mouse_x, self.mouse_y = event.pos
                self.selecting = True
                self.true_start = (self.mouse_x/self.renderer.zoom-self.renderer.pos.x),(-self.mouse_y/self.renderer.zoom-self.renderer.pos.y)
            #print(zoom)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:			
                self.dragging = False
            if event.button == 3:
                self.selecting = False
                self.start_x,self.start_y = 0,0
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.mouse_x, self.mouse_y = event.pos
                self.renderer.pos.x = self.renderer.pos.x + (self.mouse_x - self.old_mouse_x) / self.renderer.zoom
                self.renderer.pos.y = self.renderer.pos.y + (self.mouse_y - self.old_mouse_y) / self.renderer.zoom
                self.old_mouse_x, self.old_mouse_y = self.mouse_x, self.mouse_y

        if event.type == pygame.VIDEORESIZE:
            surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_x:
                self.reset()
            if event.key == pygame.K_p:
                self.playing = not self.playing

        keys = pygame.key.get_pressed()
        if keys[K_RIGHT] or self.playing:
            self.stepSim()

        self.screen.fill((255, 255, 255))
        self.renderLines()
        self.renderRiders()

        pygame.display.flip()
        self.clock.tick(self.FPS)


renderer = Simulation(grid, riders)

while renderer.running:
    renderer.process()