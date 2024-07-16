from .utils.bitmask import Bitmask, generate_initial_pop
from utils.graph import Graph, AdjacencyDictGraph, is_vc_gen_alt
from .utils.tools_MVC import partial_construct_vc
from random import random
from time import time
from math import inf
import numpy as np

import sys
COV_AMNT_W = 2.0
AMOUNT_SET_W = 1.0
NOT_VC_W = 3.0

# Genotipo: Mascara de bits de 1 hasta cantidad de nodos
# Fenotipo: Vertices que conforman la cobertura minima

def heuristic_to_bitmask(a: Bitmask, g: Graph) -> Bitmask:
    return Bitmask.from_int_set(g.vertex_count, partial_construct_vc(g, set(a.true_pos())))

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

# ============== ALGORITMO MEMETICO ==============
def genetic_memetic_algorithm(g: Graph, i_pop: int = 5, mut_rate: float=None, max_iters: int = 40, max_time: int = 300):
    try:
        pop: list[Bitmask] = generate_initial_pop(i_pop, g)
        start_time = time()
        foundTime = None
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
                foundTime = time() - start_time
    finally:
        return (best, bestFit, foundTime)
    # Tiene pinta de que elitist y worst estan matando la diversidad!


def generate_initial_diverse_pop(i_pop: int, g: Graph, percentage_closeness: float) -> list[Bitmask]:

    bitMasks = []

    while len(bitMasks) < i_pop:

        new_bitmask = Bitmask(g.vertex_count, list(np.random.choice(a=[False, True], size=g.vertex_count)))
        
        append = True
        for bitMask in bitMasks:

            if new_bitmask.dist_to(bitMask) <= g.vertex_count * percentage_closeness:
                append = False
            
        if append:
            bitMasks.append(new_bitmask) 

    return bitMasks

def improve_pop(pop: list[Bitmask], g: Graph) -> list[Bitmask]:
    result = []
    for bitmask in pop:
        result.append(heuristic_to_bitmask(bitmask, g))
    
    return result


def build_distance_matrix(pop: list[Bitmask]) -> np.matrix:
    matrix = np.zeros((len(pop),len(pop)))
    for i in range(len(pop)):
        for j in range(i, len(pop)):
            matrix[i,j] = pop[i].dist_to(pop[j]) 
    
    return matrix + matrix.T

def calculate_goodness(pop: list[Bitmask], distance_matrix: np.matrix, n: int) -> list[float]:
    dip = []
    fsi = []
    for i in range(len(pop)):
        fila = distance_matrix[i,:]
        fila = np.delete(fila, i)
        dip.append(fila.min())
        fsi.append(len(set(pop[i].true_pos())))

    dip = np.array(dip)
    fsi = np.array(fsi)

    return fsi + np.exp((0.08 * n)/dip)

def pop_updating(pop: list[Bitmask], offspring: Bitmask, distance_matrix: np.matrix, n: int) -> tuple[list[Bitmask], np.matrix]:

    new_distances = np.array([offspring.dist_to(a) for a in pop])
    new_distance_matrix = np.append(distance_matrix, new_distances.reshape(1,len(pop)), axis=0)
    new_distance_matrix = np.append(new_distance_matrix, np.append(new_distances, 0).reshape(len(pop) + 1, 1), axis=1)
    new_pop = pop + [offspring]

    hip = calculate_goodness(new_pop, new_distance_matrix, n)
    
    maximum_hip = -inf
    maximum_s_index = -1
    for i, s in enumerate(new_pop):
        if maximum_hip < hip[i]:
            maximum_hip = hip[i]
            maximum_s_index = i
    
    if maximum_s_index != len(pop):
        new_distance_matrix = np.delete(new_distance_matrix, maximum_s_index, 0)
        new_distance_matrix = np.delete(new_distance_matrix, maximum_s_index, 1)    
        new_pop.pop(maximum_s_index)
    else:
        if np.random.uniform(0,1) < 0.2:
           
            maximum_hip = -inf
            maximum_s_index = -1
            for i, s in enumerate(new_pop):
                if i != len(pop) and  maximum_hip < hip[i]:
                    maximum_hip = hip[i]
                    maximum_s_index = i
            
            new_distance_matrix = np.delete(new_distance_matrix, maximum_s_index, 0)
            new_distance_matrix = np.delete(new_distance_matrix, maximum_s_index, 1)
            new_pop.pop(maximum_s_index)
        else:
            new_pop = pop
            new_distance_matrix = distance_matrix
    
    return (new_pop, new_distance_matrix)

def relinking_paths(pop: list[Bitmask], distance_matrix: np.matrix, best: Bitmask, bestfit: float, g:Graph,percentage: float) -> tuple[list[Bitmask], np.matrix, Bitmask, float]:
    sub_pop:list = list(np.random.choice(pop, round(len(pop) * percentage),replace=False))

    if len(sub_pop) % 2 != 0:
        sub_pop.pop()
    
    if len(sub_pop) == 0:
        return pop, distance_matrix

    permutation = list(np.random.choice(g.vertex_count, g.vertex_count, replace=False))

    while len(sub_pop) > 0:
        start, end = tuple(np.random.choice(sub_pop, 2, replace=False))

        for i in permutation:
            if start[i] == end[i]:
                continue
            
            if end[i] == False:
                start[i] = False
                if is_vc_gen_alt(set(start.true_pos()), g)[0] and  len(set(start.true_pos())) < bestfit:
                    pop, distance_matrix = pop_updating(pop, start, distance_matrix, g.vertex_count)
                    best = Bitmask.from_int_set(g.vertex_count, set(start.true_pos()))
                    bestfit = len(set(start.true_pos()))
            else:
                start[i] = True
        
        sub_pop.remove(start)
        sub_pop.remove(end)
    
    return pop, distance_matrix, best, bestfit


# ============== ALGORITMO MEMETICO DISPERSO ==============
def genetic_scatter_memetic_algorithm(g: Graph, i_pop: int = 5, max_iters: int = 40, max_time: int = 300):
    pop: list[Bitmask] = generate_initial_diverse_pop(i_pop, g, 0.25)
    pop = improve_pop(pop, g)

    best, bestFit, i = None, inf, 0
    distance_matrix: np.matrix = build_distance_matrix(pop)

    for bm in pop:
        if len(set(bm.true_pos())) < bestFit:
            bestFit = len(set(bm.true_pos()))
            best = bm
    
    start_time = time()
    while (i < max_iters and time() - start_time < max_time):
        s = time()
        parents_index = np.random.choice(len(pop), 5, replace=False)
        parents = [a for i, a in enumerate(pop) if i in parents_index]
        offspring = heuristic_to_bitmask(k_parents_crossover(parents), g)

        print(f"======== Generacion {i} ========")
        i = i + 1

        if len(set(offspring.true_pos())) < bestFit:
            bestFit = len(set(offspring.true_pos()))
            best = offspring

        pop, distance_matrix = pop_updating(pop, offspring, distance_matrix, g.vertex_count)

        # hacemos el reenlazado de caminos con el 30% de la población
        pop, distance_matrix, best, bestFit = relinking_paths(pop,distance_matrix,best, bestFit, g, 0.3)

        print(f"======== La Generacion {i} tardo: {time()-s}segs ========")

    
    return (best, bestFit)

if __name__ == "__main__":
    g = AdjacencyDictGraph("./res/ca-GrQc.mtx")
    genetic_memetic_algorithm(g, i_pop=10, mut_rate=0.005, max_iters=10000, max_time=60*10)
