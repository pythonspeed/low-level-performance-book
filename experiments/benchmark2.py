from timeit import timeit
from numba import njit
import numpy as np

ARR = np.ones((1_00, 1_00), dtype=np.uint64)

@njit
def variant1(arr):
    total = 0
    for value in arr.ravel():
        total += value
    return total

@njit
def variant2(arr):
    total = 0
    arr = arr.ravel()
    for i in range(len(arr)):
        total += arr[i]
    return total

assert variant1(ARR) == variant2(ARR)

print("variant1", timeit(lambda: variant1(ARR)))
print("variant2", timeit(lambda: variant2(ARR)))
