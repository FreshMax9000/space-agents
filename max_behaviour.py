
import pygame as pg

from behaviours import BaseBehaviour
import constants as const


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
