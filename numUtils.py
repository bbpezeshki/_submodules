import numpy as np

def orderOfLastNonZero(n):
    res = None
    nStr = np.format_float_positional(abs(n), trim='.')
    if nStr == "0.":
        res = 0.0
    elif nStr[-1] == '.': # |n| >= 1
        cntr = -2;
        while nStr[cntr] == '0':
            cntr -= 1;
        res = 10**(cntr * -1 - 2)
    else: # |n| < 1
        res = 10**(-(len(nStr)-2))
    return res
