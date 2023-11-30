from numba import njit, uint64
import numpy as np
import timeit

# Increases linearly from 1 to 1,000,000:
PREDICTABLE_DATA = np.linspace(1, 1_000_000, 1_000_000, dtype=np.uint64)
# Shuffled randomly:
RANDOM_DATA = PREDICTABLE_DATA.copy()
np.random.shuffle(RANDOM_DATA)

#import llvmlite.binding as llvm
#llvm.set_option('', '--debug-only=loop-vectorize')


@njit
def naive_max(arr):
    result = arr.dtype.type(0)
    for value in arr:
        if value > result:
            result = value
    return result

naive_max(RANDOM_DATA)
print("naive", timeit.timeit("naive_max(RANDOM_DATA)", globals=globals(), number=1000))

@njit
def branchless(arr):
    dt = arr.dtype.type
    result = dt(0)
    for i in range(len(arr)):
        value = arr[i]
        result = value if value > result else result
    return result

branchless(RANDOM_DATA)
print("branchless", timeit.timeit("branchless(RANDOM_DATA)", globals=globals(), number=1000))
raise SystemExit()

@njit
def unrolled(arr):
    results = np.zeros((4,), dtype=arr.dtype)
    for i in range(len(arr) // 4):
        results[0] = arr[i * 4] if arr[i * 4] > results[0] else results[0]
        results[1] = arr[i * 4 + 1] if arr[i * 4 + 1] > results[1] else results[1]
        results[2] = arr[i * 4 + 2] if arr[i * 4 + 2] > results[2] else results[2]
        results[3] = arr[i * 4 + 3] if arr[i * 4 + 3] > results[3] else results[3]

    result = arr.dtype.type(0)

    # Combine the 4 values:
    for value in results:
        if value > result:
            result = value
    # Handle the tail of the array:
    for value in arr[-4:]:
        if value > result:
            result = value
    return result

print(unrolled(RANDOM_DATA))
print("unrolled", timeit.timeit("unrolled(RANDOM_DATA)", globals=globals(), number=1000))

@njit
def unrolled2(arr):
    results = np.zeros((4,), dtype=arr.dtype)
    for i in range(len(arr) // 4):
        results[:] = np.array([
            value if value > result else result
            for (value, result) in zip(arr[i * 4:(i+1) * 4], results)
        ])

    result = arr.dtype.type(0)

    # Combine the 4 values:
    for value in results:
        if value > result:
            result = value
    # Handle the tail of the array:
    for value in arr[-4:]:
        if value > result:
            result = value
    return result

print(unrolled2(RANDOM_DATA))
print("unrolled2", timeit.timeit("unrolled2(RANDOM_DATA)", globals=globals(), number=1000))
