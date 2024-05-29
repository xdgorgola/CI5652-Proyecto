import sys
sys.path.append("..")

from random import choice
from utils.graph import *
from .utils.tools_MVC import *
import time

def fastVC(g: Graph, cutoff: int) -> set[int]:
    """
    Calculates the minimum vertex cover of a graph with iterated local search.
    
    Args:
    ----------
    g: A graph to calculate its MVC

    cutoff: The maximun time allowed to calculate the MVC

    Return:
    -----------
    A set of vertices that correspond to the MVC
    """

    C: set[int]
    vloss: set[int]
    (C, vloss) = construct_vc(g)
    gain: dict[int, int] = {v: 0 for v in range(g.vertex_count) if v not in C}
    start_time: float = time.time()
    found_time: float | None = None

    while time.time() - start_time < cutoff:
        
        if is_vc_alt(C, g):
            found_time = time.time()
            C_star: set[int] = C.copy()
            min_loss_vertex: int = min(C, key=lambda v: vloss[v])
            C.remove(min_loss_vertex)
            continue

        u: int = ChooseRmVertex(C, vloss)
        C.remove(u)

        e: tuple[int, int] = choice([edge for edge in g.edges if edge[0] not in C and edge[1] not in C])
        v: int = e[0] if gain.get(e[0], 0) > gain.get(e[1], 0) else e[1]
        C.add(v)
        
        covered: list[int] = [edge for edge in g.edges if edge[0] in C or edge[1] in C]
        vertex_covered = {}
        for edge in covered:
            vertex_covered[edge[0]] = 1
            vertex_covered[edge[1]] = 1

        for n in g.get_neighboors(u):
            vloss[n] -= 1
            gain[n] = vertex_gain(g, n, vertex_covered)

        for n in g.get_neighboors(v):
            vloss[n] += 1
            gain[n] = vertex_gain(g, n, vertex_covered)

    return (C_star, found_time-start_time)