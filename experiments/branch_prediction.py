import os
import time
#os.environ["NUMBA_LOOP_VECTORIZE"] = "0"
#os.environ["NUMBA_OPT"] = "0"
#os.environ["NUMBA_DUMP_OPTIMIZED"] = "1"
#from llvmlite import binding as llvm
#llvm.set_option("", "--debug-only=loop-vectorize")

from numba import njit
import numpy as np

# Increases linearly from 1 to 1,000,000:
PREDICTABLE_DATA = np.linspace(1, 1_000_000, 1_000_000, dtype=np.uint64)
# Shuffled randomly:
RANDOM_DATA = PREDICTABLE_DATA.copy()
np.random.shuffle(RANDOM_DATA)

from numba import float64, int64, uint32, uint64

@njit
def count_increasing_decreasing(arr):
    previous = 0
    increasing = uint32(0)
    unchanged = uint32(0)
    #assert len(arr) < 2 ** 31
    for i in range(len(arr)):
        value = arr[i]
        if value == previous:
            unchanged += 1
        elif value > previous:
            increasing += 1
        previous = value
    decreasing = uint32(len(arr) - increasing - unchanged)
    return increasing, unchanged, decreasing

print(count_increasing_decreasing([1, 2, 3, 2, 2, 4]))

@njit
def count_increasing_decreasing_avoid_conditionals(arr):
    previous = 0
    increasing = 0
    unchanged = 0
    for i in range(len(arr)):
        value = arr[i]
        unchanged += 1 if value == previous else 0
        increasing += 1 if value > previous else 0
        previous = value
    decreasing = len(arr) - increasing - unchanged
    return increasing, unchanged, decreasing

print(count_increasing_decreasing_avoid_conditionals([1, 2, 3, 2, 2, 4]))

from numba import uint64

@njit
def count_increasing_decreasing_avoid_conditionals_2(arr):
    previous = 0
    increasing = 0
    unchanged = 0
    for value in arr:
        unchanged += uint64(value == previous)
        increasing += uint64(value > previous)
        previous = value
    decreasing = len(arr) - increasing - unchanged
    return increasing, unchanged, decreasing

print(count_increasing_decreasing_avoid_conditionals_2([1, 2, 3, 2, 2, 4]))

if __name__ == '__main__':
    import sys
    if sys.argv[1] == "original":
        f = count_increasing_decreasing
    elif sys.argv[1] == "branchless":
        f = count_increasing_decreasing_avoid_conditionals
    else:
        assert sys.argv[1] == "branchless2"
        f = count_increasing_decreasing_avoid_conditionals_2
    if sys.argv[2] == "predictable":
        data = PREDICTABLE_DATA
    else:
        assert sys.argv[2] == "random"
        data = RANDOM_DATA
    f(data)
    start = time.time()
    for i in range(1000):
        f(data)
    print(time.time() - start)
