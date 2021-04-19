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
        # Initialize groups for close boids
        self.close_friends = pg.sprite.RenderUpdates()
        self.close_enemies = pg.sprite.RenderUpdates()

    def fire(self, laser_sprites):
        DeadlyLaserRed(self.position, self.direction, laser_sprites)

    def probe_fire(self, enemy_boids):
        if pg.sprite.spritecollideany(ProbeDummy(self.aim_rect), enemy_boids) is not None:
            return True
        return False

    def filter_boids(self, friends, enemies, radius):
        self.close_friends.empty()
        self.close_enemies.empty()
        for friend in friends:
            if self.position.distance_to(friend.position) <= radius and friend != self:
                self.close_friends.add(friend)
        for enemy in enemies:
            if self.position.distance_to(enemy.position) <= radius and enemy != self:
                self.close_enemies.add(enemy)

    def update(self, friends, enemies, laser_sprites, dt: float, distress_calls: list):
        self.filter_boids(friends, enemies, const.VISION)
        # Check if laser would hit enemy
        self.aim_rect = pg.transform.rotate(DeadlyLaserRed.image, -self.direction.as_polar()[1]).get_rect(center=self.position + self.direction * 170)
        laser_hit_enemy = self.probe_fire(self.close_enemies)
        # compute Behaviour based on specific behaviour class
        direction, fire, distress_call = self.behaviour.get_moves(self.close_friends, self.close_enemies, laser_hit_enemy, distress_calls)

        self.direction = self.limit_turn(direction) #limit direction change
        # Fire if requested
        if fire:
            self.fire(laser_sprites)
        # Update representation
        self.position += self.direction * self.velocity * dt 
        _, self.heading = self.direction.as_polar()
        self.image = pg.transform.rotate(self.__class__.image, -self.heading)
        self.rect = self.image.get_rect(center=self.position)
        return distress_call  

    def limit_turn(self, desired_turn: pg.Vector2):
        try:
            desired_turn = desired_turn.normalize()
        except ValueError:
            return self.direction
        angle_to_direction = desired_turn.angle_to(self.direction)
        if angle_to_direction > const.MAXIMUM_TURN_ANGLE and angle_to_direction <= 180:
            desired_turn = self.direction.rotate(-const.MAXIMUM_TURN_ANGLE)
        elif angle_to_direction < (360 - const.MAXIMUM_TURN_ANGLE) and angle_to_direction >= 180:
            desired_turn = self.direction.rotate(const.MAXIMUM_TURN_ANGLE)
        try:
            desired_turn = desired_turn.normalize()
        except ValueError:
            desired_turn = self.direction
        return desired_turn


class XWing(Boid):
    image = pg.image.load("images/x_wing_test.png")

    def fire(self, laser_sprites):
        DeadlyLaserRed(self.position, self.direction, laser_sprites)


class TieFighter(Boid):
    image = pg.image.load("images/tie_fighter_test.png")

    def fire(self, laser_sprites):
        DeadlyLaserGreen(self.position, self.direction, laser_sprites)