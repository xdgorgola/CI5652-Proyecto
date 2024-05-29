import sys
sys.path.append("..")

from itertools import combinations
from utils.graph import *
from .utils.tools_MVC import *

def brute_mvc(g: Graph) -> list[int] | None:
    for i in range(0, g.vertex_count):
        ps = map(lambda p: p, combinations(range(g.vertex_count), i))
        for p in ps:
            print(p)
            if (is_vc_alt(set(p), g)):
                return p
    return None