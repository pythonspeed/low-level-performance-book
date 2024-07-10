from py_perf_event import measure, Hardware, CacheId, CacheOp, CacheResult, Cache, Raw
from book_common import measure_peak_memory


MEASUREMENTS = {
    "instructions": (
        [Hardware.INSTRUCTIONS],
        lambda instructions: instructions,
    ),
    "memory_cache_miss": (
        [Hardware.CACHE_REFERENCES, Hardware.CACHE_MISSES],
        lambda refs, misses: round((misses / refs) * 100, 1),
    ),
    "memory_cache_refs": (
        [Hardware.CACHE_REFERENCES],
        lambda refs: refs,
    ),
    "l1_memory_cache_miss": (
        [
            Cache(CacheId.L1D, CacheOp.READ, CacheResult.ACCESS),
            Cache(CacheId.L1D, CacheOp.READ, CacheResult.MISS),
        ],
        lambda refs, misses: round((misses / refs) * 100, 1),
    ),
    "l1_memory_cache_refs": (
        [Cache(CacheId.L1D, CacheOp.READ, CacheResult.ACCESS)],
        lambda refs: refs,
    ),
    "ll_memory_cache_miss": (
        [
            Cache(CacheId.LL, CacheOp.READ, CacheResult.ACCESS),
            Cache(CacheId.LL, CacheOp.READ, CacheResult.MISS),
        ],
        lambda refs, misses: round((misses / refs) * 100, 1),
    ),
    "ll_memory_cache_refs": (
        [Cache(CacheId.LL, CacheOp.READ, CacheResult.ACCESS)],
        lambda refs: refs,
    ),
    "branch_mispredictions": (
        [Hardware.BRANCH_INSTRUCTIONS, Hardware.BRANCH_MISSES],
        lambda ints, misses: round((misses / ints) * 100, 1),
    ),
    "branches": (
        [Hardware.BRANCH_INSTRUCTIONS],
        lambda ints: ints,
    ),
    "simd_256bit": (
        [
            # perf stat -vv -a -e fp_arith_inst_retired.256b_packed_double
            Raw(0x10C7),
            # perf stat -vv -a -e fp_arith_inst_retired.256b_packed_single
            Raw(0x20C7),
        ],
        lambda double, single: double + single,
    ),
    "simd_128bit": (
        [
            # perf stat -vv -a -e fp_arith_inst_retired.128b_packed_double
            Raw(0x4C7),
            # perf stat -vv -a -e fp_arith_inst_retired.128b_packed_single
            Raw(0x8C7),
        ],
        lambda double, single: double + single,
    ),
    "peak_memory": (
        # Handled specially:
        [],
        lambda x: x,
    ),
}


def get_measurements(
    measurement_keys: list[str], line: str, local_ns: dict[str, object]
) -> list[int | str]:
    event_set = set()
    event_counts = {}  # map event name to count
    for m in measurement_keys:
        events, _ = MEASUREMENTS[m]
        event_set |= set(events)

    event_list = list(event_set)
    for event, counter in zip(event_list, measure(event_list, exec, line, local_ns)):
        event_counts[event] = counter

    result = []
    for m in measurement_keys:
        if m == "peak_memory":
            # Handled specially:
            value = measure_peak_memory(line, local_ns)
        else:
            events, post_process = MEASUREMENTS[m]
            value = post_process(*[event_counts[ev] for ev in events])
        result.append(value)

    return result
