from collections.abc import Callable
from itertools import combinations
from random import choice
from utils.graph import *

import time

def vertex_loss(vert: int, covered: list[tuple[int, int]]) -> int:
    v_loss: int = 0
    for edge in covered:
        if vert == edge[0] or vert == edge[1]:
            v_loss = v_loss + 1
    return v_loss


def vertex_gain(g: Graph, vert: int, vertex_covered: list[tuple[int,int]]) -> int:
    v_gain: int = 0
    neighboors = g.get_neighboors(vert)

    for n in neighboors + vert:
        gains: bool = True
        if vertex_covered.get(n) != None:
            gains = False
            break
        if gains:
            v_gain = v_gain + 1

    return v_gain


def brute_mvc(g: Graph) -> list[int] | None:
    for i in range(0, g.vertex_count):
        ps = map(lambda p: p, combinations(range(g.vertex_count), i))
        for p in ps:
            print(p)
            if (is_vc_alt(set(p), g)):
                return p
    return None


def construct_vc(g: Graph) -> tuple[set[int], list[int]]:
    """
        Creates a vertex cover for a graph using the following heuristic:


    Args:
        g (Graph): Graph to create vertex cover for

    Returns:
        tuple[set[int], list[int]]: Tuple containing
            - Set of vertices from the resulting vertex cover
            - Calculated loss of the vertices of the graph
    """
    C: set[int] = set()
    for e in g.edges:
        if e[0] in C or e[1] in C:
            continue

        C.add(e[0] if g.get_degree(e[0]) > g.get_degree(e[1]) else e[1])

    vloss: list[int] = [0 for _ in range(g.vertex_count)]
    for e in g.edges:
        if e[0] in C and e[1] in C:
            continue

        looser = e[0] if e[0] in C else e[1]
        vloss[looser] = vloss[looser] + 1
    
    for v in list(C):
        if vloss[v] != 0:
            continue
        C.remove(v)
        for n in g.get_neighboors(v):
            vloss[n] = vloss[n] + 1

    return (C, vloss)

def BMS(s: set[int], k: int, f: Callable[[int], int]) -> int:
    """
        Choose k elements randomly with replacement from the set S and 
        then return the best one, it selects the best one based on the 
        function f.

        Args:
        -----------
        s: A set of integers that represent vertices of a graph
        
        k: An integer that indicates how many times the function going 
           to select a random vertex of s
        
        f: A function f is a function such that we say an element is 
           better than another one if it has a smaller f value
        
        Return:
        -----------
        An integer that is a vertex of s
    """
    best: int = choice(list(s))

    for _ in range(k):
        r:int = choice(list(s))
        if f(r) < f(best):
            best = r
    return best


def ChooseRmVertex(C: set[int], vloss: list[int]) -> int:
    return BMS(C,50, lambda x: vloss[x])

def ChooseRemoveVertices(C: set[int], vloss: list[int]) -> list[int]:
    min_loss_vertex: int = min(C, key=lambda v: vloss[v])
    C.remove(min_loss_vertex)

    bms_vertex: int = BMS(C,50, lambda x: vloss[x])
    C.add(min_loss_vertex)

    return [min_loss_vertex, bms_vertex]

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