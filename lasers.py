import pygame as pg

import constants as const

class DeadlyLaserRed(pg.sprite.Sprite):
    image = pg.Surface((const.VISION, 5), pg.SRCALPHA)
    pg.draw.rect(image, pg.Color('red'),
        pg.rect.Rect(0, 0, const.VISION, 5), width = const.VISION)  

    def __init__(self, position, rotation, laser_sprites):
        super().__init__()
        self.position = position
        self.rotation = rotation
        self.image = pg.transform.rotate(self.__class__.image, -self.rotation.as_polar()[1])
        self.rect = self.image.get_rect(center=self.position + self.rotation * (const.VISION / 2.0 + 20))
        laser_sprites.add(self)

    def update(self, boids):
        pg.sprite.spritecollide(self, boids, dokill=True)
        self.kill()

class DeadlyLaserGreen(DeadlyLaserRed):
    image = pg.Surface((const.VISION, 5), pg.SRCALPHA)
    pg.draw.rect(image, pg.Color('green'),
        pg.rect.Rect(0, 0, const.VISION, 5), width = const.VISION)