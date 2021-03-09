import sys
import math
import random
import time
#third party imports
import pygame as pg
from pygame.locals import *
import tkinter
from tkinter import messagebox


WIDTH = 1200
HEIGHT = 900
FPS = 30
BORDER_EVASION_BASE = 1.1
BOID_SPEED = 300
REBEL_COUNT = 30
IMPERIAL_COUNT = 30
VISION = 50

ALIGNMENT = 5
COHESION = 0.5
SEPERATION = 300

fireSprites = pg.sprite.RenderUpdates()

class DeadlyLaserRed(pg.sprite.Sprite):
    image = pg.Surface((300, 5), pg.SRCALPHA)
    pg.draw.rect(image, pg.Color('red'),
        pg.rect.Rect(0, 0, 300, 300), width = 3)  

    def __init__(self, position, rotation):
        super().__init__()
        self.position = position
        self.rotation = rotation
        self.image = pg.transform.rotate(self.__class__.image, -self.rotation.as_polar()[1])
        self.rect = self.image.get_rect(center=self.position + self.rotation * 170)
        fireSprites.add(self)

    def update(self, boids):
        pg.sprite.spritecollide(self, boids, dokill=True)
        self.kill()

class DeadlyLaserGreen(DeadlyLaserRed):
    image = pg.Surface((300, 5), pg.SRCALPHA)
    pg.draw.rect(image, pg.Color('green'),
        pg.rect.Rect(0, 0, 300, 300), width = 3)  

class ProbeDummy(pg.sprite.Sprite):

    def __init__(self, rect):
        super().__init__()
        self.rect = rect

class Boid(pg.sprite.Sprite):
    image = pg.Surface((10, 10), pg.SRCALPHA)
    pg.draw.polygon(image, pg.Color('white'),
        [(15, 5), (0, 2), (0, 8)])
    
    def __init__(self, position: pg.Vector2):
        super().__init__()
        self.position = position
        self.velocity = BOID_SPEED
        self.direction = pg.Vector2(random.randint(0, 10) - 5, random.randint(0, 10) - 5).normalize()
        self.heading = 0.0
        self.image = pg.transform.rotate(self.__class__.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)
        self.aim_rect = pg.transform.rotate(DeadlyLaserRed.image, -self.direction.as_polar()[1]).get_rect(center=self.position + self.direction * 170)

    def fire(self):
        DeadlyLaserRed(self.position, self.direction)

    def probe_fire(self, enemy_boids):
        if pg.sprite.spritecollide(ProbeDummy(self.aim_rect), enemy_boids, dokill=False) != []:
            return True
        return False

    def filter_boids(self, boids, radius):
        boids2 = boids
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if distance > radius or distance == 0.0:
                boids2.remove(boid)
        return boids2

    def update(self, boids, enemy_boids, dt: float):
        self.aim_rect = pg.transform.rotate(DeadlyLaserRed.image, -self.direction.as_polar()[1]).get_rect(center=self.position + self.direction * 170)
        if self.probe_fire(enemy_boids):
            self.fire()
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
        #swarm_center = swarm_center / len(boids)
        if counted == 0:
            return swarm_center
        swarm_center = swarm_center / counted
        if (swarm_center - self.position).length() == 0.0 or True:
            return swarm_center - self.position
        return (swarm_center - self.position).normalize()


    def separation(self, boids):
        aversion_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                aversion_vector += -1 / self.position.distance_squared_to(boid.position) * (boid.position - self.position)
        if aversion_vector.length() == 0.0 or True:
            return aversion_vector
        return aversion_vector.normalize()

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
        #direction_vector = direction_vector.normalize()
        return self.limit_turn(direction_vector)

class XWing(Boid):
    image = pg.image.load("images/x_wing_test.png")

    def fire(self):
        DeadlyLaserRed(self.position, self.direction)

class TieFighter(Boid):
    image = pg.image.load("images/tie_fighter_test.png")

    def fire(self):
        DeadlyLaserGreen(self.position, self.direction)

def draw(screen, background, boids):
    boids.clear(screen, background)
    fireSprites.clear(screen, background)
    lasers = fireSprites.draw(screen)
    dirty = boids.draw(screen)
    pg.display.update(dirty)
    pg.display.update(lasers)
    #pg.display.flip()

def update(boids, x_wings, tie_fighters, dt):
    old_wings = x_wings.copy()
    old_ties = tie_fighters.copy()
    for laser in fireSprites:
        laser.update(boids)
    for xwing in x_wings:
        xwing.update(old_wings.copy(), tie_fighters.copy(), dt)
    for tie in tie_fighters:
        tie.update(old_ties.copy(), x_wings.copy(), dt)

def show_info(info: str):
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo("Info!", info)

def exit():
    pg.quit()
    sys.exit(0)

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    screen.set_alpha(255)

    background = pg.Surface(screen.get_size())
    background.fill(pg.Color("black"))

    fps_clock = pg.time.Clock()

    boids = pg.sprite.RenderUpdates()
    x_wings = pg.sprite.RenderUpdates()
    tie_fighters = pg.sprite.RenderUpdates()
    for i in range(int(math.sqrt(REBEL_COUNT))):
        for j in range(int(math.sqrt(REBEL_COUNT))):
            xwing = XWing(pg.Vector2((i * 30, j * 30)))
            boids.add(xwing)
            x_wings.add(xwing)
    for i in range(int(math.sqrt(IMPERIAL_COUNT))):
        for j in range(int(math.sqrt(IMPERIAL_COUNT))):
            tie = TieFighter(pg.Vector2((i * 30 + 400, j * 30 + 400)))
            boids.add(tie)
            tie_fighters.add(tie)

    while(True):
        for event in pg.event.get():
            if event.type == QUIT:
                exit()
        dt = fps_clock.tick(FPS) * 1e-3
        if len(x_wings) == 0:
            show_info("The empire has won!")
            exit()
        if len(tie_fighters) == 0:
            show_info("The rebel alliance has won!")
            exit()
        update(boids, x_wings, tie_fighters, dt)
        draw(screen, background, boids)

if __name__ == "__main__":
    main()