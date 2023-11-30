import os
os.environ["NUMBA_LOOP_VECTORIZE"] = "0"

from numba import njit
import numpy as np

@njit
def generate_random_numbers_2(n):
    result = np.empty((n,), dtype=np.uint64)
    for i in range(n):
        random_number = (i * 437799614237992725) % (2 ** 61 - 1)
        result[i] = random_number
    return result

for i in range(5000):
    generate_random_numbers_2(1_000_000)
