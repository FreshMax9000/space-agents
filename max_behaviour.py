
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
        return angle_dif < 10

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
            direction = self.separation(friends) + self.border_aversion() + self.spinny_spinny() * 0.01 + self.boid.direction
            fire = False
        return (direction, fire, None)


class MaxBehaviour3(MaxBehaviour2):

    def alignment(self, friends):
        average_heading_vector = pg.Vector2((0, 0))
        for boid in friends:
            if not self.boid.position.distance_squared_to(boid.position) == 0.0:
                average_heading_vector += boid.direction.normalize()
        if average_heading_vector.length() == 0.0:
            return average_heading_vector
        return average_heading_vector.normalize()

    def get_enemy_center(self, enemy_boids):
        enemy_center = pg.Vector2((0, 0))
        for e in enemy_boids:
            enemy_center += e.position
        try:
            enemy_center = enemy_center / len(enemy_boids)
        except ZeroDivisionError:
            return pg.Vector2((0, 0))
        return enemy_center

    def border_aversion(self):
        aversion_vector = pg.Vector2((0, 0))
        if self.boid.position.x < const.WIDTH_INNER:
            aversion_vector.x = -(self.boid.position.x - const.WIDTH_INNER)
            aversion_vector.y += 0.1
        elif self.boid.position.x > const.WIDTH_OUTER:
            aversion_vector.x = -(self.boid.position.x - const.WIDTH_OUTER)
            aversion_vector.y += 0.1
        if self.boid.position.y < const.HEIGHT_INNER:
            aversion_vector.y = -(self.boid.position.y - const.HEIGHT_INNER)
            aversion_vector.x += 0.1
        elif self.boid.position.y > const.HEIGHT_OUTER:
            aversion_vector.y = -(self.boid.position.y - const.HEIGHT_OUTER)
            aversion_vector.x += 0.1
        return aversion_vector

    def get_scared(self, boid: Boid):
        offset_pos = self.boid.position - boid.position
        angle_dif = abs(abs(offset_pos.as_polar()[1]) - abs(boid.direction.as_polar()[1]))
        return angle_dif < 30

    def get_abs_angle_to(self, boid):
        offset_pos = boid.position - self.boid.position
        return abs(abs(offset_pos.as_polar()[1]) - abs(self.boid.direction.as_polar()[1]))

    def get_moves(self, friends, enemies, laser_hit_enemy, distress_calls):
        if len(enemies) != 0:
            get_scared_list = tuple(map(self.get_scared, enemies))
            if any(get_scared_list):
                fire = False
                direction = -(self.get_enemy_center(enemies) - self.boid.position)
            else:
                fire = self.get_abs_angle_to(self.get_closest_enemy(enemies)) < 30
                direction = self.get_closest_enemy(enemies).position - self.boid.position
        else:
            direction = self.separation(friends) * 3 + self.border_aversion() * 5e-7 + self.alignment(friends) * 0.1
            fire = False
        return (direction, fire, None)


class DummDumm(BaseBehaviour):

    def __init__(self, boid):
        super().__init__(boid)

    def get_moves(self, friends, enemies, laser_hit_enemy, distress_calls):
        direction = pg.Vector2((self.boid.direction.y, -self.boid.direction.x))
        fire = False
        return (direction, fire, None)
