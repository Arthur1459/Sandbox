import vars as vr
import config as cf
import pygame as pg
from tools import *
from random import randint

def Text(msg, coord, size, color):  # blit to the screen a text
    TextColor = pg.Color(color) # set the color of the text
    font = pg.font.Font("../pixel.ttf", size)  # set the font
    return vr.window.blit(font.render(msg, True, TextColor), coord)  # return and blit the text on the screen

def getInputs():
    keys = pg.key.get_pressed()
    vr.inputs["SPACE"] = True if keys[pg.K_SPACE] else False
    vr.inputs["Z"] = True if keys[pg.K_z] else False
    vr.inputs["S"] = True if keys[pg.K_s] else False

def isInWindow(coord):
    if 0 <= coord[0] <= vr.win_width:
        if 0 <= coord[1] <= vr.win_height:
            return True
    return False

def KeepInWin(coord, delta=0):
    return (coord[0] if delta <= coord[0] <= vr.win_width - delta else (delta if coord[0] < delta else vr.win_width - delta), coord[1] if delta <= coord[1] <= vr.win_height - delta else (delta if coord[1] < delta else vr.win_height - delta))

def makeSeg(a, b):
    return lambda t: (b[0] + (t - 1) * (b[0] - a[0]), b[1] + (t - 1) * (b[1] - a[1]))

def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def isIntersecting(seg1, seg2):
    p, r = seg1(0), Vdiff(seg1(1), seg1(0))
    q, s = seg2(0), Vdiff(seg2(1), seg2(0))

    rxs = cross_product(r, s)

    if rxs != 0.: # May intersect
        t = cross_product(Vdiff(q, p), s) / rxs
        u = cross_product(Vdiff(q, p), r) / rxs
        if 0 <= t <= 1 and 0 <= u <= 1: # Verify validity
            return True, seg1(t)
        return False, None
    elif cross_product(Vdiff(q, p), r) == 0.: # Collinear
        dt = scalar(s, r) / scalar(r, r)
        if scalar(s, r) / scalar(r, r) <= 1:
            return True, seg2(1/2) if norm(Vdiff(seg1(1), seg1(0))) > norm(Vdiff(seg2(1), seg2(0))) else seg1(1/2)
    else: # Not intersecting
        return False, None


def getRndCoord(delta=20):
    return randint(delta, vr.win_width - delta), randint(delta, vr.win_height - delta)

def drawSeg(seg, color=(20, 20, 100), width=1):
    pg.draw.line(vr.window, color, seg[0], seg[1], width)

def getNewId():
    vr.id += 1
    return vr.id

def isValidIndex(l, c, grid):
    return True if (0 <= l < len(grid) and 0 <= c < len(grid[0])) else False

def get_grid_pos(coord):
    return int(ControlValue((coord[0] * cf.grid_factor) // vr.win_width, 0, len(vr.grid) - 1)), int(ControlValue((coord[1] * cf.grid_factor) // vr.win_width, 0, len(vr.grid[0]) - 1))

def get_distance_to_side(coord):
    return min([coord[0], vr.win_width - coord[0], coord[1], vr.win_height - coord[1]])

def nearest_side_projection(coord) -> tuple:
    distance = min([coord[0], vr.win_width - coord[0], coord[1], vr.win_height - coord[1]])
    if distance == coord[0]:
        return 0, coord[1]
    elif distance == vr.win_width - coord[0]:
        return vr.win_width, coord[1]
    elif distance == coord[1]:
        return coord[0], 0
    else:
        return coord[0], vr.win_height

def opposite_side(side_coord):
    if side_coord[0] <= 0:
        return (vr.win_width, side_coord[1])
    elif side_coord[0] >= vr.win_width:
        return (0, side_coord[1])
    elif side_coord[1] <= 0:
        return (side_coord[0], vr.win_height)
    else:
        return (side_coord[0], 0)