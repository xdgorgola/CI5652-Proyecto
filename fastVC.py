from utils.graph import *
from random import choice
import time
from collections.abc import Callable

def vertex_loss(vert: int, covered: list[tuple[int, int]]) -> int:
    v_loss: int = 0
    for edge in covered:
        if vert == edge[0] or vert == edge[1]:
            v_loss = v_loss + 1
    return v_loss


def vertex_gain(g: Graph, vert: int, covered: list[tuple[int,int]]) -> int:
    v_gain: int = 0
    neighboors = g.get_neighboors(vert)
    for n in neighboors + vert:
        gains: bool = True
        for edge in covered:
            if n == edge[0] or n == edge[1]:
                gains = False
                break
        if gains:
            v_gain = v_gain + 1

    return v_gain

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
        #Updatear adyacentes. Se les suma 1 a los vecinos pero no estoy claro si es en el grafo per se o en C?
        for n in g.get_neighboors(v):
            vloss[n] = vloss[n] + 1

    assert(is_vc(list(C), g.edges))
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
    


g = AdjacencyDictGraph(read_mtx("./res/bio-yeast.mtx"))
(VC, l) = construct_vc(g)

def fastVC(g: Graph, cutoff: int) -> set[int]:
    """
    Calculates the minimum vertex cover of a graph.
    
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
    start_time: time = time.time()

    while time.time() - start_time < cutoff:
        if is_vc(list(C), g.edges):
            C_star: set[int] = C.copy()
            min_loss_vertex: int = min(C, key=lambda v: vloss[v])
            C.remove(min_loss_vertex)
            continue

        u: int = ChooseRmVertex(C, vloss)
        C.remove(u)

        e: tuple[int, int] = choice([edge for edge in g.edges if edge[0] not in C and edge[1] not in C])
        v: int = e[0] if gain.get(e[0], 0) > gain.get(e[1], 0) else e[1]
        C.add(v)

        for n in g.get_neighboors(u):
            vloss[n] -= 1
            gain[n] = vertex_gain(g, n, [edge for edge in g.edges if edge[0] in C or edge[1] in C])

        for n in g.get_neighboors(v):
            vloss[n] += 1
            gain[n] = vertex_gain(g, n, [edge for edge in g.edges if edge[0] in C or edge[1] in C])

    return C_star

print(fastVC(g, 1000))