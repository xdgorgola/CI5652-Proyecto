from abc import ABC, abstractmethod
from __future__ import annotations
from typing import TypeAlias

import scipy
import scipy.io

Graph_MTX: TypeAlias = scipy.NDArray | scipy.sparse.coo_matrix
def read_mtx(path: str) -> Graph_MTX:
    mtx = scipy.io.mmread(path)
    return mtx


class Graph(ABC):
    @abstractmethod
    def __init__(self, mtx_repr: Graph_MTX) -> None:
        self.vertex_count: int = mtx_repr.shape[0]
    
    
    @abstractmethod
    def get_neighboors(self, vertex: int) -> list[int]:
        raise NotImplementedError
    
    @abstractmethod
    def get_degree(self, vertex: int) -> list[int]:
        raise NotImplementedError


class AdjacencyDictGraph(Graph):
    def __init__(self, mtx_repr: Graph_MTX) -> None:
            super.__init__()
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


    def get_neighboors(self, vertex):
        assert(vertex in self.grp)
        return self.grp[vertex]
    

    def get_degree(self, vertex: int) -> int:
        assert(vertex in self.grp)
        return len(self.grp[vertex])