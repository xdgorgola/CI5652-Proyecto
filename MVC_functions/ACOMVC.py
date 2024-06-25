import sys
sys.path.append("..")

import random
from utils.graph import *
import time

def travel_graph(g: Graph, source: int, pheromones: list[int]) -> set[int]:
    visited = [0 for _ in range(g.vertex_count)]
    visited[source] = 1

    cover: set[int] = set()
    cover.add(source)
    uncovered_edges: list[tuple[int, int]] = []

    for edge in g.edges:
        if edge[0] != source and edge[1] != source:
            uncovered_edges.append(edge)

    current: int = source
    while len(uncovered_edges) != 0:
        jumps_neighbors: list[int] = []
        jumps_values: list[float] = []

        for v in g.vertex_count:
            if not visited[v]:
                sediment = max(pheromones[v], 1e-5)
                value = (sediment**0.9 ) * (g.get_degree(v) **1.5) 
                jumps_neighbors.append(v)
                jumps_values.append(value)

        next_node = random.choices(jumps_neighbors, weights = jumps_values)[0]
        visited[next_node] = 1
        current = next_node
        cover.add(current)
        for uncovered_edge in uncovered_edges:
                if uncovered_edge[0] == next_node or uncovered_edge[1] == next_node:
                    uncovered_edges.remove(uncovered_edge)
    return cover

def ACO(g: Graph, 
        cutoff: int, 
        ant_count: int, 
        q: int | None = None, 
        degradation_factor: float = .9) -> set[int]:
    C: set[int] = set(range(g.vertex_count))
    C_star: set[int] = type(C)(C)
    pheromones: list[float] = [1e-2]*g.vertex_count

    start_time: float = time.time()
    if q is None:
        q = (3/4) * g.vertex_count

    while time.time() - start_time < cutoff:

        covers: list[set[int]] = [travel_graph(g, random.randint(0, g.vertex_count - 1), pheromones) for _ in range(ant_count)]
        covers.sort(key=lambda x: len(x))
        len_best_cover = len(covers[0])

        for cover in covers:
            delta: float = q/len_best_cover
            for v in cover:
                pheromones[v] += delta

        pheromones *= degradation_factor

        if len_best_cover < len(C_star):
            C_star = type(covers[0])(covers[0])

    return C_star