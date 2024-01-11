from collections.abc import Iterable

def deleteListIndicesInRevSortedOrder(l, idx):
    if isinstance(idx, Iterable):
        idx = sorted(idx, reverse=True)
    else:
        idx = [idx]
    for i in idx:
        del l[i]

def rebuildListToOmitIndices(l, idx):
    if isinstance(idx, Iterable):
        idx = set(idx)
    else:
        idx = [idx]
    ll = [l[i] for i in range(len(l)) if i not in idx]
    return ll