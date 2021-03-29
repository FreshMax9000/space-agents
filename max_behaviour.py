
import pygame as pg

from behaviours import BaseBehaviour
import constants as const
from boids import Boid


class MaxBehaviour(BaseBehaviour):

    def __init__(self, boid):
        super().__init__(boid)

    def get_moves(self, friends, enemies, laser_hit_enemy, distress_calls):
        if len(enemies) == 0:
            direction = self.border_aversion()
        else:
            closest_enemy = min([e for e in enemies], key=lambda e: self.boid.position.distance_to(e.position))
            direction = (closest_enemy.position - self.boid.position).normalize() - self.boid.direction * 2
        fire = not self.boid.probe_fire(friends) and len(enemies) != 0

        return (direction, fire, None)

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

class MaxBehaviour2(BaseBehaviour):

    def __init__(self, boid):
        super().__init__(boid)

    def get_closest_enemy(self, enemies):
        return min([e for e in enemies], key=lambda e: self.boid.position.distance_to(e.position))

    def separation(self, friends):
        aversion_vector = pg.Vector2((0, 0))
        for boid in friends:
            aversion_vector += -1 / self.boid.position.distance_squared_to(boid.position) * (boid.position - self.boid.position)
        return aversion_vector

    def spinny_spinny(self):
        return pg.Vector2((self.boid.direction.y, -self.boid.direction.x))

    def get_scared(self, boid: Boid):
        offset_pos = self.boid.position - boid.position
        angle_dif = abs(abs(offset_pos.as_polar()[1]) - abs(boid.direction.as_polar()[1]))
        return angle_dif < 90

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

    def get_moves(self, friends, enemies, laser_hit_enemy, distress_calls):
        if len(enemies) != 0:
            closest_enemy = self.get_closest_enemy(enemies)
            if self.get_scared(closest_enemy):
                fire = False
                direction = -(self.get_closest_enemy(enemies).position - self.boid.position)
            else:
                fire = True
                direction = self.get_closest_enemy(enemies).position - self.boid.position
        else:
            direction = self.separation(friends) * 50 + self.border_aversion() + self.spinny_spinny() * 0.001 + self.boid.direction
            fire = False
        return (direction, fire, None)
