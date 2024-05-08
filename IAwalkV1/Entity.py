import config as cf
import vars as vr
import utils as u
import tools as t
import pygame as pg
from geometry import SolidLine
from math import cos
from random import random

class Particle:
    def __init__(self, coord, acc=(0, 0), radius=vr.particle_size, color=(250, 250, 250), static=False, mass=None, breakforce=0, force_id=None, ignore_list=()):
        self.id = u.getNewId() if force_id is None else force_id
        self.coord, self.vel, self.acc = coord, [0, 0], list(acc)
        self.prev_coord = self.coord
        self.radius, self.mass = radius, radius if mass is None else mass
        self.color, self.pressure = color, 0
        self.pos, self.last_pos = u.get_grid_pos(self.coord), u.get_grid_pos(self.coord)
        self.static = static
        self.breakforce = breakforce
        self.ignore_list = list(ignore_list)
        self._precision = 3

        vr.entities[self.id] = self
        vr.entities_list.append(self.id)
        vr.grid[self.pos[0]][self.pos[1]].append(self.id)

    def update(self):
        self.pos = u.get_grid_pos(self.coord)
        l, c = self.pos
        if self.pos != self.last_pos:
            l_, c_ = self.last_pos
            vr.grid[l_][c_].remove(self.id)
            vr.grid[l][c].append(self.id)
            self.last_pos = (l, c)

        if vr.gravity_mode == 'no':
            pass
        elif vr.gravity_mode == 'down':
            self.acc[1] += cf.gravity
        elif vr.gravity_mode == 'right-middle':
            self.acc[0] += cf.gravity
            self.acc[1] += cf.gravity if self.coord[1] < vr.win_height/2 else -cf.gravity
        elif vr.gravity_mode == 'central':
            self.acc = t.Vmult(t.Vdiff(vr.middle, self.coord), 1)
        elif vr.gravity_mode == 'extern':
            self.acc = t.Vmult(t.Vdiff(vr.middle, self.coord), -1)
        elif vr.gravity_mode == 'right':
            self.acc[0] += cf.gravity
        elif vr.gravity_mode == 'left':
            self.acc[0] += -cf.gravity
        elif vr.gravity_mode == 'up':
            self.acc[1] += -cf.gravity
        elif vr.gravity_mode == 'cursor':
            self.acc = t.Vmult(t.Vdiff(vr.cursor, self.coord), cf.gravity / max(0.1, t.norm(t.Vdiff(vr.cursor, self.coord))))

        self.acc = t.Vcl(1, self.acc, (self.mass * 0.05) / (8 * vr.dt), self.vel) # Inertia

        if cf.collision:
            collision_correction = [0, 0]
            collision_intensity = 0
            for i in range(self._precision):
                for entity_id in u.get_grid_neighbors(l, c):
                    if entity_id in self.ignore_list:
                        continue
                    entity = vr.entities[entity_id]
                    dist = t.norm(t.Vdiff(self.coord, entity.coord))
                    if dist < self.radius + entity.radius and dist != 0:
                        corr = t.Vmult(t.Vdiff(self.coord, entity.coord), (entity.mass * ((self.radius + entity.radius) - dist)) / (8 * self._precision * dist * self.mass))
                        collision_intensity += t.norm(corr)
                        corr = t.Vcl(1, corr, -1 * cf.viscosity * vr.dt, t.Vdiff(self.vel, entity.vel))
                        collision_correction = t.Vadd(collision_correction, corr)
                for geo_id in vr.geo:
                    if geo_id in self.ignore_list:
                        continue
                    geo = vr.geo[geo_id]
                    if geo.Touched(self.coord, delta=self.radius):
                        geo.update(self.id)
                        corr = t.Vmult(geo.getNormal(above=geo.isAbove(self.coord)), -0.1 * (self.radius - geo.distance(self.coord)))
                        collision_correction = t.Vadd(collision_correction, corr)
                        collision_intensity += t.norm(corr)
                if self.static is False:
                    self.coord = t.Vadd(self.coord, collision_correction)
            self.pressure = collision_intensity / self._precision

        if self.static is False:
            prev_coord = self.coord[:]
            self.coord = t.Vcl(1, self.coord, -0.5 * vr.dt * (self.pressure + 0.01), self.vel)
            self.coord = t.Vcl(1, self.coord, -0.01 * vr.dt * self.breakforce, self.vel)
            if vr.mode == 'circle':
                self.coord, _ = u.KeepInMiddle(t.Vcl(1, t.Vcl(2, self.coord, -1, self.prev_coord), 0.75 * vr.dt * vr.dt, self.acc), delta=self.radius, radius=vr.circle_radius)
            elif vr.mode == 'rectangle':
                self.coord, corrected = u.KeepInSquare(t.Vcl(1, t.Vcl(2, self.coord, -1, self.prev_coord), 0.75 * vr.dt * vr.dt, self.acc), delta=self.radius, dimension=vr.rect_size)
                if corrected:
                    self.coord = (self.prev_coord[0], self.coord[1])
            elif vr.mode == 'corridor':
                self.coord, _ = u.KeepInHeight(t.Vcl(1, t.Vcl(2, self.coord, -1, self.prev_coord), 0.75 * vr.dt * vr.dt, self.acc), delta=self.radius, height=vr.corridor_height)
            else:
                self.coord, _ = u.KeepInWin(t.Vcl(1, t.Vcl(2, self.coord, -1, self.prev_coord), 0.75 * vr.dt * vr.dt, self.acc), delta=self.radius)
            self.prev_coord = prev_coord

            self.acc = [0, 0]

            self.vel = t.Vcl(1/vr.dt, self.coord, -1/vr.dt, self.prev_coord)
            if vr.slow_mo:
                self.coord = t.Vcl(1, self.coord, -1 * vr.slow_factor * vr.dt, self.vel)
        elif self.coord != self.prev_coord: # keep Static
            self.coord = self.prev_coord[:]

        if u.isInWindow(self.coord) is False:
            vr.grid[l][c].remove(self.id)
            vr.entities_list.remove(self.id)
            del vr.entities[self.id]

    def setCoord(self, coord):
        if self.static is False:
            self.coord = coord

    def draw(self):
        #r = min(255, max(0, self.pressure * 255))
        #self.color = (r, 255 - r, 255 - r)

        pg.draw.circle(vr.window, self.color, self.coord, self.radius)

    def on_delete(self):
        try:
            del vr.entities[self.id]
            vr.entities_list.remove(self.id)
            vr.grid[self.pos[0]][self.pos[1]].remove(self.id)
        except:
            pass

