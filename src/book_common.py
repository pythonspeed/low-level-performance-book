import tracemalloc

def measure_peak_memory(line: str, local_ns: dict[str, object]) -> int:
    """Measure peak memory (in bytes) using tracemalloc."""
    tracemalloc.start()
    exec(line, local_ns)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak
