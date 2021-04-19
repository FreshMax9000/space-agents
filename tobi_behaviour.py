
import pygame as pg

from behaviours import BaseBehaviour
import constants as const
from boids import Boid
ALIGNMENT = 10
COHESION = 0.35
SEPERATION = 40
HUNTING = 24
AVOID_ENEMY = 5
AVOID_ENEMYfire = 150




class TobiBehaviour(BaseBehaviour):

    def __init__(self, boid):
        super().__init__(boid)

    def border_aversion(self):
        aversion_vector = pg.Vector2((0, 0))
        if self.boid.position.x < const.WIDTH_INNER:
            aversion_vector.x = const.BORDER_EVASION_BASE ** -(self.boid.position.x - const.WIDTH_INNER)
            aversion_vector.y += 0.01
        elif self.boid.position.x > const.WIDTH_OUTER:
            aversion_vector.x = -(const.BORDER_EVASION_BASE ** (self.boid.position.x - const.WIDTH_OUTER))
            aversion_vector.y += 0.01
        if self.boid.position.y < const.HEIGHT_INNER:
            aversion_vector.y = const.BORDER_EVASION_BASE ** -(self.boid.position.y - const.HEIGHT_INNER)
            aversion_vector.x += 0.01
        elif self.boid.position.y > const.HEIGHT_OUTER:
            aversion_vector.y = -(const.BORDER_EVASION_BASE ** (self.boid.position.y - const.HEIGHT_OUTER))
            aversion_vector.x += 0.01
        return aversion_vector


    def get_scared(self, boid: Boid):
        offset_pos = self.boid.position - boid.position
        angle_dif = abs(abs(offset_pos.as_polar()[1]) - abs(boid.direction.as_polar()[1]))
        return angle_dif < 90

    def get_moves(self, friends, enemies, laser_hit_enemy, distress_calls):
        if len(friends) == 0 and len(enemies) == 0:
            print("err")
        direction = self.compute(friends, enemies)
        fire = laser_hit_enemy
        return (direction, fire, None)

    def alignment(self, boids):
        average_heading_vector = pg.Vector2((0, 0))
        for boid in boids:
            if not self.boid.position.distance_squared_to(boid.position) == 0.0:
                average_heading_vector += boid.direction.normalize()
        if average_heading_vector.length() == 0.0:
            return average_heading_vector
        return average_heading_vector.normalize()

    def cohesion(self, boids):
        swarm_center = pg.Vector2((0, 0))
        counted = 0
        for boid in boids:
            if not self.boid.position.distance_squared_to(boid.position) == 0.0:
                swarm_center += boid.position
                counted += 1
        if counted == 0:
            return swarm_center
        swarm_center = swarm_center / counted
        return swarm_center - self.boid.position

    def separation(self, friends):
        aversion_vector = pg.Vector2((0, 0))
        for boid in friends:
            if not self.boid.position.distance_squared_to(boid.position) == 0.0:
                aversion_vector += -1 / self.boid.position.distance_squared_to(boid.position) * (
                            boid.position - self.boid.position)
        return aversion_vector

    def border_aversion(self):
        aversion_vector = pg.Vector2((0, 0))
        if self.boid.position.x < const.WIDTH_INNER:
            aversion_vector.x = const.BORDER_EVASION_BASE ** -(self.boid.position.x - const.WIDTH_INNER)
            aversion_vector.y += 0.01
        elif self.boid.position.x > const.WIDTH_OUTER:
            aversion_vector.x = -(const.BORDER_EVASION_BASE ** (self.boid.position.x - const.WIDTH_OUTER))
            aversion_vector.y += 0.01
        if self.boid.position.y < const.HEIGHT_INNER:
            aversion_vector.y = const.BORDER_EVASION_BASE ** -(self.boid.position.y - const.HEIGHT_INNER)
            aversion_vector.x += 0.01
        elif self.boid.position.y > const.HEIGHT_OUTER:
            aversion_vector.y = -(const.BORDER_EVASION_BASE ** (self.boid.position.y - const.HEIGHT_OUTER))
            aversion_vector.x += 0.01
        return aversion_vector

    def hunting(self, enemy_boids):
        enemy_center = pg.Vector2((0, 0))
        for e in enemy_boids:
            enemy_center += e.position
        try:
            enemy_center = enemy_center / len(enemy_boids)
        except ZeroDivisionError:
            return pg.Vector2((0, 0))

        try:
            closest_enemy = min([e for e in enemy_boids], key=lambda e: self.boid.position.distance_to(e.position))
        except ValueError:
            return pg.Vector2((0, 0))

        closest_enemy = (closest_enemy.position - self.boid.position).normalize()
        return (closest_enemy).normalize()


    def avoid_enemy_swarm(self, enemy_boids):
        enemy_center = pg.Vector2((0, 0))
        for e in enemy_boids:
            enemy_center += e.position
        try:
            enemy_center = enemy_center / len(enemy_boids)
        except ZeroDivisionError:
            return pg.Vector2((0, 0))

        return -(enemy_center - self.boid.position) * (1 / self.boid.position.distance_to(enemy_center))

    def avoid_enemy_fire(self, enemy_boids):
        enemy_center = pg.Vector2((0, 0))
        for e in enemy_boids:
            enemy_center += e.position
        try:
            closest_enemy = min([e for e in enemy_boids], key=lambda e: self.boid.position.distance_to(e.position))
        except ValueError:
            return pg.Vector2((0, 0))
        if self.get_scared(closest_enemy):
            fire = False
            closest_enemy = (closest_enemy.position - self.boid.position).normalize()
            return -(closest_enemy).normalize()
        else:
            fire = True
            closest_enemy = (closest_enemy.position - self.boid.position).normalize()
            return (closest_enemy).normalize()
        
	
	

    def compute(self, boids, enemy_boids):
        direction_vector = self.alignment(boids) * ALIGNMENT
        direction_vector += self.cohesion(boids) * COHESION
        direction_vector += self.separation(boids) * SEPERATION
        direction_vector += self.border_aversion() 
        direction_vector += self.hunting(enemy_boids) * HUNTING
        direction_vector += self.avoid_enemy_swarm(enemy_boids) * AVOID_ENEMY
        direction_vector += self.avoid_enemy_fire(enemy_boids) * AVOID_ENEMYfire
        

        return direction_vector

