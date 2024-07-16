import numpy as np
from utils.graph import Graph
from ..utils.tools_MVC import partial_construct_vc

class Bitmask():
    LAST_ID = 0

    def from_int_set(n: int, base: set[int]):
        barr = np.zeros((n,), dtype=bool)
        for v in base:
            barr[v] = True
        return Bitmask(n, barr.tolist())
    
    def __init__(self, n = None, base: list[bool] = None):
        self.id = Bitmask.LAST_ID + 1
        Bitmask.LAST_ID = Bitmask.LAST_ID + 1
        if base != None:
            self.mask = np.array(base, dtype=bool)
            self.n = self.mask.shape[0]
            self.amount_set = np.count_nonzero(self.mask)
            return
        
        if n == None:
            raise ValueError()
        
        self.mask = np.zeros(n, dtype=bool)
        self.n = n
        self.amount_set: int = 0
    
    def set_bit(self, bit): # bits starts from 0
        if self.mask[bit] == 0:
            self.amount_set = self.amount_set + 1
        self.mask[bit] = True

    def clear_bit(self, bit):
        if self[bit] == 1:
            self.amount_set = self.amount_set - 1
        self.mask[bit] = False

    def is_set(self, bit):
        return self.mask[bit]

    def inverse(self):
        a = Bitmask(self.mask.shape[0])
        a.mask = np.logical_not(self.mask)
        a.amount_set = np.count_nonzero(a.mask)
        return a
    
    def dist_to(self, b):
        return (self.mask != b.mask).sum()

    def xor(self, mask):
        return Bitmask(self.n, np.logical_xor(self.mask, mask.mask))
    
    def true_pos(self):
        return self.mask.nonzero()[0]
    
    def false_pos(self):
        return (self.mask == False).nonzero()[0]
    
    def to_list(self):
        return self.mask.nonzero()[0].tolist()
    
    def to_set(self):
        return set(self.to_list())
    
    def __getitem__(self, key):
        return self.is_set(key)
    
    def __setitem__(self, key, value):
        if not (isinstance(value, (bool, np.bool_))):
            raise ValueError()
        self.clear_bit(key) if not value else self.set_bit(key)

    def __str__(self) -> str:
        return ''.join(self.mask.astype(int).astype(str).tolist())
    
def generate_initial_pop(i_pop: int, g: Graph) -> list[Bitmask]:
    boolMask = [set(np.random.choice(a=[False, True], size=g.vertex_count).nonzero()[0]) for _ in range(i_pop)]
    return [Bitmask.from_int_set(g.vertex_count, partial_construct_vc(g, bm)) for bm in boolMask]