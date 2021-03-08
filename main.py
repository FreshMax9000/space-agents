import sys
import copy
#third party imports
import pygame as pg
from pygame.locals import *


WIDTH = 900
HEIGHT = 900
FPS = 30.0


class Boid(pg.sprite.Sprite):
    image = pg.image.load("images/x_wing_test.png")
    
    def __init__(self, position: pg.Vector2):
        super().__init__()
        self.position = position
        self.velocity = 150
        self.direction = pg.Vector2(10.0, 10.0)
        self.heading = 0.0

    def update(self, boids, dt: float):
        self.direction = self.compute(boids)
        self.position += self.direction * self.velocity * dt 
        speed, self.heading = self.direction.as_polar()
        self.image = pg.transform.rotate(Boid.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)

    def alignment(self, boids):
        average_heading_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                average_heading_vector += boid.direction.normalize()
        #TODO fix
        if average_heading_vector.length() == 0.0:
            return average_heading_vector
        return average_heading_vector.normalize()


    def cohesion(self, boids):
        swarm_center = pg.Vector2((0, 0))
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                swarm_center += boid.position
        swarm_center = swarm_center / len(boids)
        return (swarm_center - self.position).normalize()


    def separation(self, boids):
        aversion_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self.position.distance_squared_to(boid.position) == 0.0:
                aversion_vector += -1 / self.position.distance_squared_to(boid.position) * (boid.position - self.position)
        return aversion_vector

    def border_aversion(self):
        aversion_vector = pg.Vector2((0, 0))
        if self.position.x < 0:
            aversion_vector.x = 1
        elif self.position.x > WIDTH:
            aversion_vector.x = -1
        if self.position.y < 0:
            aversion_vector.y = 1
        elif self.position.y > HEIGHT:
            aversion_vector.y = -1
        if aversion_vector.length() != 0.0:
            return aversion_vector.normalize()
        return aversion_vector

    def compute(self, boids):
        direction_vector = self.alignment(boids)
        direction_vector += self.cohesion(boids)
        direction_vector += self.separation(boids) * 10
        direction_vector += self.border_aversion()
        direction_vector = direction_vector.normalize()
        return direction_vector


def draw(screen, background, boids):
    boids.clear(screen, background)
    dirty = boids.draw(screen)
    pg.display.update(dirty)

def update(boids, dt):
    for b in boids:
        b.update(boids, dt)

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    background = pg.Surface(screen.get_size())
    background.fill(pg.Color("black"))

    fps_clock = pg.time.Clock()

    boids = pg.sprite.RenderUpdates()
    for i in range(30):
        boids.add(Boid(pg.Vector2((100, 10 * i + 200))))

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