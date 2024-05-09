from scipy.io import mmread

def mtex_to_adjs(path: str) -> dict[int, list[int]]:
    mtx = mmread(path)
    grp: dict[int, list[int]] = {}
    nze = mtx.nonzero()
    for nd in range(len(nze[0])):
        a: int = nze[0][nd]
        b: int = nze[1][nd]

        if not a in grp:
            grp[a] = []
        if not b in grp:
            grp[b] = []
        
        grp[a].append(b)
        grp[b].append(a)
    return grp