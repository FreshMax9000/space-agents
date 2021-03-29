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
from faction import Faction


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO
)


laserSprites = pg.sprite.RenderUpdates()


def draw(screen, background, factions):
    laserSprites.clear(screen, background)
    for faction in factions:
        faction.boids.clear(screen, background)
        pg.display.update(faction.boids.draw(screen))
    lasers = laserSprites.draw(screen)
    pg.display.update(lasers)

def update(factions, dt):
    
    for laser in laserSprites:
        for faction in factions:
            laser.update(faction.boids)
    old_factions = [faction.copy() for faction in factions]
    for faction in factions:
        enemies = pg.sprite.RenderUpdates()
        friends = pg.sprite.RenderUpdates()
        for old_faction in old_factions:
            try:
                if not old_faction.has(faction.boids.sprites()[0]):
                    enemies.add(old_faction.boids.sprites())
                else:
                    friends.add(old_faction.boids.sprites())
            except IndexError:
                logging.warning(f"Faction \"{faction}\" is empty!")
        faction.update(friends, enemies, laserSprites, dt)

def fill_rebels(x_wings, count):
    for i in range(int(math.sqrt(const.REBEL_COUNT))):
        for j in range(int(math.sqrt(const.REBEL_COUNT))):
            xwing = XWing(pg.Vector2((i * 30, j * 30)), StandardBehaviour)
            x_wings.add(xwing)

def fill_imperial(tie_fighters, count):
    for i in range(int(math.sqrt(count))):
        for j in range(int(math.sqrt(count))):
            tie = TieFighter(pg.Vector2((i * 30 + 750, j * 30 + 750)), StandardBehaviour)
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

    x_wings = pg.sprite.RenderUpdates()
    tie_fighters = pg.sprite.RenderUpdates()
    fill_rebels(x_wings, const.REBEL_COUNT)
    fill_imperial(tie_fighters, const.IMPERIAL_COUNT)
    imperial_faction = Faction("Imperium", tie_fighters)
    rebel_faction = Faction("Rebellen", x_wings)
    factions = [imperial_faction, rebel_faction]

    while(True):
        for event in pg.event.get():
            if event.type == QUIT:
                exit()
        dt = fps_clock.tick(const.FPS) * 1e-3
        if fps_clock.get_rawtime() == fps_clock.get_time():
            logging.warning(f"Lagging behind {fps_clock.get_rawtime() - 1.0 / const.FPS}ms!")
        if len(factions[1]) == 0:
            show_info("The empire has won!")
            exit()
        if len(factions[0]) == 0:
            show_info("The rebel alliance has won!")
            exit()
        #update(boids, factions, dt)
        update(factions, dt)
        draw(screen, background, factions)

if __name__ == "__main__":
    main()