class Link:
    def __init__(self, particle_1, particle_2, static=(False, False), flex=0., independant=True, range=1., color=None):
        self.id = u.getNewId()
        if independant:
            vr.entities[self.id] = self
            vr.entities_list.append(self.id)

        self.p1 = particle_1
        self.p2 = particle_2
        self.p1.static, self.p2.static = static[0], static[1]
        self.length, self.base_length = t.norm(t.Vdiff(self.p2.coord, self.p1.coord)), t.norm(t.Vdiff(self.p2.coord, self.p1.coord))
        self.length_range = (self.length * (1 - range), self.length * range)
        self.flex = flex
        self.tension = 0
        self._precision = 2
        self.max_tension = 4
        self.color = color

    def update(self, precision=None):
        self.length = min(max(self.length, self.length_range[0]), self.length_range[1])
        if self.tension > self.max_tension * 0.5:
            self.length += (self.base_length - self.length) * 0.2
        tension = 0
        for i in range(self._precision if precision is None else precision):
            diff = t.Vdiff(self.p2.coord, self.p1.coord)
            v_unit = t.Vmult(diff, 1 / max(1, t.norm(diff)))
            delta_length = t.norm(diff) - self.length
            tension += abs(delta_length)

            self.p1.setCoord(t.Vcl(1, self.p1.coord, delta_length / (2 + self.flex), v_unit))
            self.p2.setCoord(t.Vcl(1, self.p2.coord, -1 * delta_length / (2 + self.flex), v_unit))

        self.tension = min(1., max(0., (tension / self._precision) / self.max_tension))

    def draw(self):
        color = self.color if self.color is not None else u.rgb(255 * self.tension, 255 * (1 - self.tension), 255)
        pg.draw.line(vr.window, color, self.p1.coord, self.p2.coord, width=2)

    def on_delete(self):
        self.p1.on_delete()
        self.p2.on_delete()
        try:
            del vr.entities[self.id]
            vr.entities_list.remove(self.id)
        except:
            pass

