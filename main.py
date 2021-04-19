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
from faction import Faction
# Import behaviours
from behaviours import StandardBehaviour
from marvin_behaviour import MarvinBehaviour
from max_behaviour import MaxBehaviour, MaxBehaviour2, MaxBehaviour3, DummDumm
from benny_behaviour import BennyBehaviour
from tobi_behaviour import TobiBehaviour


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO
)


laserSprites = pg.sprite.RenderUpdates()


def draw(screen, background, factions, time_gone):
    # Draw status
    font = pg.font.Font(None, 30)
    text = f"{factions[1].name} - {len(factions[1])} : {len(factions[0])} - {factions[0].name}                                                                                {time_gone:.1f}s"
    status_surface = pg.Surface((1700, 200))
    status_surface.fill((0, 0, 0))
    status_surface.blit(font.render(text, 1, (255, 255, 255)), (480, 0))
    screen.blit(status_surface, status_surface.get_rect())
    pg.display.update(status_surface.get_rect())
    
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

def fill_rebels(x_wings, count, rebel_class):
    for i in range(int(math.sqrt(const.REBEL_COUNT))):
        for j in range(int(math.sqrt(const.REBEL_COUNT))):
            xwing = XWing(pg.Vector2((i * 30, j * 30 + 500)), rebel_class)
            x_wings.add(xwing)

def fill_imperial(tie_fighters, count, imperial_class):
    for i in range(int(math.sqrt(count))):
        for j in range(int(math.sqrt(count))):
            tie = TieFighter(pg.Vector2((i * 30 + 1500, j * 30 + 500)), imperial_class)
            tie_fighters.add(tie)

def show_info(info: str):
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo("Info!", info)

def exit():
    pg.quit()
    sys.exit(0)

def run_simulation(behaviour1, behaviour2):
    pg.init()
    screen = pg.display.set_mode((const.WIDTH, const.HEIGHT))
    screen.set_alpha(255)

    background = pg.Surface(screen.get_size())
    background.fill(pg.Color("black"))

    

    x_wings = pg.sprite.RenderUpdates()
    tie_fighters = pg.sprite.RenderUpdates()
    fill_rebels(x_wings, const.REBEL_COUNT, behaviour1)
    fill_imperial(tie_fighters, const.IMPERIAL_COUNT, behaviour2)
    rebel_faction = Faction(f"{behaviour1.__name__} (Rebellen)", x_wings)
    imperial_faction = Faction(f"{behaviour2.__name__} (Imperium)", tie_fighters)    
    factions = [imperial_faction, rebel_faction]

    time.sleep(0)

    fps_clock = pg.time.Clock()

    start_time = time.time()

    while(True):
        for event in pg.event.get():
            if event.type == QUIT:
                exit()
        dt = fps_clock.tick(const.FPS) * 1e-3
        if fps_clock.get_rawtime() == fps_clock.get_time():
            logging.warning(f"Lagging behind {fps_clock.get_rawtime() - 1.0 / const.FPS}ms!")
        if len(factions[1]) == 0:
            show_info(f"{factions[0].name} has won!")
            exit()
        if len(factions[0]) == 0:
            show_info(f"{factions[1].name} has won!")
            exit()
        update(factions, dt)
        time_gone = time.time() - start_time
        draw(screen, background, factions, time_gone)

        if time_gone > 60.0:
            if len(factions[0]) == len(factions[1]):
                show_info("Its a draw!")
                exit()
            elif len(factions[1]) > len(factions[0]):
                show_info(f"{factions[1].name} has won!")
                exit()
            else:
                show_info(f"{factions[0].name} has won!")
                exit()


def main():
    run_simulation(MarvinBehaviour, MaxBehaviour3)


if __name__ == "__main__":
    main()