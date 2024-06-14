from .utils.bitmask import Bitmask
from utils.graph import Graph, AdjacencyDictGraph, is_vc_gen_alt
from .utils.tools_MVC import partial_construct_vc
from random import random
from time import time
from math import inf
import numpy as np

COV_AMNT_W = 2.0
AMOUNT_SET_W = 1.0
NOT_VC_W = 3.0

# Genotipo: Mascara de bits de 1 hasta cantidad de nodos
# Fenotipo: Vertices que conforman la cobertura minima

def heuristic_to_bitmask(a: Bitmask, g: Graph) -> Bitmask:
    return Bitmask.from_int_set(g.vertex_count, partial_construct_vc(g, set(a.true_pos())))

def generate_initial_pop(i_pop: int, g: Graph) -> list[Bitmask]:
    boolMask = [set(np.random.choice(a=[False, True], size=g.vertex_count)) for _ in range(i_pop)]
    return [Bitmask.from_int_set(g.vertex_count, partial_construct_vc(g, bm)) for bm in boolMask]


def fitness(a: Bitmask, g: Graph) -> int:
    """
    Fitness functions for the genotipes. This functions takes into acount
    the amount of edges covered by the genotipe, and tries to steer it to a 
    better solution by reducing the score depending on the amount of bits set
    in the bitmask or if the bitmask is not a vertex cover

    Args:
        a (Bitmask): Bitmask to evaluate
        g (Graph): Graph to calculate the minimum vertex cover

    Returns:
        int: Fitness value
    """
    (is_vc, cov_amnt) = is_vc_gen_alt(set(a.true_pos()), g)
    print(f"is_vc {is_vc} cov_amnt {cov_amnt} amount_set {a.amount_set}")
    return COV_AMNT_W * cov_amnt - AMOUNT_SET_W * a.amount_set #- NOT_VC_W * g.edge_count() * (1 - is_vc)


# ============== CRUCE ==============
def uniform_crossover(p1: Bitmask, p2: Bitmask, chance: float = 0.5) -> tuple[Bitmask, Bitmask]:
    """
    Uniform crossover. Every bit of p1 and p2 is swapped
    based on a probability

    Args:
        p1 (Bitmask): Genotipe 1 to cross
        p2 (Bitmask): Genotipe 2 to cross
        chance (float, optional): Chance of swapping. Defaults to 0.5.

    Returns:
        tuple[Bitmask, Bitmask]: Tuple of bitmask result of the crossover
    """
    (o1, o2) = (Bitmask(p1.n), Bitmask(p1.n))
    for b in range(0, p1.n):
        if (random() <= chance):
            o1[b] = p2[b]
            o2[b] = p1[b]
    return (o1, o2)


def uniform_crossover_alt(p1: Bitmask, p2: Bitmask, chance: float = 0.5) -> tuple[Bitmask, Bitmask]:
    """
    Uniform crossover. Every bit of p1 and p2 is swapped
    based on a probability independently

    Args:
        p1 (Bitmask): Genotipe 1 to cross
        p2 (Bitmask): Genotipe 2 to cross
        chance (float, optional): Chance of swapping. Defaults to 0.5.

    Returns:
        tuple[Bitmask, Bitmask]: Tuple of bitmask result of the crossover
    """
    (o1, o2) = (Bitmask(p1.n), Bitmask(p1.n))
    for b in range(0, p1.n):
        p = random()
        o1[b] = p1[b] if p <= chance else p2[b]
        o2[b] = p2[b] if p <= chance else p1[b]
    return (o1, o2)


def k_parents_crossover(ps: list[Bitmask]) -> Bitmask:
    o = Bitmask(ps[0].n)
    for b in range(ps[0].n):
        if not ps[0][b]:
            continue
        same = True
        for m in ps:
            if not m[b]:
                same = False
                break
        
        if not same:
            continue

        o[b] = True
    return o


# ============== MUTACION ==============
def uniform_mutation(p1: Bitmask, rate: float | None = None) -> Bitmask:
    """
    Switches bit by bit of p1 based on a probability

    Args:
        p1 (Bitmask): Genotipe to mutate
        rate (float | None, optional): Probability of mutation. Defaults to None.

    Returns:
        Bitmask: P1 mutated
    """
    o1: Bitmask = Bitmask(p1.n)
    chance: float = 1.0 / p1.n if rate == None else rate
    for b in range(0, p1.n):
        o1[b] = ~p1[b] if random() <= chance else p1[b]
    return o1
    