class SolidLink:
    def __init__(self, a=(0, 0), b=(1, 1), p_start=None, p_end=None, radius=vr.particle_size * 0.5, anchored=(False, False), independant=True):
        self.id = u.getNewId()
        if independant is True:
            vr.entities[self.id] = self
            vr.entities_list.append(self.id)

        if p_start is not None:
            a = p_start.coord
            p_start.radius = radius

        self.length = t.norm(t.Vdiff(a, b))
        self.solid_line = SolidLine(a, b, static=True)

        self.p1 = p_start if p_start is not None else Particle(a, radius=radius, static=anchored[0])
        self.p2 = p_end if p_end is not None else Particle(b, radius=radius, static=anchored[0])

        self.solid_line.ignore_list.append(self.p1.id)
        self.solid_line.ignore_list.append(self.p2.id)
        self.p1.ignore_list.append(self.solid_line.id)
        self.p2.ignore_list.append(self.solid_line.id)

        self.link = Link(self.p1, self.p2, independant=False)
        self.link.p1.static = anchored[0]
        self.link.p2.static = anchored[1]

        self._precision = 4

    def update(self):

        self.link.update()

        self.solid_line.a = self.p1.coord[:]
        self.solid_line.b = self.p2.coord[:]

    def draw(self):
        self.link.draw()

    def on_delete(self):
        try:
            del vr.entities[self.id]
            vr.entities_list.remove(self.id)
        except:
            pass

class Polygone:
    def __init__(self, particles, radius=vr.particle_size * 0.5, anchored=False, color=None):
        self.id = u.getNewId()
        vr.entities[self.id] = self
        vr.entities_list.append(self.id)

        self.particles = particles

        self.links = []
        for i in range(len(self.particles)):
            p1, p2 = self.particles[i-1], self.particles[i]
            self.particles.append(p1)
            self.particles.append(p2)
            link = Link(p1, p2, independant=False, range=1.5, color=color)
            self.links.append(link)

        self._precision = 4

    def update(self):
        for link in self.links:
            link.update(precision=self._precision)

    def draw(self):
        for link in self.links:
            link.draw()

    def on_delete(self):
        for link in self.links:
            link.on_delete()
        try:
            del vr.entities[self.id]
            vr.entities_list.remove(self.id)
        except:
            pass

