import math
import random

import pygame as pg
from math import cos, sin, pi, tan
import tools as t
import utils as u
import vars as vr
import config as cf
import time
from Entity import Particle, Link, SolidLink, Polygone, Body
from geometry import SolidLine
import datetime

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

    vr.t_key = time.time()
    frames_fps, t_fps = 0, time.time() - 1

    for i in range(cf.nb_body):
        vr.bodies.append(Body())

    while vr.running:

        vr.clock.tick(cf.fps)

        frames_fps += 1
        vr.fps = frames_fps/(time.time() - t_fps)
        vr.dt = cf.dt_ref * vr.time_factor
        vr.t += vr.dt
        if frames_fps > 20:
            frames_fps, t_fps = 0, time.time()

        vr.inputs["CLICK"] = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                vr.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if cf.debug:
                    print("Cursor : ", pg.mouse.get_pos())
                vr.inputs["CLICK"] = True

        # Main Loop #
        if vr.fps > cf.fps * cf.fps_treshold:
            vr.has_start = True
            display_pre_update()
            u.getInputs()
            update()
            display_post_update()
        elif vr.has_start is False:
            display_low_fps()

        if vr.fps < cf.fps * cf.fps_treshold * 1.05 or vr.low_fps is True:
            vr.low_fps = True
        if vr.fps > cf.fps * cf.fps_treshold * 1.3:
            vr.low_fps = False
        # --------- #

    return