# ============== SELECCION DE PADRES ==============
# Sin replacement
def elitist_selection(cands: list[Bitmask], fit: list[int], n: int) -> list[Bitmask]:
    """
    Selects the n genotipes with the best fitness

    Args:
        cands (list[Bitmask]): Candidate genotipes
        fit (list[int]): Fitness of the genotipes
        n (int): Amount of genotipes to select

    Returns:
        list[Bitmask]: Result of the selection
    """
    return list(map(lambda r: r[1], sorted(enumerate(cands), key=lambda a: fit[a[0]], reverse=True)))[:min(n, len(cands))]

# ============== SUPERVIVENCIA DE POBLACION ==============
def worst_elimination(pop: list[Bitmask], fit: list[int], offspring: list[Bitmask]) -> list[Bitmask]:
    """
    Replaces the worst genotipes with the offspring of a generation

    Args:
        pop (list[Bitmask]): Population to select survivors
        fit (list[int]): Fitness of the population
        offspring (list[Bitmask]): Offspring of the generation

    Returns:
        list[Bitmask]: Surviving population
    """
    return list(map(lambda s: s[1], sorted(enumerate(pop), key=lambda a: fit[a[0]], reverse=True)))[:-len(offspring)] + offspring


# ============== ALGORITMO GENETICO ==============
def genetic_process(g: Graph, i_pop: int = 5, mut_rate: float=None, max_iters: int = 40, max_time: int = 300):
    """
    Genetic algorithm itself.

    Args:
        g (Graph): Graph to find MVC for
        i_pop (int, optional): Population sizes. Defaults to 5.
        mut_rate (float, optional): Mutation rate. Defaults to None.
        max_iters (int, optional): Max iteration. Defaults to 40.
        max_time (int, optional): Max running time. Defaults to 300.
    """
    pop: list[Bitmask] = [Bitmask(base=np.random.choice(a=[False, True], size=g.vertex_count).tolist()) for _ in range(i_pop)]
    start_time = time()
    best, bestFit, i = None, -inf, 0
    while (i < max_iters and time() - start_time < max_time):
        pop_fit = list(map(lambda b: fitness(b, g), pop))
        parents = elitist_selection(pop, pop_fit, 2)
        offspring = list(map(lambda o: uniform_mutation(o), uniform_crossover_alt(parents[0], parents[1])))
        offspring_fit = list(map(lambda b: fitness(b, g), offspring))
        pop = worst_elimination(pop, pop_fit, offspring)
        
        print(f"======== Generacion {i} ========")
        i = i + 1
        gb = max(zip(pop + offspring, pop_fit + offspring_fit), key=lambda t: t[1])
        if gb[1] > bestFit:
            best = gb[0]
            bestFit = gb[1]
             
    return (best, bestFit)


def genetic_memetic_algorithm(g: Graph, i_pop: int = 5, mut_rate: float=None, max_iters: int = 40, max_time: int = 300):
    pop: list[Bitmask] = generate_initial_pop(i_pop, g)
    start_time = time()
    best, bestFit, i = None, -inf, 0
    while (i < max_iters and time() - start_time < max_time):
        pop_fit = list(map(lambda b: fitness(b, g), pop))
        parents = elitist_selection(pop, pop_fit, 3)
        offspring = [heuristic_to_bitmask(uniform_mutation(k_parents_crossover(parents), mut_rate), g)]
        offspring_fit = [fitness(offspring[0], g)]
        pop = worst_elimination(pop, pop_fit, offspring)
        
        print(f"======== Generacion {i} ========")
        i = i + 1
        gb = max(zip(pop + offspring, pop_fit + offspring_fit), key=lambda t: t[1])
        if gb[1] > bestFit:
            best = gb[0]
            bestFit = gb[1] 

    return (best, bestFit)
    # Tiene pinta de que elitist y worst estan matando la diversidad!

if __name__ == "__main__":
    g = AdjacencyDictGraph("./res/ca-GrQc.mtx")
    genetic_memetic_algorithm(g, i_pop=10, mut_rate=0.005, max_iters=10000, max_time=60*10)
