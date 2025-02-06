def float_compare(a, b):
    EPS = 1e-12

    if abs(a - b) < EPS:
        return 0
    if a < b:
        return -1
    return 1
