import numpy as np
from functools import reduce

class Bitmask():
    LAST_ID = 0
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
    
    def true_pos(self):
        return self.mask.nonzero()[0]
    
    def false_pos(self):
        return (self.mask == False).nonzero()[0]
    
    def to_set(self):
        return set(self.mask.nonzero()[0].tolist())
    
    def __getitem__(self, key):
        return self.is_set(key)
    
    def __setitem__(self, key, value):
        if not (isinstance(value, (bool, np.bool_))):
            raise ValueError()
        self.clear_bit(key) if not value else self.set_bit(key)

    def __str__(self) -> str:
        return ''.join(self.mask.astype(int).astype(str).tolist())