class Body:
    def __init__(self, pulsation=None, amplitudes=None, phase=None, color=None):
        self.id = u.getNewId()
        vr.entities[self.id] = self
        vr.entities_list.append(self.id)

        self.life_time = 0

        left_foot, right_foot = Particle(t.Vadd(cf.start_pos, (-35, 60))), Particle(t.Vadd(cf.start_pos, (35, 60)))
        left_knee_ext, right_knee_ext = Particle(t.Vadd(cf.start_pos, (-45, 30)), radius=6), Particle(t.Vadd(cf.start_pos, (45, 30)), radius=6)
        left_knee_int, right_knee_int = Particle(t.Vadd(cf.start_pos, (-25, 30)), radius=4), Particle(t.Vadd(cf.start_pos, (25, 30)), radius=4)
        body_down, body_up = Particle(t.Vadd(cf.start_pos, (0, 10))), Particle(t.Vadd(cf.start_pos, (0, -40)))
        left_hip, right_hip = Particle(t.Vadd(cf.start_pos, (-15, -10))), Particle(t.Vadd(cf.start_pos, (15, -10)))
        shoulder_left, shoulder_right = Particle(t.Vadd(cf.start_pos, (-20, -55))), Particle(t.Vadd(cf.start_pos, (20, -55)))
        hand_left, hand_right = Particle(t.Vadd(cf.start_pos, (-35, 0))), Particle(t.Vadd(cf.start_pos, (35, 0)))

        left_leg_down, left_leg_up = [left_foot, left_knee_int, left_knee_ext], [left_knee_ext, left_knee_int, left_hip, body_down, left_knee_ext, left_hip]
        right_leg_down, right_leg_up = [right_foot, right_knee_int, right_knee_ext], [right_knee_ext, right_knee_int, right_hip, body_down, right_knee_ext, right_hip]
        body_left = [left_hip, shoulder_left, body_up]
        body_right = [right_hip, shoulder_right, body_up]
        left_arm = [hand_left, shoulder_left, body_up]
        right_arm =[hand_right, shoulder_right, body_up]
        hip = [left_hip, right_hip, body_down]

        self.body_poly = {"left_leg_up": left_leg_up, "right_leg_up": right_leg_up, "left_leg_down": left_leg_down, "right_leg_down": right_leg_down, "body_left": body_left, "body_right": body_right, "left_arm": left_arm, "right_arm": right_arm, "hip": hip}
        self.body = {}
        self.ids = []
        for key_poly in self.body_poly:
            for particule in self.body_poly[key_poly]:
                self.ids.append(particule.id)
        for key_poly in self.body_poly:
            for particule in self.body_poly[key_poly]:
                particule.ignore_list = particule.ignore_list + self.ids
                particule.color = color if color is not None else (250, 250, 250)
            self.body[key_poly] = Polygone(self.body_poly[key_poly], color=color)

        self.left_leg_links = [self.body["left_leg_up"].links[4], self.body["left_leg_up"].links[2]]
        self.right_leg_links = [self.body["right_leg_up"].links[4], self.body["right_leg_up"].links[2]]

        self.left_arm_links = [self.body["left_arm"].links[0]]
        self.right_arm_links = [self.body["right_arm"].links[0]]

        self.parts_links = [self.left_leg_links, self.right_leg_links, self.left_arm_links, self.right_arm_links]
        self.body_center = body_up
        self.body_center.color = (250, 0, 0)

        self.pulsations = pulsation if pulsation is not None else [[random() * 2 for i in range(len(part_links))] for part_links in self.parts_links]
        self.phase = phase if phase is not None else [[random() * 3.14 for i in range(len(part_links))] for part_links in self.parts_links]
        self.amplitudes = amplitudes if amplitudes is not None else [[(random() - random()) for i in range(len(part_links))] for part_links in self.parts_links]

    def update(self):
        self.life_time += vr.dt
        for p, part_link in enumerate(self.parts_links):
            for l, link in enumerate(part_link):
                link.length = link.base_length + link.base_length * self.amplitudes[p][l] * cos(self.pulsations[p][l] * self.life_time + self.phase[p][l])

        for key in self.body:
            self.body[key].update()

    def draw(self):
        for key in self.body:
            self.body[key].draw()

    def add_ignore_ids(self, ids):
        for key_poly in self.body_poly:
            for particule in self.body_poly[key_poly]:
                particule.ignore_list = particule.ignore_list + ids

    def on_delete(self):
        for poly_key in self.body:
            self.body[poly_key].on_delete()
        try:
            del vr.entities[self.id]
            vr.entities_list.remove(self.id)
        except:
            pass
