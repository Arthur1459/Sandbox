import pygame as pg
import config as cf
import vars as vr
import tools as t
from utils import rand
import utils as u
import time
from random import randint, random, choice
from math import sin, pi
from Cells import Soil, Sprout, Roc

def game_init():

    pg.init()
    pg.display.set_caption(cf.game_name)

    # screen initialisation
    if not cf.fullscreen:
        vr.window = pg.display.set_mode(vr.window_size)
    else:
        vr.window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        vr.window_size = vr.window.get_size()

    vr.grids[u.CurrentGrid()] = [[Soil(rand(25, 75)) for col in range(cf.grid_size[1])] for line in range(cf.grid_size[0])]
    for c in range(int((cf.grid_line * cf.grid_col / cf.roc_size**2) * cf.rocs_proportion/100)):
        u.MakeRoc(u.getRndPos(), size=cf.roc_size + randint(-5, 5))
    for i in range(cf.germs):
        u.MakeCluster(u.NewSproutGen(), u.NewTeam())
    for i in range(cf.altruist_germs):
        u.MakeCluster(u.NewSproutGen_Altruist(), u.NewTeam())
    for i in range(cf.selfish_germs):
        u.MakeCluster(u.NewSproutGen_Selfish(), u.NewTeam())
    vr.grids[u.NextGrid()] = vr.grids[u.CurrentGrid()]

    vr.clock = pg.time.Clock()
    u.LogPrint("initialised.", game_init)
    return

def main():
    u.LogPrint("started.", main)
    game_init()

    vr.running = True
    u.LogPrint("game started.", main)

    frames_fps, t_fps = 0, time.time() - 1

    while vr.running:

        vr.clock.tick(cf.fps)

        frames_fps += 1
        vr.fps = frames_fps/(time.time() - t_fps)
        if frames_fps > 1000:
            frames_fps, t_fps = 0, time.time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                vr.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                u.LogPrint(pg.mouse.get_pos())
                vr.inputs["CLICK"] = True
            else:
                vr.inputs["CLICK"] = False

        # Main Loop #
        u.getInputs()
        pre_display()
        game_update()
        post_display()
        # --------- #

    return

def game_update():

    if vr.inputs["ESCAPE"]:
        vr.running = False

    if vr.inputs["A"]:
        vr.mode = 'potential'
    elif vr.inputs["Z"]:
        vr.mode = 'selfish'
    elif vr.inputs["E"]:
        vr.mode = 'altruist'
    elif vr.inputs["R"]:
        vr.mode = 'team'

    if vr.inputs['CLICK']:
        u.MakeRoc(u.getPos(pg.mouse.get_pos()))

    if vr.inputs["Q"]:
        u.MakeCluster(u.NewSproutGen(), u.NewTeam())

    if vr.inputs["S"]:
        vr.food_factor = 20
    else:
        vr.food_factor = 1

    vr.grid = vr.grids[u.CurrentGrid()]
    for line in range(cf.grid_line):
        for col in range(cf.grid_col):
            cell = vr.grid[line][col]
            cell.draw((line, col))
            if not vr.inputs["SPACE"]:
                cell.update((line, col))

    vr.grid_index = u.NextGrid()
    return

def pre_display():
    vr.window.fill('black')
    return

def post_display():

    #u.Text("Gen : " + str(vr.general_genetics), (10, 25), 'orange')
    u.Text("Nb : " + str(vr.nb_entity), (150, vr.win_height - 24), 'orange')
    u.Text("fps : " + str(round(vr.fps, 1)), (10, vr.win_height - 24), 'orange')
    u.Text("mode : " + str(vr.mode), (10, vr.win_height - 42), 'orange')
    pg.display.update()
    return

if __name__ == "__main__":
    main()
