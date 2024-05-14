from itertools import permutations
from utils.graph import is_vc

def naive_mvc(nv: int, es: list[tuple[int, int]]) -> list[int] | None:
    for i in range(0, nv):
        ps = list(map(lambda p: list(p), permutations(range(nv), i)))
        for p in ps:
            #print(f'{p} {is_vc(p, es)}')
            if (is_vc(p, es)):
                return p
    return None

naive_mvc(5, [(0,1), (1,2), (2,3),(3,4),(4,0)])