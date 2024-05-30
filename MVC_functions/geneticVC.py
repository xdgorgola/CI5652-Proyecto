from .utils.bitmask import Bitmask
from utils.graph import Graph, AdjacencyDictGraph, is_vc_alt, is_vc_gen_alt, read_mtx
from random import random, randint, shuffle
from time import time
import numpy as np

# Genotipo: Mascara de bits de 1 hasta cantidad de nodos
# Fenotipo: Vertices que conforman la cobertura minima
# Seria bueno saber cuantos ejes quedan por cubrir :think:
def fitness(a: Bitmask, g: Graph) -> int:
    (is_vc, cov_amnt) = is_vc_gen_alt(set(a.true_pos()), g)
    print(f"is_vc {is_vc} cov_amnt {cov_amnt} amount_set {a.amount_set}")
    return 2 * cov_amnt - a.amount_set - 5 * g.vertex_count * (1 - is_vc)


# ============== CRUCE ==============
def crossover(p1: Bitmask, p2: Bitmask, pi: int) -> tuple[Bitmask, Bitmask]:
    (o1, o2) = (Bitmask(p1.n), Bitmask(p1.n))
    for b in range(0, pi):
        o1[b] = p1[b]
        o2[b] = p2[b]

    for b in range(pi, p1.n):
        o1[b] = p2[b]
        o2[b] = p1[b]

    return (o1, o2)


def k_crossover(p1: Bitmask, p2: Bitmask, pi: list[int]) -> tuple[Bitmask, Bitmask]:
    (o1, o2) = (Bitmask(p1.n), Bitmask(p1.n))
    i, t = 0, 0
    for p in pi + [p1.n]:
        for b in range(i, p):
            o1[b] = p1[b] if t % 2 == 0 else p2[b]
            o2[b] = p2[b] if t % 2 == 0 else p1[b]
        i = p
        t = t + 1
    return (o1, o2)


def uniform_crossover(p1: Bitmask, p2: Bitmask) -> tuple[Bitmask, Bitmask]:
    (o1, o2) = (Bitmask(p1.n), Bitmask(p1.n))
    for b in range(0, p1.n):
        p = random()
        o1[b] = p1[b] if p <= 0.5 else p2[b]
        o2[b] = p2[b] if p <= 0.5 else p1[b]
    return (o1, o2)


# ============== MUTACION ==============
def uniform_mutation(p1: Bitmask, rate: float | None = None) -> Bitmask:
    o1: Bitmask = Bitmask(p1.n)
    chance: float = 1.0 / p1.n
    for b in range(0, p1.n):
        o1[b] = ~p1[b] if random() <= (rate if rate != None else chance) else p1[b]
    return o1


def invert_mutation(p1: Bitmask) -> Bitmask:
    return p1.inverse()


# ============== SELECCION DE PADRES ==============
# Sin replacement
def elitist_selection(cands: list[Bitmask], n: int, fit: list[int]) -> list[Bitmask]:
    return list(map(lambda r: r[1], sorted(enumerate(cands), key=lambda a: fit[a[0]], reverse=True)))[:min(n, len(cands))]


def roulette_selection(cands: list[Bitmask], n: int, fit: list[int], replace: bool = True) -> list[Bitmask]:
    r: list[Bitmask] = []
    tf: int = sum(map(abs,fit))
    i: int = 0
    while len(r) < n or len(r) == 0:
        if abs(fit[i]) / tf <= random():
            r.append(cands[i] if replace else cands.pop(i))
        i = (i + 1) % len(cands)
    return r

# ============== SUPERVIVENCIA DE POBLACION ==============
def worst_elimination(pop: list[Bitmask], offspring: list[Bitmask], fit: list[int]) -> list[Bitmask]:
    return list(map(lambda s: s[1], sorted(enumerate(pop), key=lambda a: fit[a[0]], reverse=True)))[:-len(offspring)] + offspring

# Con replacement
def tournament_selection(cands: list[Bitmask], n: int, t_size: int, g: Graph) -> list[Bitmask]:
    f: list[int] = [fitness(c, g) for c in cands]
    r: list[Bitmask] = []
    while len(r) < n:
        l = randint(0, len(cands) - t_size) # Cuidado, randint es inclusivo a la derecha...
        r.append(cands[np.argmax(f[l:l+t_size])])
    return r

# ============== POBLACION INICIAL ==============
def genetic_process(g: Graph, i_pop: int = 5, max_iters: int = 40, max_time: int = 300):
    pop: list[Bitmask] = [Bitmask(base=np.random.choice(a=[False, True], size=g.vertex_count).tolist()) for _ in range(i_pop)]
    start_time = time()
    i = 0
    while (i < max_iters and time() - start_time < max_time):
        pop_fit = list(map(lambda b: fitness(b, g), pop))
        parents = roulette_selection(pop, 2, pop_fit)
        offspring = list(map(lambda o: uniform_mutation(o), uniform_crossover(parents[0], parents[1])))
        offspring_fit = list(map(lambda b: fitness(b, g), offspring))
        pop = worst_elimination(pop, offspring, pop_fit)
        print(f"======== Generacion {i} ========")
        i = i + 1

# g = AdjacencyDictGraph(read_mtx("./res/ca-GrQc.mtx"))
# genetic_process(g, max_iters=10000)