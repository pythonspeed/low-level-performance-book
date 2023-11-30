from numba import njit, uint64
import numpy as np
import timeit

# Increases linearly from 1 to 1,000,000:
PREDICTABLE_DATA = np.linspace(1, 1_000_000, 1_000_000, dtype=np.uint64)
# Shuffled randomly:
RANDOM_DATA = PREDICTABLE_DATA.copy()
np.random.shuffle(RANDOM_DATA)
RANDOM_DATA2 = np.random.randint(0, 1_000_000, (1_000_000,), dtype=np.uint64)

#import llvmlite.binding as llvm
#llvm.set_option('', '--debug-only=loop-vectorize')


@njit(error_model="numpy")
def mean(x, y):
    out = np.empty(x.shape, dtype=np.float64)
    for i in range(x.shape[0]):
        out[i] = x.dtype.type(2) * (x[i] - y[i]) / (x[i] + y[i])
    return out

mean(RANDOM_DATA, RANDOM_DATA2)
print("mean", timeit.timeit("mean(RANDOM_DATA, RANDOM_DATA2)", globals=globals(), number=1000))

@njit
def mean2(arr1, arr2):
    assert arr1.shape == arr2.shape
    result = np.empty((len(arr1), ), dtype=np.float64)
    for i in range(len(arr1) // 4):
        i = uint64(i)
        for j in range(4):
            j = uint64(j)
            result[i * 4 + j] = (arr1[i * 4 +j] + arr2[i * 4 + j]) / 2
    return result

mean2(RANDOM_DATA, RANDOM_DATA2)
print("mean2", timeit.timeit("mean2(RANDOM_DATA, RANDOM_DATA2)", globals=globals(), number=1000))
raise SystemExit()

@njit
def branchless(arr):
    result = uint64(0)
    for i in range(len(arr)):
        value = arr[i]
        result = value if value > result else result
    return result

branchless(RANDOM_DATA)
print("branchless", timeit.timeit("branchless(RANDOM_DATA)", globals=globals(), number=1000))
raise SystemExit(0)

@njit
def unrolled(arr):
    results = np.zeros((4,), dtype=np.uint64)
    for i in range(len(arr) // uint64(4)):
        i = uint64(i)
        results[0] = arr[i * 4] if arr[i * 4] > results[0] else results[0]
        results[1] = arr[i * 4 + 1] if arr[i * 4 + 1] > results[1] else results[1]
        results[2] = arr[i * 4 + 2] if arr[i * 4 + 2] > results[2] else results[2]
        results[3] = arr[i * 4 + 3] if arr[i * 4 + 3] > results[3] else results[3]

    result = uint64(0)

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
#raise SystemExit(1)

@njit
def unrolled2(arr):
    results = np.zeros((4,), dtype=np.uint64)
    for i in range(len(arr) // 4):
        values = arr[i * 4:(i + 1) * 4]
        is_larger = values > results
        is_not_larger = ~is_larger
        results *= is_not_larger
        results += is_larger * values

    result = uint64(0)

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
