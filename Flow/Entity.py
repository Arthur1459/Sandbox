import config as cf
import vars as vr
import utils as u
import tools as t
import pygame as pg
from geometry import SolidLine

class Particle:
    def __init__(self, coord, acc=(0, 0), radius=vr.particle_size, color=(250, 250, 250), static=False, mass=None, breakforce=0):
        self.id = u.getNewId()
        self.coord, self.vel, self.acc = coord, [0, 0], list(acc)
        self.prev_coord = self.coord
        self.radius, self.mass = radius, radius if mass is None else mass
        self.color, self.pressure = color, 0
        self.pos, self.last_pos = u.get_grid_pos(self.coord), u.get_grid_pos(self.coord)
        self.static = static
        self.breakforce = breakforce
        self.ignore_list = []
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
                self.coord, _ = u.KeepInSquare(t.Vcl(1, t.Vcl(2, self.coord, -1, self.prev_coord), 0.75 * vr.dt * vr.dt, self.acc), delta=self.radius, dimension=vr.rect_size)
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
        r = min(255, max(0, self.pressure * 255))
        self.color = (r, 255 - r, 255 - r)

        pg.draw.circle(vr.window, self.color, self.coord, self.radius)

    def on_delete(self):
        pass

class Link:
    def __init__(self, particle_1, particle_2, static=(False, False), flex=0., independant=True):
        self.id = u.getNewId()
        if independant:
            vr.entities[self.id] = self
            vr.entities_list.append(self.id)

        self.p1 = particle_1
        self.p2 = particle_2
        self.p1.static, self.p2.static = static[0], static[1]
        self.length = t.norm(t.Vdiff(self.p2.coord, self.p1.coord))
        self.flex = flex
        self.tension = 0
        self._precision = 2
        self.max_tension = 4

    def update(self):

        tension = 0
        for i in range(self._precision):
            diff = t.Vdiff(self.p2.coord, self.p1.coord)
            v_unit = t.Vmult(diff, 1 / max(1, t.norm(diff)))
            delta_length = t.norm(diff) - self.length
            tension += abs(delta_length)

            self.p1.setCoord(t.Vcl(1, self.p1.coord, delta_length / (2 + self.flex), v_unit))
            self.p2.setCoord(t.Vcl(1, self.p2.coord, -1 * delta_length / (2 + self.flex), v_unit))

        self.tension = min(1., max(0., (tension / self._precision) / self.max_tension))

    def draw(self):
        pg.draw.line(vr.window, u.rgb(255 * self.tension, 255 * (1 - self.tension), 255), self.p1.coord, self.p2.coord, width=3)

    def on_delete(self):
        pass

class Rope:
    def __init__(self, a=(0, 0), b=(10, 10), p_start=None, radius=vr.particle_size * 0.2, anchored=(False, False), flex=0.):
        self.id = u.getNewId()
        vr.entities[self.id] = self
        vr.entities_list.append(self.id)

        if p_start is not None:
            a = p_start.coord
            p_start.radius = radius
        self.length = t.norm(t.Vdiff(a, b))
        self.flex = flex
        seg = u.makeSeg(a, b)
        self.nb_particles = int(self.length / (2.1 * radius))
        self.particles = [p_start] if p_start is not None else []
        self.particles = self.particles + [Particle(seg(i / self.nb_particles), radius=radius, mass=8) for i in range(0 if p_start is None else 1, self.nb_particles)]
        self.links = [Link(p1, p2, flex=self.flex, independant=False) for p1, p2 in [(self.particles[i], self.particles[i + 1]) for i in range(len(self.particles) - 1)]]
        self.links[0].p1.static = anchored[0]
        self.links[-1].p2.static = anchored[1]

        self._precision = 4

    def update(self):
        for i in range(self._precision):
            for link in self.links:
                link.update()

    def draw(self):
        for link in self.links:
            link.draw()

    def on_delete(self):
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
        pass

class Polygone:
    def __init__(self, pts, radius=vr.particle_size * 0.5, anchored=False):
        self.id = u.getNewId()
        vr.entities[self.id] = self
        vr.entities_list.append(self.id)

        self.particles = []
        for pt in pts:
            self.particles.append(Particle(pt, static=anchored))
        self.solid_links = []

        for i in range(len(pts)):
            p1, p2 = self.particles[i-1], self.particles[i]
            self.particles.append(p1)
            self.particles.append(p2)
            solid_link = SolidLink(p_start=p1, p_end=p2, radius=radius, independant=False)
            self.solid_links.append(solid_link)

        self._precision = 4

    def update(self):
        for link in self.solid_links:
            link.update()

    def draw(self):
        for link in self.solid_links:
            link.draw()

    def on_delete(self):
        pass
