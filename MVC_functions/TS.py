import sys
sys.path.append("..")

from utils.graph import *
from .utils.tools_MVC import *

def get_neighbors(g: Graph, C: set[int]) -> set[tuple[int, tuple[int]]]:
    neighbors: set[tuple[int, tuple[int]]] = set()
    for u in C:
        to_add: list[int] = []
        for v in g.get_neighboors(u):
            if v not in C:
                to_add.append(v)

        neighbors.add((u, tuple(to_add)))
                
    return neighbors

def tabu_search(g: Graph, max_iterations: int, tabu_list_size: int) -> set[int]:
    C: set[int]
    (C, _) = construct_vc(g)
    C_star: set[int] = type(C)(C)
    tabu_list: list = []

    for _ in range(max_iterations):
        neighbors: set[tuple[int, tuple[int]]] = get_neighbors(g, C)
        best_neighbor: tuple[int, tuple[int]] | None = None
        best_neighbor_fitness: float | int = float('inf')

        for neighbor in neighbors:
            neighbor_fitness: int = len(neighbor[1]) - 1
            if set(neighbor[1]).intersection(tabu_list) and neighbor_fitness >= best_neighbor_fitness:
                continue

            best_neighbor = neighbor
            best_neighbor_fitness = neighbor_fitness

        if best_neighbor is None:
            continue

        C.remove(best_neighbor[0])
        for v in best_neighbor[1]:
            C.add(v)

        tabu_list.append(best_neighbor[0])
        if len(tabu_list) > tabu_list_size:
            tabu_list.pop(0)

        if len(C) < len(C_star):
            C_star = type(C)(C)

    return C_star

