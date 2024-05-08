import vars as vr
import config as cf
import pygame as pg
from tools import *
from random import randint
from time import time

def Text(msg, coord, size, color):  # blit to the screen a text
    TextColor = pg.Color(color) # set the color of the text
    font = pg.font.Font("../pixel.ttf", size)  # set the font
    return vr.window.blit(font.render(msg, True, TextColor), coord)  # return and blit the text on the screen

def getInputs():
    keys = pg.key.get_pressed()
    vr.inputs["SPACE"] = True if keys[pg.K_SPACE] else False
    vr.inputs["Z"] = True if keys[pg.K_z] else False  # speed fact +0.5
    vr.inputs["S"] = True if keys[pg.K_s] else False  # speed fact -0.5
    vr.inputs["ESC"] = True if keys[pg.K_ESCAPE] else False  # Quit
    vr.inputs["R"] = True if keys[pg.K_r] else False  # Place particle
    vr.inputs["T"] = True if keys[pg.K_t] else False  # Remove Line
    vr.inputs["Y"] = True if keys[pg.K_y] else False  # Reset entities
    vr.inputs["P"] = True if keys[pg.K_p] else False  # slow fact -0.05
    vr.inputs["M"] = True if keys[pg.K_m] else False  # slow fact +0.05
    vr.inputs["G"] = True if keys[pg.K_g] else False  # gravity mode
    vr.inputs["F"] = True if keys[pg.K_f] else False  # world mode
    vr.inputs["RIGHT"] = True if keys[pg.K_RIGHT] else False
    vr.inputs["LEFT"] = True if keys[pg.K_LEFT] else False
    vr.inputs["UP"] = True if keys[pg.K_UP] else False
    vr.inputs["DOWN"] = True if keys[pg.K_DOWN] else False
    vr.inputs["B"] = True if keys[pg.K_b] else False # make Rope
    vr.inputs["N"] = True if keys[pg.K_n] else False  # Static Point
    vr.inputs["V"] = True if keys[pg.K_v] else False  # Multi pts Geo

def keyResetTime(delay=0.5):
    vr.t_key = time() + delay - 0.5

def isInWindow(coord):
    if 0 <= coord[0] <= vr.win_width:
        if 0 <= coord[1] <= vr.win_height:
            return True
    return False

def KeepInWin(coord, delta=0):
    return (coord[0] if delta <= coord[0] <= vr.win_width - delta else (delta if coord[0] < delta else vr.win_width - delta), coord[1] if delta <= coord[1] <= vr.win_height - delta else (delta if coord[1] < delta else vr.win_height - delta))

def KeepInMiddle(coord, radius=vr.circle_radius, delta=0):
    dist = norm(Vdiff(coord, vr.middle))
    if dist + delta < radius:
        return coord, False
    else:
        return Vadd(vr.middle, Vmult(Vdiff(coord, vr.middle), (radius - delta)/dist)), True

def KeepInSquare(coord, dimension=vr.rect_size, delta=0):
    width, height = dimension
    w, h = width/2, height/2
    x_m, y_m = vr.middle
    return (coord[0] if x_m - w + delta <= coord[0] <= x_m + w - delta else (x_m - w + delta if coord[0] < x_m - w + delta else x_m + w - delta),
            coord[1] if y_m - h + delta <= coord[1] <= y_m + h - delta else (y_m - h + delta if coord[1] < y_m - h + delta else y_m + h - delta)), False

def KeepInHeight(coord, height=vr.corridor_height, delta=0):
    w, h = vr.win_width, height/2
    x_m, y_m = vr.middle
    return (coord[0], coord[1] if y_m - h + delta <= coord[1] <= y_m + h - delta else (y_m - h + delta if coord[1] < y_m - h + delta else y_m + h - delta)), False

def rgb(r, g, b):
    return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))

def makeSeg(a, b):
    return lambda t: (b[0] + (t - 1) * (b[0] - a[0]), b[1] + (t - 1) * (b[1] - a[1]))

def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def distance(a,b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def isInLine(a, b, pt, delta=5):
    if min(a[0], b[0]) - delta <= pt[0] <= max(a[0], b[0]) + delta and min(a[1], b[1]) - delta <= pt[1] <= max(a[1], b[1]) + delta:
        point_on_seg = makeSeg(a, b)(distance(a, pt) / distance(a, b))
        if abs(point_on_seg[0] - pt[0]) <= delta and abs(point_on_seg[1] - pt[1]) <= delta:
            return True
    return False

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
    pg.draw.line(vr.window, color, seg(0), seg(1), width)

def getNewId():
    vr.id += 1
    return vr.id

def isValidIndex(l, c, grid):
    return True if (0 <= l < len(grid) and 0 <= c < len(grid[0])) else False

def get_grid_pos(coord):
    return int(ControlValue((coord[0] * cf.grid_factor) // vr.win_width, 0, len(vr.grid) - 1)), int(ControlValue((coord[1] * cf.grid_factor) // vr.win_width, 0, len(vr.grid[0]) - 1))

def get_grid_neighbors(l, c):
    pot_pos = [(l, c), (l-1, c), (l-1, c+1), (l, c+1), (l+1, c+1), (l+1, c), (l+1, c-1), (l, c-1), (l-1, c-1)]
    neighbors = []
    for pos in pot_pos:
        if 0 <= pos[0] < len(vr.grid) and 0 <= pos[1] < len(vr.grid[1]):
            neighbors += vr.grid[pos[0]][pos[1]]
    return neighbors

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

