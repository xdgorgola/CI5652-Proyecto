from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeAlias

import numpy as np
import scipy.sparse
import scipy.io

Graph_MTX: TypeAlias = np.ndarray | scipy.sparse.coo_matrix
def read_mtx(path: str) -> Graph_MTX:
    mtx = scipy.io.mmread(path)
    return mtx

class Graph(ABC):
    @abstractmethod
    def __init__(self, mtx_repr: Graph_MTX) -> None:
        self.vertex_count: int = mtx_repr.shape[0]
        self.edges: list[tuple[int, int]] = []
        self.set_edges()
    
    @abstractmethod
    def edge_count(self) -> int:
        """
            Calculates the amount of edges in the graph

        Returns:
            int: Amount of edges in the graph
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_neighboors(self, vertex: int) -> list[int]:
        """
            Gets the neighboors of a vertex in the graph

        Args:
            vertex (int): Vertex id

        Returns:
            list[int]: List of ids of the neighbooring vertices
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_degree(self, vertex: int) -> int:
        """
            Calculates the degree of a vertex in the graph

        Args:
            vertex (int): Vertex to calculate the degree for

        Returns:
            int: Degree of the vertex
        """
        raise NotImplementedError

    @abstractmethod
    def set_edges(self):
        """
            Intended to run on super the constructor.
            Sets the property self.edges
        """
        raise NotImplementedError


class AdjacencyDictGraph(Graph):
    def __init__(self, mtx_repr: Graph_MTX) -> None:
            self.grp: dict[int, list[int]] = {}
            nze = mtx_repr.nonzero()
            for nd in range(len(nze[0])):
                a: int = nze[0][nd]
                b: int = nze[1][nd]

                if not a in self.grp:
                    self.grp[a] = []
                if not b in self.grp:
                    self.grp[b] = []

                self.grp[a].append(b)
                self.grp[b].append(a)
            super().__init__(mtx_repr)

    def edge_count(self) -> int:
        return len(self.edges)

    def get_neighboors(self, vertex):
        #assert(vertex in self.grp)
        return self.grp[vertex]
    
    def get_degree(self, vertex: int) -> int:
        #assert(vertex in self.grp)
        return len(self.grp[vertex])
    
    def set_edges(self):
        checked: set[int] = set()
        for v in range(0, self.vertex_count):
            adjs = self.grp[v]
            for a in adjs:
                if a in checked:
                    continue
                
                self.edges.append((v, a))
            checked.add(v)


def is_vc(vs: list[int], es: list[tuple[int, int]]) -> bool:
    """
        Determines if a set of vertices is a vertex cover for a
        list of vertices

    Args:
        vs (list[int]): Vertices of the vertex cover
        es (list[tuple[int, int]]): Edges to cover

    Returns:
        bool: True if VS is a vertex cover for ES
    """
    for v in vs:
        es = list(filter(lambda e: e[0] != v and e[1] != v, es))
    return len(es) == 0