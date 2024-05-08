import pygame as pg
from math import cos, sin, pi, tan
import tools as t
import utils as u
import vars as vr
import config as cf
import time
from entities import Planet

def init():

    pg.init()
    pg.display.set_caption(cf.game_name)

    # screen initialisation
    if not cf.fullscreen:
        vr.window = pg.display.set_mode(vr.window_size)
    else:
        vr.window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        vr.window_size = vr.window.get_size()

    vr.clock = pg.time.Clock()
    return

def main():
    init()

    vr.running = True

    frames_fps, t_fps = 0, time.time() - 1

    for i in range(30):
        vr.entities_list.append(Planet(u.getRndCoord(), mass=cf.mass_ref * u.randint(10, 100), speed=(u.randint(-100, 100), u.randint(-100, 100))))

    vr.entities_list.append(Planet(vr.middle, mass=1e30, static=True))

    while vr.running:

        vr.clock.tick(cf.fps)

        frames_fps += 1
        vr.fps = frames_fps/(time.time() - t_fps)
        vr.dt = (1 / vr.fps if vr.fps != 0 else 0.1) * vr.time_factor
        if frames_fps > 1000:
            frames_fps, t_fps = 0, time.time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                vr.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                print("Cursor : ", pg.mouse.get_pos())

        # Main Loop #
        if vr.fps > cf.fps * cf.fps_treshold:
            vr.has_start = True
            display_pre_update()
            u.getInputs()
            update()
            display_post_update()
        elif vr.has_start is False:
            display_low_fps()
        else:
            display_low_fps_started()
        # --------- #

    return

def update():
    vr.cursor = pg.mouse.get_pos()

    if vr.wait_key:
        if vr.inputs["Z"]:
            vr.time_factor += 1
            vr.wait_key = False
        elif vr.inputs["S"]:
            vr.time_factor -= 1
            vr.wait_key = False
    else:
        if time.time() - vr.t_key > 0.3:
            vr.wait_key = True
            vr.t_key = time.time()

    for entity in vr.entities_list:
        entity.update()
        entity.draw()

    if cf.debug:
        zone_size = (vr.win_width // cf.grid_factor, vr.win_height // cf.grid_factor)
        for line in range(1, cf.grid_factor):
            vr.seg_to_draw.append([(0, zone_size[1] * line), (vr.win_width, zone_size[1] * line)])
        for col in range(1, cf.grid_factor):
            vr.seg_to_draw.append([(zone_size[0] * col, 0), (zone_size[0] * col, vr.win_height)])

    return

def display_pre_update():
    if cf.persistence == 0:
        vr.window.fill('black')
    else:
        persistence = pg.Surface(vr.window_size)
        persistence = persistence.convert_alpha()
        persistence.fill((0, 0, 0, cf.persistence))
        vr.window.blit(persistence, (0, 0))

    return

def display_post_update():
    for seg in vr.seg_to_draw:
        u.drawSeg(seg)
    vr.seg_to_draw = []

    for pt in vr.points_to_draw:
        if (isinstance(pt, list) or isinstance(pt, tuple)) and len(pt) == 2:
            pg.draw.circle(vr.window, 'yellow', pt, 4)
    vr.points_to_draw = []

    mask = pg.Surface((248, 24))
    mask.fill('black')
    vr.window.blit(mask, (0, vr.win_height - 24))
    u.Text(f"fps: {str(round(vr.fps, 1))} / {cf.fps}  |  Speed: {vr.time_factor}x", (8, vr.win_height - 18), 14, 'white')
    pg.display.update()
    return

def display_low_fps():
    vr.window.fill('black')
    u.Text(f"FPS Stabilisation... ({str(round(vr.fps, 1))}/{int(cf.fps * cf.fps_treshold)})", (16, 16), 20, 'white')
    pg.display.update()
    return

def display_low_fps_started():
    mask = pg.Surface((400, 50))
    mask.fill('black')
    vr.window.blit(mask, (0, 0))
    u.Text(f"FPS Stabilisation... ({str(round(vr.fps, 1))}/{int(cf.fps * cf.fps_treshold)})", (16, 16), 20, 'white')
    return

if __name__ == "__main__":
    main()