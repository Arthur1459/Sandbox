import pygame as pg
import vars as vr
import config as cf
import utils as u
from random import shuffle

class Cell:
    def __init__(self, empty=True, color=None):
        if empty:
            self.empty = True
            self.color = cf.cell_default_color
        else:
            self.empty = False
            self.color = tuple(u.getRndRGB()) if color is None else color
        return

    def update(self, current_pos):
        u.GridStay(current_pos)
        return

    def draw(self, current_pos):
        coord = u.getCoord(current_pos)
        pg.draw.rect(vr.window, self.color, (coord[0], coord[1], cf.cell_default_size, cf.cell_default_size))

    def replicate(self):
        return Cell(empty=self.empty, color=self.color)

class Soil(Cell):
    def __init__(self, energy=25):
        super().__init__(empty=True)
        self.team = 0
        self.energy_stored = energy
        self.color = (0, 200 * (self.energy_stored/100), 200 * (self.energy_stored/100))

    def update(self, current_pos):
        u.GridStay(current_pos)
        self.color = (0, 255 * (self.energy_stored / 100), 255 * (self.energy_stored / 100))
        self.energy_stored = min(self.energy_stored + cf.food_growth * vr.food_factor, 100)

class Roc(Cell):
    def __init__(self):
        super().__init__(empty=True)
        self.team = 0

        c = u.rand(10, 50)
        self.color = (c, c, c)

    def update(self, current_pos):
        u.GridStay(current_pos)

class Sprout(Cell):
    def __init__(self, energy=100, genetics=None, team=None):
        super().__init__(empty=False)
        self.genetics = u.NewSproutGen() if genetics is None else genetics

        self.team = u.NewTeam() if team is None else team
        if self.team in vr.teams:
            vr.teams[self.team] = vr.teams[self.team] + 1
        else:
            vr.teams[self.team] = 1
            vr.teams_colors[self.team] = u.getRndCellRGB()

        self.energy = energy
        self.color = self.updateColor()

        vr.nb_entity += 1
        u.UpdtGeneralGen(self.genetics)

    def update(self, current_pos):

        self.energy = max(min(self.energy, 255), 0)

        self.color = self.updateColor()

        if self.energy == 0:
            u.GridDied(current_pos, self.team)
            return

        self.energy -= cf.commun_energy_lost

        neighborhood = u.getNeighborhood(current_pos)
        shuffle(neighborhood)

        for neighbor, targeted_pos in neighborhood:
            if isinstance(neighbor, Roc):
                continue
            elif u.IsSoil(targeted_pos): # Land
                if u.Proba(self.genetics['soil_preference']) or (u.isThereTeam(targeted_pos, self.team, exclude=(current_pos)) and u.Proba(self.genetics['friend_preference'])) or (u.isThereEnemy(targeted_pos, self.team) and u.Proba(self.genetics['attack_preference'])):
                    if u.Proba(self.genetics['move']) > 10: # Move
                        self.energy += -1
                        self.energy += neighbor.energy_stored
                        neighbor.energy_stored = 0
                        u.GridSwitch(current_pos, targeted_pos)
                        return
                    elif u.Proba(self.genetics['replicate']) and self.energy > 20:
                            self.energy = self.energy * cf.replication_lost
                            u.GridReplicate(current_pos, targeted_pos)
                            return
            elif u.WhatTeam(targeted_pos) == self.team and u.Proba(self.genetics['friend_preference']): # Teammate
                if u.Proba((self.genetics['share'] + neighbor.genetics['share']) / 2):
                    energy = (self.energy + neighbor.energy) * 0.5
                    self.energy = energy
                    neighbor.energy = energy
                    return
                elif u.Proba(self.genetics['reproduce']) and self.energy > 20 and neighbor.energy > 20:  # Replicate
                    for cell, new_pos in neighborhood:
                        if u.IsSoil(new_pos):
                            self.energy = self.energy * cf.reproduction_lost
                            neighbor.energy = neighbor.energy * cf.reproduction_lost
                            u.GridReproduce(current_pos, targeted_pos, new_pos)
                            return
            elif u.WhatTeam(targeted_pos) != self.team and u.Proba(self.genetics['attack_preference']): # Potential Enemy
                if u.Proba(self.genetics['attack']):
                    self.energy = self.energy * cf.attack_lost
                    if self.energy - neighbor.energy > 0:
                        self.energy += neighbor.energy * cf.attack_recuperation
                        neighbor.energy = 0
                        u.GridSwitch(current_pos, targeted_pos)
                        return
                    else:
                        self.energy = 0
                        u.GridDied(current_pos, self.team)
                        return

        u.GridStay(current_pos)
        return

    def replicate(self):
        return Sprout(energy=self.energy, genetics=u.Mutation(self.genetics), team=self.team)

    def updateColor(self):
        if vr.mode == 'potential':
            return (max(min(255 * (self.energy / 100), 255), 0), 255 * (1 - self.genetics['move']/100), 255 * self.genetics['replicate']/100)
        elif vr.mode == 'selfish':
            return (255 * u.control(self.genetics['attack'] + self.genetics['attack_preference'] - self.genetics['friend_preference'])/100, 50, 50)
        elif vr.mode == 'altruist':
            return (50, 255 * u.control(self.genetics['friend_preference'] + self.genetics['share'] - self.genetics['attack'])/100, 50)
        elif vr.mode == 'team':
            return vr.teams_colors[self.team]
        else:
            return (max(min(255 * (self.energy / 100), 255), 0), 255 * (1 - self.genetics['move']/100), 255 * self.genetics['replicate']/100)
