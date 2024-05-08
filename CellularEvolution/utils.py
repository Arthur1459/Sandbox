import pygame as pg
import vars as vr
import config as cf
from random import randint, random
from Cells import Soil, Sprout, Cell, Roc
from math import exp

try:
    import colorama as cl
except ImportError:
    cl = None

def LogPrint(msg, func=None):
    if func is None:
        print(cl.Fore.YELLOW + str(msg) + cl.Style.RESET_ALL)
    else:
        print(cl.Fore.LIGHTYELLOW_EX + func.__name__ + " : " + cl.Fore.YELLOW + str(msg) + cl.Style.RESET_ALL)

def Text(msg, coord, color, size=None):  # blit to the screen a text
    TextColor = pg.Color(color) # set the color of the text
    if size is not None:
        font = pg.font.Font("ressources/pixel.ttf", size)  # set the font
    else:
        font = cf.default_font
    return vr.window.blit(font.render(msg, True, TextColor), coord)  # return and blit the text on the screen

def Proba(percentage):
    return rand(0, 100) < percentage

def control(value, bound=100):
    return min(bound, max(value, 0))

def getPos(coord):
    return coord[1] // vr.cell_size, coord[0] // vr.cell_size

def getCoord(pos):
    return pos[1] * vr.cell_size, pos[0] * vr.cell_size

def isValidPos(pos):
    line, col = pos
    if 0 <= line < cf.grid_line and 0 <= col < cf.grid_col:
        return True
    return False

def keepRGB(color):
    return [max(min(abs(color[0]), 250), 1), max(min(abs(color[1]), 250), 1), max(min(abs(color[2]), 250), 1)]

def getRndPos(soil_needed=False):
    if soil_needed is False:
        return randint(0, cf.grid_line - 1), randint(0, cf.grid_col - 1)
    else:
        l, c = randint(0, cf.grid_line - 1), randint(0, cf.grid_col - 1)
        return (l, c) if IsSoil((l, c)) else getRndPos(soil_needed=soil_needed)

def getRndPosAround(l, c, soil_needed=False, delta=1, rec=0):
    if rec > 50:
        return l, c
    l_, c_ = l + randint(-1 * delta, delta), c + randint(-1 * delta, delta)
    if not isValidPos((l_, c_)):
        return getRndPosAround(l, c, soil_needed=soil_needed, delta=delta, rec=rec+1)
    if soil_needed is False:
        return (l_, c_)
    else:
        return (l_, c_) if IsSoil((l_, c_)) else getRndPosAround(l, c, soil_needed=soil_needed, delta=delta, rec=rec+1)


def getRndRGB():
    return [randint(1, 250), randint(1, 250), randint(1, 250)]

def getInputs():
    keys = pg.key.get_pressed()
    vr.inputs["SPACE"] = True if keys[pg.K_SPACE] else False
    vr.inputs["ESCAPE"] = True if keys[pg.K_ESCAPE] else False
    vr.inputs["A"] = True if keys[pg.K_a] else False
    vr.inputs["Z"] = True if keys[pg.K_z] else False
    vr.inputs["E"] = True if keys[pg.K_e] else False
    vr.inputs["R"] = True if keys[pg.K_r] else False
    vr.inputs["Q"] = True if keys[pg.K_q] else False
    vr.inputs["S"] = True if keys[pg.K_s] else False

def rand(start, end):
    return start + (end - start) * random()

def rand1():
    return 1 if Proba(50) else -1

def CopyGrid(grid):
    return [[grid[line][col] for col in range(len(grid[line]))] for line in range(len(grid))]

def PrintGrid():
    print("\n")
    for line in range(cf.grid_line):
        print("|", end=' ')
        for col in range(cf.grid_col):
            cell = vr.grids[CurrentGrid()][line][col]
            print(str(cell.color), end=" ")
        print("|", end='\n')

def CurrentGrid():
    return vr.grid_index

def NextGrid():
    return (vr.grid_index + 1) % 2

def MakeRoc(pos, size=cf.roc_size):
    l, c = pos
    for line in range(size):
        if l + line >= cf.grid_line:
            continue
        for col in range(size):
            if c + col >= cf.grid_col:
                continue
            vr.grids[CurrentGrid()][l + line][c + col] = Roc()

# --------------- #
def NewTeam():
    vr.nb_teams += 1
    return vr.nb_teams

def MakeCluster(gen, team, max_size=20):
    l, c = getRndPos(soil_needed=True)
    team = NewTeam()
    for i in range(randint(1, max_size)):
        l, c = getRndPosAround(l, c, soil_needed=True, delta=1)
        vr.grids[CurrentGrid()][l][c] = Sprout(genetics=gen, team=team)

def getRndCellRGB():
    return [randint(30, 250), randint(30, 250), randint(30, 250)]

def NewSproutGen():
    move = rand(1, 99)
    replicate = rand(1, 99)
    reproduce = rand(1, 99)
    share = rand(1, 99)
    attack = rand(1, 99)
    soil_preference = rand(1, 99)
    friend_preference = rand(1, 99)
    attack_preference = rand(1, 99)
    new_gen = {'move': move, 'replicate': replicate,
               'share': share, 'attack': attack,
               'soil_preference': soil_preference,
               'friend_preference': friend_preference,
               'attack_preference': attack_preference,
               'reproduce': reproduce}
    return new_gen
