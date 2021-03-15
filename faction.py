
import pygame as pg


class Faction:

    def __init__(self, boids: pg.sprite.Group, old_distress=[], new_distress=[]):
        self.boids = boids
        self.old_distress = old_distress
        self.new_distress = new_distress

    def update(self, friends, enemies, laser_sprites, dt):
        self.old_distress = self.new_distress
        self.new_distress = []
        for boid in self.boids:
            self.new_distress.append(boid.update(friends, enemies, laser_sprites, dt, self.old_distress))

    def copy(self):
        return Faction(self.boids.copy(), old_distress=self.old_distress, new_distress=self.new_distress)

    def has(self, sprite: pg.sprite.Sprite):
        return self.boids.has(sprite)

    def __len__(self):
        return len(self.boids)

        