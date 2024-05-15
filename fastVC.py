from utils.graph import *
from random import choice
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

    for i in range(k):
        r:int = choice(list(s))
        if f(r) < f(best):
            best = r
    
    return best

def ChooseRmVertex(C: set[int], vloss: list[int]) -> int:
    return BMS(C,50, lambda x: vloss[x])
    


g = AdjacencyDictGraph(read_mtx("./res/bio-yeast.mtx"))
(VC, l) = construct_vc(g)

print(ChooseRmVertex(VC, l))