def update():
    vr.cursor = pg.mouse.get_pos()
    if vr.inputs['ESC']:
        with open(f"./bestGenArchive/{datetime.datetime.today()}.txt", "w") as f:
            f.write(str(vr.best_gen))
        vr.running = False
        return

    # -------------- Key ----------------- #
    if vr.inputs["CLICK"]:
        if vr.inputs["V"]:
            vr.geo_pts.append((vr.cursor, True if vr.inputs["N"] else False))
            vr.make_multi_geo = True
        elif len(vr.geo_pts) > 0:
            for i in range(len(vr.geo_pts) - 1):
                p1, st1 = vr.geo_pts[i]
                p2, st2 = vr.geo_pts[i+1]
                SolidLine(p1, p2)
            vr.geo_pts = []
            vr.make_multi_geo = False
        else:
            if vr.make_geo is False:
                vr.geo_pt_1 = vr.cursor
                vr.make_geo = True
                vr.st_1 = True if vr.inputs["N"] else False
            else:
                vr.geo_pt_2 = vr.cursor
                vr.make_geo = False
                vr.st_2 = True if vr.inputs["N"] else False
                SolidLine(vr.geo_pt_1, vr.geo_pt_2)

    if vr.inputs['T'] and vr.wait_key:
        if len(vr.geo_list) != 0:
            geo_id = vr.geo_list.pop()
            del vr.geo[geo_id]
        u.keyResetTime(0.2)

    if vr.wait_key:
        if vr.inputs["Z"]:
            vr.time_factor += 0.5
            if vr.time_factor == 0: vr.time_factor = 0.5
            u.keyResetTime(0.3)
        elif vr.inputs["S"]:
            vr.time_factor -= 0.5
            if vr.time_factor == 0: vr.time_factor = -0.5
            u.keyResetTime(0.3)
    if vr.inputs["P"] and vr.wait_key:
        if vr.slow_factor < 0.95:
            vr.slow_factor += 0.05
        u.keyResetTime(0.1)
    elif vr.inputs["M"] and vr.wait_key:
        if 0.051 < vr.slow_factor:
            vr.slow_factor -= 0.05
        u.keyResetTime(0.1)

    if vr.inputs['F'] and vr.wait_key:
        vr.mode = cf.modes[(cf.modes.index(vr.mode) + 1) % len(cf.modes)]
        u.keyResetTime(0.5)
    elif vr.inputs['G'] and vr.wait_key:
        vr.gravity_mode = cf.gravity_modes[(cf.gravity_modes.index(vr.gravity_mode) + 1) % len(cf.gravity_modes)]
        u.keyResetTime(0.5)

    if time.time() - vr.t_key > 0.5:
        vr.wait_key = True
    else:
        vr.wait_key = False
    # ------------------------------------ #

    vr.cluster_time += vr.dt
    if len(vr.gen_buffer[vr.cluster]) >= cf.nb_body:
        vr.cluster_time = 0
        vr.cluster = (vr.cluster + 1) % cf.nb_cluster

        best_gen = u.getBestGen(vr.gen_buffer[vr.cluster])
        if len(vr.gen_buffer[vr.cluster]) != 0 and vr.best_gen is not None:
            best_pulse, best_phase, best_amp = best_gen
            for i in range(cf.nb_body - 1):
                pulse, phase, amp = u.getMutation(best_pulse, delta=0.2), u.getMutation(best_phase, delta=0.8), u.getMutation(best_amp, delta=0.02)
                u.CreateBody(pulse, phase, amp)
            u.CreateBody(best_pulse, best_phase, best_amp, color=(250, 200, 20))
        else:
            for i in range(cf.nb_body):
                u.CreateBody(None, None, None)
        vr.gen_buffer[vr.cluster] = []

    for body in vr.bodies:
        if body.life_time > 10:
            body.on_delete()
            vr.bodies.remove(body)
            vr.gen_buffer[vr.cluster].append((u.target_distance(body.body_center.coord), body.pulsations, body.phase, body.amplitudes))
        elif body.body_center.coord[1] > 570: # fall
            body.on_delete()
            vr.bodies.remove(body)
            vr.gen_buffer[vr.cluster].append((None, body.pulsations, body.phase, body.amplitudes))

    for entity_id in vr.entities_list:
        entity = vr.entities[entity_id]
        entity.update()
        entity.draw()

    for geo_id in vr.geo:
        geo = vr.geo[geo_id]
        geo.draw()

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

    pg.draw.line(vr.window, (200, 100, 0), (cf.target, vr.middle[1] - vr.rect_size[1]/2), (cf.target, vr.middle[1] + vr.rect_size[1]/2))
    if vr.best_score:
        pg.draw.line(vr.window, (80, 250, 20), (abs(vr.best_score - cf.target), vr.middle[1] - vr.rect_size[1]/2), (abs(vr.best_score - cf.target), vr.middle[1] + vr.rect_size[1]/2))

    if vr.mode == 'circle':
        pg.draw.circle(vr.window, (255, 255, 255), vr.middle, vr.circle_radius, width=3)
    elif vr.mode == 'rectangle':
        w, h = vr.rect_size
        w, h = w/2, h/2
        vr.seg_to_draw.append(u.makeSeg(t.Vadd(vr.middle, (-w, -h)), t.Vadd(vr.middle, (w, -h))))
        vr.seg_to_draw.append(u.makeSeg(t.Vadd(vr.middle, (w, -h)), t.Vadd(vr.middle, (w, h))))
        vr.seg_to_draw.append(u.makeSeg(t.Vadd(vr.middle, (w, h)), t.Vadd(vr.middle, (-w, h))))
        vr.seg_to_draw.append(u.makeSeg(t.Vadd(vr.middle, (-w, h)), t.Vadd(vr.middle, (-w, -h))))
    elif vr.mode == 'corridor':
        w, h = (vr.win_width, vr.corridor_height)
        w, h = w/2, h/2
        vr.seg_to_draw.append(u.makeSeg(t.Vadd(vr.middle, (-w, -h)), t.Vadd(vr.middle, (w, -h))))
        vr.seg_to_draw.append(u.makeSeg(t.Vadd(vr.middle, (w, h)), t.Vadd(vr.middle, (-w, h))))
    else:
        pass

    if vr.make_geo is True:
        pg.draw.line(vr.window, ('white' if vr.geo_pt_1[0] < vr.cursor[0] else 'red'), vr.geo_pt_1, vr.cursor, 3)
        #vr.seg_to_draw.append(u.makeSeg(vr.geo_1, vr.cursor))
    if vr.make_multi_geo is True:
        for i in range(len(vr.geo_pts) - 1):
            p1, st1 = vr.geo_pts[i]
            p2, st2 = vr.geo_pts[i + 1]
            pg.draw.line(vr.window, 'white', p1, p2, 3)
        pg.draw.line(vr.window, 'white', vr.geo_pts[-1][0], vr.cursor, 3)

    for seg in vr.seg_to_draw:
        u.drawSeg(seg, color=(255, 255, 255), width=3)
    vr.seg_to_draw = []

    for pt in vr.points_to_draw:
        if (isinstance(pt, list) or isinstance(pt, tuple)) and len(pt) == 2:
            pg.draw.circle(vr.window, 'yellow', pt, 4)
    vr.points_to_draw = []

    if vr.low_fps:
        display_low_fps_started()

    for body in vr.bodies:
        u.Text(f"|", (body.body_center.coord[0], vr.middle[1] + vr.rect_size[1]/2 + 2), 18, (200, 0, 0))

    u.Text(f"{round(vr.cluster_time, 1)}", (12, 32), 20, (250, 200, 20))
    u.Text(f"Cluster: {vr.cluster + 1} / {cf.nb_cluster} | Best: {vr.best_score}", (12, 12), 20, 'white')

    u.Text(f"fps: {str(round(vr.fps, 1))} / {cf.fps}  |  Speed: {vr.time_factor}x  |  Entities: {len(vr.entities_list)}  |  Slow : {round(vr.slow_factor, 2)}  |  Mode : {vr.mode}  |  Gravity : {vr.gravity_mode}", (8, vr.win_height - 18), 14, 'white')
    pg.display.update()
    return

def display_low_fps():
    vr.window.fill('black')
    u.Text(f"FPS Stabilisation... ({str(round(vr.fps, 1))}/{int(cf.fps * cf.fps_treshold)})", (16, 16), 20, 'white')
    pg.display.update()
    return

def display_low_fps_started():
    #mask = pg.Surface((200, 30))
    #mask.fill('black')
    #vr.window.blit(mask, (0, 0))
    u.Text(f"# Low FPS # ({str(round(vr.fps, 1))}/{int(cf.fps * cf.fps_treshold)})", (12, 12), 12, 'white')
    return

if __name__ == "__main__":
    main()