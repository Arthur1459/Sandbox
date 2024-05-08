import config as cf
import vars as vr
import utils as u
import tools as t
import pygame as pg

class SolidLine:
    def __init__(self, a, b, static=True):
        self.id = u.getNewId()

        self.a = a if a[0] < b[0] else b
        self.b = b if self.a == a else a
        self.static = static
        self.length = self.current_length()
        self.mass = self.current_length()/20
        self.ignore_list = []

        vr.geo[self.id] = self
        vr.geo_list.append(self.id)

    def getSeg(self):
        return u.makeSeg(self.a, self.b)

    def getNormal(self, above=True):
        dx = self.b[0] - self.a[0]
        dy = self.b[1] - self.a[1]
        normal = [-dy, dx] if above else [dy, -dx]
        return t.Vmult(normal, 1/max(t.norm(normal), 0.01))

    def Touched(self, pt, delta=5):
        return u.isInLine(self.a, self.b, pt, delta=delta)

    def isAbove(self, pt, delta=vr.particle_size * 3):
        t = u.distance(self.a, pt) / u.distance(self.a, self.b)
        seg_pt = self.getSeg()(t)
        if abs(self.a[0] - self.b[0]) > delta:
            if pt[1] < seg_pt[1]:
                return True
        else:
            if pt[0] < seg_pt[0]:
                return True
        return False

    def current_length(self):
        return abs(u.distance(self.a, self.b))

    def distance(self, pt):
        return abs(u.distance(self.a, pt) + u.distance(pt, self.b) - self.current_length())

    def update(self, id=None):
        if id is not None and id not in self.ignore_list:
            particle = vr.entities[id]
            if self.static is False:
                t_ = u.distance(self.a, particle.coord) / u.distance(self.a, self.b)
                point_on_seg = u.makeSeg(self.a, self.b)(t_)
                factor = abs(t_ - 1/2)
                v_normal = t.Vmult(t.Vcl(1, point_on_seg, -1, particle.coord), particle.mass/self.mass)
                norm = abs(particle.radius - t.norm(v_normal))
                middle = t.Vcl(1/2, self.a, 1/2, self.b)
                v_dir = t.Vcl(1, t.Vadd(point_on_seg, v_normal), -1, middle)
                v_dir_unit = t.Vmult(v_dir, 1/max(1, t.norm(v_dir)))
                self.a = t.Vcl(1, middle, factor * self.length / 2, v_dir_unit)
                self.b = t.Vcl(1, middle, -1 * factor * self.length / 2, v_dir_unit)

        #if not self.a[0] < self.b[0]:
        #   self.a, self.b = self.b, self.a

    def draw(self):
        if self.static is True:
            vr.seg_to_draw.append(self.getSeg())

