from timeit import timeit
from numba import njit
import numpy as np

@njit
def divide(n):
    total = 0
    for i in range(n):
        i = np.int32(i)
        total += i // 32
    return total

@njit
def shift(n):
    total = 0
    for i in range(n):
        i = np.int32(i)
        total += i >> 5
    return total

@njit(error_model="numpy")
def divide2(n):
    total = 0
    for i in range(n):
        i = np.int32(i)
        total += i // 32
    return total

assert divide(1000) == shift(1000)
assert divide(1000) == divide2(1000)

print("divide", timeit(lambda: divide(10_000)))
print("shift", timeit(lambda: shift(10_000)))
print("divide2", timeit(lambda: divide2(10_000)))
