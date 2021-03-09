import random

import pygame as pg

import constants as const
from lasers import DeadlyLaserRed
from lasers import DeadlyLaserGreen


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
        self.velocity = const.BOID_SPEED
        try:
            self.direction = pg.Vector2(random.randint(0, 10) - 5, random.randint(0, 10) - 5).normalize()
        except ValueError:
            self.direction = pg.Vector2((1, 0))
        self.heading = 0.0
        self.image = pg.transform.rotate(self.__class__.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)
        self.aim_rect = pg.transform.rotate(DeadlyLaserRed.image, -self.direction.as_polar()[1]).get_rect(center=self.position + self.direction * 170)

    def fire(self, laser_sprites):
        DeadlyLaserRed(self.position, self.direction, laser_sprites)

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

    def update(self, boids, enemy_boids, laser_sprites, dt: float):
        self.aim_rect = pg.transform.rotate(DeadlyLaserRed.image, -self.direction.as_polar()[1]).get_rect(center=self.position + self.direction * 170)
        if self.probe_fire(enemy_boids):
            self.fire(laser_sprites)
        boids = self.filter_boids(boids, const.VISION)
        self.direction = self.compute(boids, enemy_boids)
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
        if self.position.x < const.WIDTH_INNER:
            aversion_vector.x = const.BORDER_EVASION_BASE ** -(self.position.x - const.WIDTH_INNER)
        elif self.position.x > const.WIDTH_OUTER:
            aversion_vector.x = -(const.BORDER_EVASION_BASE ** (self.position.x - const.WIDTH_OUTER))
        if self.position.y < const.HEIGHT_INNER:
            aversion_vector.y = const.BORDER_EVASION_BASE ** -(self.position.y - const.HEIGHT_INNER)
        elif self.position.y > const.HEIGHT_OUTER:
            aversion_vector.y = -(const.BORDER_EVASION_BASE ** (self.position.y - const.HEIGHT_OUTER))
        return aversion_vector

    def hunting(self, enemy_boids):
        try:
            closest_enemy = min([e for e in enemy_boids], key=lambda e: self.position.distance_to(e.position))
        except ValueError:
            return pg.Vector2((0, 0))
        return (closest_enemy.position - self.position).normalize()

    def avoid_enemy_swarm(self, enemy_boids):
        enemy_center = pg.Vector2((0, 0))
        for e in enemy_boids:
            enemy_center += e.position
        try:
            enemy_center = enemy_center / len(enemy_boids)
        except ZeroDivisionError:
            return pg.Vector2((0, 0))
        
        return -(enemy_center - self.position) * (1 / self.position.distance_to(enemy_center))

    def limit_turn(self, desired_turn: pg.Vector2):
        return (self.direction + desired_turn * 0.5).normalize()

    def compute(self, boids, enemy_boids):
        direction_vector = self.alignment(boids) * const.ALIGNMENT
        direction_vector += self.cohesion(boids) * const.COHESION
        direction_vector += self.separation(boids) * const.SEPERATION
        direction_vector += self.border_aversion()
        direction_vector += self.hunting(enemy_boids) * const.HUNTING
        direction_vector += self.avoid_enemy_swarm(enemy_boids) * const.AVOID_ENEMY
        return self.limit_turn(direction_vector)


class XWing(Boid):
    image = pg.image.load("images/x_wing_test.png")

    def fire(self, laser_sprites):
        DeadlyLaserRed(self.position, self.direction, laser_sprites)


class TieFighter(Boid):
    image = pg.image.load("images/tie_fighter_test.png")

    def fire(self, laser_sprites):
        DeadlyLaserGreen(self.position, self.direction, laser_sprites)