import numpy
from py_perf_event import measure, Cache, CacheId, CacheOp, CacheResult
from contextlib import contextmanager
from subprocess import Popen
from os import getpid
from signal import SIGINT
from time import sleep, time
from resource import getrusage, RUSAGE_SELF
from numba import njit
import numpy as np

events = [
    "instructions",
    "cache-references",
    "cache-misses",
    "avx_insts.all",
]

data = np.ones((100_000_000,), dtype=np.uint8)

@njit
def scan_memory(data, multiplier):
    index = 0
    for _ in range(1_000_000):
        data[index] += 1
        index = (multiplier * index + 1) % len(data)
    return data[0]

LINEAR = 1
RANDOM = 22695477

scan_memory(data, LINEAR)


@contextmanager
def perf():
    """Benchmark this process with Linux's perf util."""
    p = Popen(["perf", "stat", "-e", "l1d-loads,l1d-misses,LLC-loads,LLC-misses,LLC-prefetch", "-p", str(getpid())])
    # Ensure perf has started before running more code.
    # This will add ~0.1 to the elapsed time reported by perf,
    # so we also track elapsed time separately.
    sleep(1)
    start = time()
    try:
        yield
    finally:
        sleep(1)
        p.send_signal(SIGINT)

import sys
if sys.argv[1] == "perf":
    with perf():
        scan_memory(data, LINEAR)

    with perf():
        scan_memory(data, RANDOM)
else:
    access, miss, access2, miss2 = measure([Cache(CacheId.LL, CacheOp.READ, CacheResult.ACCESS), Cache(CacheId.LL, CacheOp.READ, CacheResult.MISS),
                                        Cache(CacheId.L1D, CacheOp.READ, CacheResult.ACCESS), Cache(CacheId.L1D, CacheOp.READ, CacheResult.MISS)], scan_memory, data, LINEAR)
    print("LL ACCESS:", access)
    print("LL MISS:  ", miss)
    print("L1D ACCESS:", access2)
    print("L1D MISS:  ", miss2)

    access, miss, access2, miss2 = measure([Cache(CacheId.LL, CacheOp.READ, CacheResult.ACCESS), Cache(CacheId.LL, CacheOp.READ, CacheResult.MISS),
                            Cache(CacheId.L1D, CacheOp.READ, CacheResult.ACCESS), Cache(CacheId.L1D, CacheOp.READ, CacheResult.MISS)], scan_memory, data, RANDOM)
    print("LL ACCESS:", access)
    print("LL MISS:  ", miss)
    print("L1D ACCESS:", access2)
    print("L1D MISS:  ", miss2)

