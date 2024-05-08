import config as cf
import vars as vr
import tools as t
import utils as u
import pygame as pg


class Entity:
    def __init__(self):
        self.id = u.getNewId()

class Planet(Entity):
    def __init__(self, coord, speed=(0, 0), acceleration=(0, 0), mass=6e24, static=False):
        Entity.__init__(self)
        self.static = static
        self.coord = coord
        self.speed = speed
        self.acceleration = acceleration

        self.radius, self.mass = (mass / cf.mass_ref) ** 0.4, mass
        self.color = (255, 0, 0)

        self.grid_pos = u.get_grid_pos(self.coord)
        vr.grid[self.grid_pos[1]][self.grid_pos[0]].append(self.id)
        vr.entities[self.id] = self

    def update(self) -> None:
        self.acceleration = [0, 0]
        near_entities = self.get_near_entities()
        for entity_id in near_entities:
            self.acceleration = t.Vadd(self.acceleration, t.Vmult(self.gravitation_force(vr.entities[entity_id]), t.inv(self.mass)))

        self.acceleration = t.Vadd(self.acceleration, t.Vmult(self.side_force(), t.inv(self.mass)))
        self.acceleration = t.Vadd(self.acceleration, t.Vmult(self.god_force(), t.inv(self.mass)))

        if not self.static:
            self.speed = t.Vadd(self.speed, t.Vmult(self.acceleration, vr.dt))
            self.speed = t.Vmult(self.speed, cf.speed_loss)
            self.coord = u.KeepInWin(t.Vadd(self.coord, t.Vmult(self.speed, vr.dt)), delta=10)

        pos = tuple(self.grid_pos)
        self.grid_pos = u.get_grid_pos(self.coord)

        if pos != self.grid_pos:
            vr.grid[pos[1]][pos[0]].remove(self.id)
            vr.grid[self.grid_pos[1]][self.grid_pos[0]].append(self.id)

        n_forces = t.norm(self.acceleration)
        vr.n_acceleration = ((len(vr.entities_list) - 1) * vr.n_acceleration + n_forces) / len(vr.entities_list)

        self.color = (u.ControlValue(150 * n_forces / vr.n_acceleration, 0, 255), u.ControlValue(50 * (1 - n_forces / vr.n_acceleration), 0, 255), 50)

    def get_near_entities(self) -> list:
        col, line = self.grid_pos
        zones = [(line - 1, col - 1), (line - 1, col), (line - 1, col + 1),
                 (line, col - 1), (line, col), (line, col + 1),
                 (line + 1, col - 1), (line + 1, col), (line + 1, col + 1)]
        near_entities = []
        for l, c in zones:
            if u.isValidIndex(l, c, vr.grid):
                for entity_id in vr.grid[l][c]:
                    if entity_id != self.id:
                        near_entities.append(entity_id)
        return near_entities

    def gravitation_force(self, entity) -> list:
        signe = -1
        distance = t.norm(t.Vdiff(self.coord, entity.coord))
        if distance <= self.radius + entity.radius:
            signe = 1
            distance = max(distance, self.radius)
        F = signe * cf.G * self.mass * entity.mass * t.inv((distance * cf.d_factor) ** 2)
        return t.Vmult(t.Vdiff(self.coord, entity.coord), F * t.inv(t.norm(t.Vdiff(self.coord, entity.coord))))

    def side_force(self):
        side_projection = u.nearest_side_projection(self.coord)
        opposite_side = u.opposite_side(side_projection)
        F = cf.side_factor * cf.G * self.mass * self.mass * t.inv((t.norm(t.Vdiff(self.coord, side_projection)) * cf.d_factor) ** 2)
        return t.Vmult(t.Vdiff(opposite_side, self.coord), F * t.inv(t.norm(t.Vdiff(opposite_side, self.coord))))

    def god_force(self):
        distance = max(t.norm(t.Vdiff(self.coord, vr.cursor)), self.radius + 1)
        signe = 1 if pg.mouse.get_pressed(3)[0] else (-1 if pg.mouse.get_pressed(3)[2] else 0)
        F = cf.god_factor * signe * cf.G * self.mass * self.mass * t.inv((distance * cf.d_factor) ** 2)
        return t.Vmult(t.Vdiff(vr.cursor, self.coord), F * t.inv(t.norm(t.Vdiff(vr.cursor, self.coord))))

    def draw(self):
        pg.draw.circle(vr.window, self.color, self.coord, self.radius)
        if cf.full_debug:
            #u.Text(str(self.id), self.coord, 20, 'orange')
            pas = vr.win_width // cf.grid_factor
            u.drawSeg([(pas * self.grid_pos[0], pas * self.grid_pos[1]), (pas * self.grid_pos[0] + pas, pas * self.grid_pos[1])], 'yellow', 2)
            u.drawSeg([(pas * self.grid_pos[0] + pas, pas * self.grid_pos[1]), (pas * self.grid_pos[0] + pas, pas * self.grid_pos[1] + pas)], 'yellow', 2)
            u.drawSeg([(pas * self.grid_pos[0] + pas, pas * self.grid_pos[1] + pas), (pas * self.grid_pos[0], pas * self.grid_pos[1] + pas)], 'yellow', 2)
            u.drawSeg([(pas * self.grid_pos[0], pas * self.grid_pos[1] + pas), (pas * self.grid_pos[0], pas * self.grid_pos[1])], 'yellow', 2)
