import math

from typing import List

from behaviours import StandardBehaviour
import constants as const
import pygame as pg

from boids import Boid

# Type aliases for often used ones
BoidList = List[Boid]

class MarvinBehaviour(StandardBehaviour):
    def get_within_range(self, boids: BoidList, range_to_check: float):
        in_range = []
        closest: (float, Boid) = (float('inf'), None)
        for other in boids:
            dist = self.boid.position.distance_to(other.position)
            if dist <= range_to_check:
                in_range.append(other)
            if dist < closest[0]:
                closest = (dist, other)
        return in_range, closest

    @staticmethod
    def is_within_angle(ang_thresh: float, direction: pg.Vector2, offset: pg.Vector2):
        #          aaaaaaaaaaaa                    aaaaaaaaaaaa
        ang_diff = math.degrees(math.acos(math.cos(math.radians(direction.as_polar()[1] - offset.as_polar()[1]))))
        return ang_diff <= ang_thresh

    def check_threat(self, potential_threats: BoidList):
        is_threatened = False
        smallest_dist = (float('inf'), None)
        for enemy in potential_threats:
            offset: pg.Vector2 = self.boid.position - enemy.position
            relevant = self.is_within_angle(15, enemy.direction, offset)
            is_threatened |= relevant
            if relevant:
                dist = offset.magnitude()
                if dist < smallest_dist[0]:
                    smallest_dist = (dist, enemy)
        return is_threatened, smallest_dist

    # 1. get all enemies within vision range
    # 2. check if any are aiming within X degrees of me
    # 3. if True:
    # 3.1. choose direction that best avoids the closest one of them
    # 3.2. if margin to enemies allows: try to curve away, hopefully into ally range
    # 3.3. otherwise keep best escape vector
    # 4. if False:
    # 4.1. pursue nearest enemy
    def get_moves(self, friends: BoidList, enemies: BoidList, laser_hit_enemy: bool, distress_calls: List[pg.Vector2]):
        direction = self.boid.direction
        # direction += self.cohesion(friends) * const.COHESION
        direction += self.border_aversion()
        direction += self.hunting(enemies) * const.HUNTING
        direction += self.avoid_enemy_swarm(enemies) * const.AVOID_ENEMY

        is_threatened, threat_dist = self.check_threat(enemies)
        threat_dir = direction
        if is_threatened:
            # for enemy in enemies:
            #     offset = self.boid.position - enemy.position
            #     threat_dir += offset

            enemy = threat_dist[1]
            offset = self.boid.position - enemy.position
            threat_dir += offset

            threat_dir = threat_dir.normalize()
            if threat_dist[0] > const.LASER_LENGTH * 1.2:
                threat_dir = threat_dir.rotate(45)
            direction += threat_dir
        else:
            direction += self.separation(friends) * const.SEPERATION
            direction += self.alignment(friends) * const.ALIGNMENT

        return direction.normalize(), laser_hit_enemy, None
