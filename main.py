import sys
import math
import random
import time
#third party imports
import pygame as pg
from pygame.locals import *


WIDTH = 1200
HEIGHT = 900
FPS = 30
BORDER_EVASION_BASE = 1.1
BOID_SPEED = 150
BOIDS_COUNT = 100
VISION = 50

ALIGNMENT = 5
COHESION = 0.5
SEPERATION = 300


class Boid(pg.sprite.Sprite):
    image = pg.Surface((10, 10), pg.SRCALPHA)
    pg.draw.polygon(image, pg.Color('white'),
        [(15, 5), (0, 2), (0, 8)])
    
    def __init__(self, position: pg.Vector2):
        super().__init__()
        self.position = position
        self.velocity = BOID_SPEED
        self.direction = pg.Vector2(10.0, 10.0).normalize()
        self.heading = 0.0
        self.image = pg.transform.rotate(self.__class__.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)

    def filter_boids(self, boids, radius):
        boids2 = boids
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if distance > radius or distance == 0.0:
                boids2.remove(boid)
        if len(boids) == 0:
            print(len(boids2))
        return boids2

    def update(self, boids, dt: float):
        boids = self.filter_boids(boids, VISION)
        self.direction = self.compute(boids)
        self.position += self.direction * self.velocity * dt 
        speed, self.heading = self.direction.as_polar()
        self.image = pg.transform.rotate(self.__class__.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)

    def alignment(self, boids):
        average_heading_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                average_heading_vector += boid.direction.normalize()
        if average_heading_vector.length() == 0.0:
            return average_heading_vector
        return average_heading_vector.normalize()

    def cohesion(self, boids):
        swarm_center = pg.Vector2((0, 0))
        counted = 0
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                if self.position.distance_to(boid.position) < 150:
                    swarm_center += boid.position
                    counted += 1
        if counted == 0:
            return swarm_center
        swarm_center = swarm_center / counted
        return swarm_center - self.position

    def separation(self, boids):
        aversion_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                aversion_vector += -1 / self.position.distance_squared_to(boid.position) * (boid.position - self.position)
        return aversion_vector

    def border_aversion(self):
        aversion_vector = pg.Vector2((0, 0))
        if self.position.x < 0:
            aversion_vector.x = BORDER_EVASION_BASE ** -self.position.x
        elif self.position.x > WIDTH:
            aversion_vector.x = -(BORDER_EVASION_BASE ** (self.position.x - WIDTH))
        if self.position.y < 0:
            aversion_vector.y = BORDER_EVASION_BASE ** -self.position.y
        elif self.position.y > HEIGHT:
            aversion_vector.y = -(BORDER_EVASION_BASE ** (self.position.y - HEIGHT))
        return aversion_vector

    def limit_turn(self, desired_turn: pg.Vector2):
        return (self.direction + desired_turn * 0.5).normalize()

    def compute(self, boids):
        direction_vector = self.alignment(boids) * ALIGNMENT
        direction_vector += self.cohesion(boids) * COHESION
        direction_vector += self.separation(boids) * SEPERATION
        direction_vector += self.border_aversion()
        return self.limit_turn(direction_vector)

class XWing(Boid):
    image = pg.image.load("images/x_wing_test.png")

def draw(screen, background, boids):
    boids.clear(screen, background)
    dirty = boids.draw(screen)
    pg.display.update(dirty)

def update(boids, dt):
    old_boids = boids.copy()
    for b in boids:
        b.update(old_boids.copy(), dt)

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    screen.set_alpha(255)

    background = pg.Surface(screen.get_size())
    background.fill(pg.Color("black"))

    fps_clock = pg.time.Clock()

    boids = pg.sprite.RenderUpdates()
    for i in range(int(math.sqrt(BOIDS_COUNT))):
        for j in range(int(math.sqrt(BOIDS_COUNT))):
            boids.add(XWing(pg.Vector2((i * 30 + 200, j * 30 + 200))))

    while(True):
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit(0)
        dt = fps_clock.tick(FPS) * 1e-3
        print(float(dt))
        update(boids, dt)
        draw(screen, background, boids)

if __name__ == "__main__":
    main()