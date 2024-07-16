from typing import Callable
from .utils.bitmask import Bitmask, generate_initial_pop
from utils.graph import Graph, AdjacencyDictGraph, is_vc_gen_alt
from .utils.tools_MVC import partial_construct_vc
from .graspMVC import partialGraspMVC
from random import *
from time import time
from math import inf


COV_AMNT_W = 2.0
AMOUNT_SET_W = 1.0
NOT_VC_W = 3.0

# Genotipo: Mascara de bits de 1 hasta cantidad de nodos
# Fenotipo: Vertices que conforman la cobertura minima

def heuristic_to_bitmask(a: Bitmask, g: Graph) -> Bitmask:
    return Bitmask.from_int_set(g.vertex_count, partial_construct_vc(g, set(a.true_pos())))

def patrick_fitness(a: Bitmask, g: Graph) -> int:
    (is_vc, cov_amnt) = is_vc_gen_alt(set(a.true_pos()), g)
    return COV_AMNT_W * cov_amnt - AMOUNT_SET_W * a.amount_set - NOT_VC_W * g.edge_count() * (1 - is_vc)

def random_fragmentation(m: Bitmask, take: int) -> Bitmask:
    if (take > m.n):
        take = m.n

    return Bitmask.from_int_set(m.n, set(sample(m.to_list(), take)))

def patrick_star(
        g: Graph, 
        star_max_time: float, 
        rec_max_time: float, 
        init_amnt: int, 
        max_pob: int, 
        surv_pob: int, 
        frag_fact: int, 
        fitness_f: Callable[[Bitmask], float], 
        frag_f: Callable[[Bitmask], Bitmask], 
        rec_f: Callable[[Bitmask], Bitmask]) -> Bitmask:
    
    try:
        pob: list[Bitmask] = generate_initial_pop(init_amnt, g)
        init_time: float = time()
        best: Bitmask = pob[0]
        best_time: int = 0
        best_fitness: int = fitness_f(best)

        while (time() - init_time < star_max_time):
            while (len(pob) < max_pob):
                rec_pob: list[Bitmask] = []
                fra_pob: list[Bitmask] = []
                for bm in pob:
                    if (time() - init_time >= star_max_time):
                        break

                    print(f"Reconstruyendo individuo...")
                    reconstruccion = partialGraspMVC(g, bm.to_set(), rec_max_time)
                    if reconstruccion == set():
                       reconstruccion = heuristic_to_bitmask(bm, g)
                                        
                    rec_pob.append(Bitmask.from_int_set(g.vertex_count, reconstruccion))
                
                print(f"Fragmentando... Factor {frag_fact}")
                for i in rec_pob:
                    if (time() - init_time >= star_max_time):
                        break
                    print(f"Fragmentando nuevo individuo...")
                    for _ in range(frag_fact):
                        if (time() - init_time >= star_max_time):
                            break
                        print("Generada fragmentacion!")
                        fra_pob.append(frag_f(i))
                pob = rec_pob + fra_pob

            print("Podando...")
            fitness = map(lambda bm : fitness_f(bm), pob)
            sorted_by_fit = sorted(zip(pob, fitness), key=lambda z: z[1], reverse=True)
            pob = list(map(lambda i: i[0], sorted_by_fit[0:surv_pob]))
            if (best == None or sorted_by_fit[0][1] > best_fitness):
                best = sorted_by_fit[0][0]
                best_time = time()
                best_fitness = sorted_by_fit[0][1]

            print(f"Sobreviven {len(pob)}...")
    except Exception as e:
        print(e)
        pass
    finally:
        return (best, best_time, best_fitness)
