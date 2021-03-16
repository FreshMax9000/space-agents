# Standard Lib Imports
import sys
import math
# Third Party Imports
import pygame as pg
from pygame.locals import QUIT


# Game Settings
WIDTH = 1200 # Width of window
HEIGHT = 900 # Height of window
FPS = 60 # Desired Frames Per Secound
# Boid Settings
BOID_SPEED = 300 # Speed of Boids in pixelsize / secound
BOIDS_COUNT = 150
VISION = 60 # Vision range of boids in pixelsize
ALIGNMENT = 5 # alignment weight in Boid.compute() method
COHESION = 0.5 # cohesion weight in Boid.compute() method
SEPERATION = 300 # seperation weight in Boid.compute() method


class Boid(pg.sprite.Sprite):
    # Set visual "surface" of Boid
    image = pg.Surface((10, 10))
    # Set visual representation to draw on surface
    # The "image" is a white polygon with 3 corners -> an arrow
    pg.draw.polygon(image, pg.Color('white'),
        [(15, 5), (0, 2), (0, 8)])

    def __init__(self, position: pg.Vector2):
        """Constructor of class Boid
        """
        super().__init__()
        self.position = position
        self.direction = pg.Vector2(10.0, 10.0).normalize() # Set initial moving direction
        self.close_boids = pg.sprite.RenderUpdates() # Initialize group for close boids
        self.rect = self.__class__.image.get_rect(center=self.position) #Initialize object rectangle

    def filter_boids(self, boids, radius):
        """Adds the given boids which are within radius to self.close_boids
        """
        self.close_boids.empty()
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if distance <= radius:
                self.close_boids.add(boid)

    def update(self, boids, dt: float):
        """Updates position and image based on physics and behaviour
        """
        self.filter_boids(boids, VISION) # Writes close boids in self.close_boids
        self.direction = self.compute(self.close_boids) # Compute new direction
        self.position += self.direction * BOID_SPEED * dt # move
        _, heading = self.direction.as_polar() # Obtain heading as angle
        self.image = pg.transform.rotate(self.__class__.image, -heading) # Rotate class image to fit heading
        self.rect = self.image.get_rect(center=self.position) # Set representation in space

    def alignment(self, boids):
        average_heading_vector = pg.Vector2((0, 0))
        for boid in boids:
            average_heading_vector += boid.direction.normalize()
        average_heading_vector = average_heading_vector.normalize()
        return average_heading_vector

    def cohesion(self, boids):
        swarm_center = pg.Vector2((0, 0))
        for boid in boids:
            swarm_center += boid.position
        swarm_center = swarm_center / len(boids)
        return swarm_center - self.position

    def separation(self, boids):
        aversion_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self == boid:
                aversion_vector += -1 / self.position.distance_squared_to(boid.position) * (boid.position - self.position)
        return aversion_vector

    def border_aversion(self):
        aversion_vector = pg.Vector2((0, 0))
        if self.position.x < 0:
            aversion_vector.x = self.position.x ** 2
        elif self.position.x > WIDTH:
            aversion_vector.x = -((self.position.x - WIDTH) ** 2)
        if self.position.y < 0:
            aversion_vector.y = self.position.y ** 2
        elif self.position.y > HEIGHT:
            aversion_vector.y = -((self.position.y - HEIGHT) ** 2)
        return aversion_vector

    def limit_turn(self, desired_turn: pg.Vector2):
        return (self.direction + desired_turn * 0.5).normalize()

    def compute(self, boids):
        direction_vector = self.alignment(boids) * ALIGNMENT
        direction_vector += self.cohesion(boids) * COHESION
        direction_vector += self.separation(boids) * SEPERATION
        direction_vector += self.border_aversion()
        return self.limit_turn(direction_vector)

def draw(screen, background, boids):
    """Draws the given background and boids on the screen
    """
    boids.clear(screen, background) # Draws the background over the boids rendered last time
    boids_rect = boids.draw(screen) # Draws the boids on the screen
    pg.display.update(boids_rect) # Refreshes only the part of the screen where boids are

def update(boids, dt):
    old_boids = boids.copy() # Copy boids to let all boids make decisions based on last game state
    boids.update(old_boids, dt) # Calls the update() method for all members of boids
    old_boids.empty() # Clear copy to free storage

def main():
    # Set up pygame and the window
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    # Generate a background surface
    background = pg.Surface(screen.get_size())
    background.fill(pg.Color("black"))
    # Generate Clock
    fps_clock = pg.time.Clock()
    # Generate Boids
    boids = pg.sprite.RenderUpdates()
    for i in range(int(math.sqrt(BOIDS_COUNT))):
        for j in range(int(math.sqrt(BOIDS_COUNT))):
            boids.add(Boid(pg.Vector2((i * 30 + 200, j * 30 + 200))))
    # Simulation Loop
    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit(0)
        dt = fps_clock.tick(FPS) * 1e-3 # Wait time to hold given Frames Per Secound
        update(boids, dt) # dt == time passed since last call
        draw(screen, background, boids)

if __name__ == "__main__":
    main()