def NewSproutGen_Altruist():
    move = rand(75, 99)
    replicate = rand(50, 99)
    reproduce = rand(50, 99)
    share = rand(75, 99)
    attack = rand(1, 30)
    soil_preference = rand(1, 1)
    friend_preference = rand(99, 99)
    attack_preference = rand(1, 30)
    new_gen = {'move': move, 'replicate': replicate,
               'share': share, 'attack': attack,
               'soil_preference': soil_preference,
               'friend_preference': friend_preference,
               'attack_preference': attack_preference,
               'reproduce': reproduce}
    return new_gen
def NewSproutGen_Selfish():
    move = rand(1, 99)
    replicate = rand(1, 75)
    reproduce = rand(1, 75)
    share = rand(1, 30)
    attack = rand(50, 99)
    soil_preference = rand(1, 99)
    friend_preference = rand(1, 50)
    attack_preference = rand(50, 99)
    new_gen = {'move': move, 'replicate': replicate,
               'share': share, 'attack': attack,
               'soil_preference': soil_preference,
               'friend_preference': friend_preference,
               'attack_preference': attack_preference,
               'reproduce': reproduce}
    return new_gen

def Mutation(genetic):
    new_gen = {}
    for key in genetic:
        new_gen[key] = max(0, min(100, genetic[key] + getMutation()))
    return new_gen

def getMutation(size=cf.mutation_size):
    return rand(-1 * size, size) * (1 + rand(-12, 12)**12/2e12)

def Reproduction(gen1, gen2, team):
    new_gen = {}
    for key in gen1:
        mutation = getMutation()
        new_gen[key] = max(0, min(100, (gen1[key] + gen2[key])/2 + mutation))
        if abs(mutation) > 5.8 * cf.mutation_size:
            team = NewTeam()
    return Sprout(genetics=new_gen, team=team)

def UpdtGeneralGen(new_gen):
    for key in vr.general_genetics:
        vr.general_genetics[key] = round(((vr.nb_entity - 1) * vr.general_genetics[key] + new_gen[key])/vr.nb_entity, 0)

# --------------- #
def GridSwitch(pos_from, pos_to):
    grid = vr.grids[CurrentGrid()]
    grid_next = vr.grids[NextGrid()]
    l1, c1 = pos_from
    l2, c2 = pos_to
    grid_next[l1][c1], grid_next[l2][c2] = grid[l2][c2], grid[l1][c1]

def GridStay(pos):
    l, c = pos
    grid = vr.grids[CurrentGrid()]
    grid_next = vr.grids[NextGrid()]
    grid_next[l][c] = grid[l][c]

def GridReplicate(origin, child):
    grid = vr.grids[CurrentGrid()]
    grid_next = vr.grids[NextGrid()]
    l1, c1 = origin
    l2, c2 = child
    grid_next[l1][c1], grid_next[l2][c2] = grid[l1][c1], grid[l1][c1].replicate()

def GridReproduce(parent_1, parent_2, child_pos):
    grid = vr.grids[CurrentGrid()]
    grid_next = vr.grids[NextGrid()]
    l1, c1 = parent_1
    l2, c2 = parent_2
    l, c =child_pos
    grid_next[l1][c1], grid_next[l][c] = grid[l1][c1], Reproduction(grid[l1][c1].genetics, grid[l2][c2].genetics, grid[l1][c1].team if not Proba(cf.traitor_proba) else NewTeam())

def GridDied(pos, team):
    l, c = pos
    grid_next = vr.grids[NextGrid()]
    grid_next[l][c] = Soil(energy=20)
    vr.nb_entity += -1
    vr.teams[team] = vr.teams[team] - 1

# --------------- #
def IsSoil(pos):
    line, col = pos
    grid = vr.grids[CurrentGrid()]
    return isinstance(grid[line][col], Soil)

def WhatTeam(pos):
    line, col = pos
    grid = vr.grids[CurrentGrid()]
    return grid[line][col].team

def getNeighborhood(pos) -> list[tuple[Cell | tuple]]:
    l, c = pos
    pot_neigh = [(l-1, c), (l-1, c+1), (l, c+1), (l+1, c+1), (l+1, c), (l+1, c-1), (l, c-1), (l-1, c-1)]
    neighbors = []
    for pot_pos in pot_neigh:
        if isValidPos(pot_pos):
            l_, c_ = pot_pos
            neighbors.append((vr.grids[CurrentGrid()][l_][c_], pot_pos))
    return neighbors

def isThereTeam(pos, team, exclude=()):
    neighbors = getNeighborhood(pos)
    for neighbor, pos in neighbors:
        if not isinstance(neighbor, Soil) and neighbor.team == team and (pos not in exclude):
            return True
    return False

def isThereEnemy(pos, team):
    neighbors = getNeighborhood(pos)
    for neighbor, pos in neighbors:
        if not isinstance(neighbor, Soil) and neighbor.team != team:
            return True
    return False
