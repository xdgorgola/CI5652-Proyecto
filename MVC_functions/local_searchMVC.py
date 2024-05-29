import sys
sys.path.append("..")

from random import choice
from utils.graph import *
from .utils.tools_MVC import *
import time

def localSearchMVC(g: Graph, 
                   cutoff: int, 
                   max_iter: int = 60,
                   init_sol: tuple[set[int], list[int]] | None = None) -> set[int]:
    """
    Calculates the minimum vertex cover of a graph with local search.
    
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
    (C, vloss) = construct_vc(g) if init_sol is None else init_sol
    C_star: set[int] = type(C)(C)
    iter: int = 0

    start_time: float = time.time()
    found_time: float | None = None

    chosen_vertex: int | None = None
    R: list[int] | None = None
    N_R: list[int] | None = None
    while time.time() - start_time < cutoff:
        R = ChooseRemoveVertices(C, vloss)
        C.remove(R[0])
        C.remove(R[1])

        vloss[R[0]] = 0
        vloss[R[1]] = 0

        uncovered_edges: list[tuple[int, int]] = []
        
        for edge in g.edges:
            if edge[0] not in C and edge[1] not in C:
                uncovered_edges.append(edge)

        N_R = g.get_neighboors(R[0]) + g.get_neighboors(R[1])
        
        while len(uncovered_edges) != 0:
            chosen_vertex = choice(N_R)

            C.add(chosen_vertex)
            N_R.remove(chosen_vertex)

            for uncovered_edge in uncovered_edges:
                if uncovered_edge[0] == chosen_vertex or uncovered_edge[1] == chosen_vertex:
                    uncovered_edges.remove(uncovered_edge)
                    vloss[chosen_vertex] += 1 
        
        found_time = time.time()

        redundant_vertex: list[int] = [i for i in C if vloss[i] == 0]
        for n in redundant_vertex:
            C.remove(n)
            vloss[n] = 0

        if len(C) < len(C_star):
            C_star = type(C)(C)
            iter = 0
        else:
            iter += 1
            if iter == max_iter:
                break

    return (C_star, found_time-start_time)