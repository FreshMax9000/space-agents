import sys
import math
import time
import logging
#third party imports
import pygame as pg

from pygame.locals import QUIT, KEYDOWN
import tkinter
from tkinter import messagebox
#project imports
import constants as const
from lasers import DeadlyLaserRed
from lasers import DeadlyLaserGreen
from boids import XWing
from boids import TieFighter
from behaviours import StandardBehaviour


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO
)


laserSprites = pg.sprite.RenderUpdates()


def draw(screen, background, boids):
    boids.clear(screen, background)
    laserSprites.clear(screen, background)
    lasers = laserSprites.draw(screen)
    dirty = boids.draw(screen)
    pg.display.update(dirty)
    pg.display.update(lasers)

def update(boids, x_wings, tie_fighters, dt):
    old_wings = x_wings.copy()
    old_ties = tie_fighters.copy()
    for laser in laserSprites:
        laser.update(boids)
    for xwing in x_wings:
        xwing.update(old_wings.copy(), tie_fighters.copy(), laserSprites, dt)
    for tie in tie_fighters:
        tie.update(old_ties.copy(), x_wings.copy(), laserSprites, dt)

def fill_rebels(boids, x_wings, count):
    for i in range(int(math.sqrt(const.REBEL_COUNT))):
        for j in range(int(math.sqrt(const.REBEL_COUNT))):
            xwing = XWing(pg.Vector2((i * 30, j * 30)), StandardBehaviour)
            boids.add(xwing)
            x_wings.add(xwing)

def fill_imperial(boids, tie_fighters, count):
    for i in range(int(math.sqrt(count))):
        for j in range(int(math.sqrt(count))):
            tie = TieFighter(pg.Vector2((i * 30 + 750, j * 30 + 750)), StandardBehaviour)
            boids.add(tie)
            tie_fighters.add(tie)

def show_info(info: str):
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo("Info!", info)

def exit():
    pg.quit()
    sys.exit(0)

def main():
    pg.init()
    screen = pg.display.set_mode((const.WIDTH, const.HEIGHT))
    screen.set_alpha(255)

    background = pg.Surface(screen.get_size())
    background.fill(pg.Color("black"))

    fps_clock = pg.time.Clock()

    boids = pg.sprite.RenderUpdates()
    x_wings = pg.sprite.RenderUpdates()
    tie_fighters = pg.sprite.RenderUpdates()
    fill_rebels(boids, x_wings, const.REBEL_COUNT)
    fill_imperial(boids, tie_fighters, const.IMPERIAL_COUNT)

    while(True):
        try:
            event = pg.event.get()[0]
        except IndexError:
            continue
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN:
            break

    while(True):
        for event in pg.event.get():
            if event.type == QUIT:
                exit()
        dt = fps_clock.tick(const.FPS) * 1e-3
        if fps_clock.get_rawtime() == fps_clock.get_time():
            logging.warning(f"Lagging behind {fps_clock.get_rawtime() - 1.0 / const.FPS}ms!")
        if len(x_wings) == 0:
            show_info("The empire has won!")
            exit()
        if len(tie_fighters) == 0:
            show_info("The rebel alliance has won!")
            exit()
        update(boids, x_wings, tie_fighters, dt)
        draw(screen, background, boids)

if __name__ == "__main__":
    main()