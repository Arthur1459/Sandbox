# Some useful functions

def s(x):
    return 1 if x >= 0 else -1

def inv(x, explode=1e-9):
    return 1/x if x != 0. else explode

def Vmult(v, coef):
    return [vi * coef for vi in v]

def Vadd(v1, v2):
    return [v1[i] + v2[i] for i in range(min(len(v1), len(v2)))]

def Vdiff(v1, v2):
    return [v1[i] - v2[i] for i in range(min(len(v1), len(v2)))]

def Vcl(l1, v1, l2, v2):
    return [l1 * v1[i] + l2 * v2[i] for i in range(min(len(v1), len(v2)))]

def VectsSum(vectors):
    return [sum([vectors[i][u] for i in range(len(vectors))]) for u in range(min([len(v) for v in vectors]))]

def norm(v):
    return sum([vi ** 2 for vi in v]) ** 0.5

def scalar(v1, v2, approx=False):
    sc = sum([v1[i] * v2[i] for i in range(min(len(v1), len(v2)))])
    return sc if approx is False else round(sc)

def vectorial(v1, v2):
    return [v1[1] * v2[2] - v1[2] * v2[1], v1[2] * v2[0] - v1[0] * v2[2], v1[0] * v2[1] - v1[1] * v2[0]]

def normalise(v):
    return Vmult(v, inv(norm(v)))

def moy(vector):
    return sum(vector) / len(vector) if len(vector) != 0 else 0

def ControlValue(value, a, b):
    if value < a:
        return a
    elif value > b:
        return b
    else:
        return value