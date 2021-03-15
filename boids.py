import random
import logging

import pygame as pg

import constants as const
from lasers import DeadlyLaserRed
from lasers import DeadlyLaserGreen
from behaviours import BaseBehaviour


class ProbeDummy(pg.sprite.Sprite):

    def __init__(self, rect):
        super().__init__()
        self.rect = rect


class Boid(pg.sprite.Sprite):
    image = pg.Surface((10, 10), pg.SRCALPHA)
    pg.draw.polygon(image, pg.Color('white'),
        [(15, 5), (0, 2), (0, 8)])
    
    def __init__(self, position: pg.Vector2, behaviour_class):
        super().__init__()
        self.behaviour = behaviour_class(self)
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
        boids2 = boids.copy()
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if distance > radius or distance == 0.0:
                boids2.remove(boid)
        return boids2

    def update(self, boids, enemy_boids, laser_sprites, dt: float, distress_calls: list):
        boids = self.filter_boids(boids, const.VISION)
        enemy_boids = self.filter_boids(enemy_boids, const.VISION)
        # Check if laser would hit enemy
        self.aim_rect = pg.transform.rotate(DeadlyLaserRed.image, -self.direction.as_polar()[1]).get_rect(center=self.position + self.direction * 170)
        laser_hit_enemy = self.probe_fire(enemy_boids)
        # compute Behaviour based on specific behaviour class
        direction, fire, distress_call = self.behaviour.get_moves(boids, enemy_boids, laser_hit_enemy, distress_calls)

        self.direction = self.limit_turn(direction) #limit direction change
        # Fire if requested
        if fire:
            self.fire(laser_sprites)
        # Update representation
        self.position += self.direction * self.velocity * dt 
        speed, self.heading = self.direction.as_polar()
        self.image = pg.transform.rotate(self.__class__.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)  
        return distress_call  

    def limit_turn(self, desired_turn: pg.Vector2):
        try:
            return (self.direction + desired_turn.normalize() * 0.5).normalize()
        except ValueError:
            logging.info("Not enough inputs for boid, staying on course!")
            return self.direction.normalize()


class XWing(Boid):
    image = pg.image.load("images/x_wing_test.png")

    def fire(self, laser_sprites):
        DeadlyLaserRed(self.position, self.direction, laser_sprites)


class TieFighter(Boid):
    image = pg.image.load("images/tie_fighter_test.png")

    def fire(self, laser_sprites):
        DeadlyLaserGreen(self.position, self.direction, laser_sprites)