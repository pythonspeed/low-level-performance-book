import sys
import os
from timeit import timeit
from io import BytesIO
import locale
from time import perf_counter_ns, sleep
import gc
import tracemalloc

from IPython.core.magic import (
    register_cell_magic,
    register_line_magic,
    needs_local_scope,
)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import display, Markdown, Image
from IPython.core import page as ipython_page
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style
import numpy as np
import PIL.Image

from numba import config as numba_config

if False:#sys.platform == "linux":
    from book_linux import get_measurements
else:
    from book_common import measure_peak_memory

    def get_measurements(
            measurement_keys: list[str], line: str, local_ns: dict[str, object]
    ) -> list[int | str]:
        result = []
        for key in measurement_keys:
            if key == "peak_memory":
                result.append(measure_peak_memory(line, local_ns))
            else:
                result.append(f"N/A, Linux only")
        return result


locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

HELP_THIS_BOOK = os.getenv("HELP_THIS_BOOK") == "1"


# Workaround for https://github.com/quarto-dev/quarto-cli/issues/10248
ipython_page.page = lambda text: display(Markdown(f"```\n{text}\n```"))


def ns_per_iteration(line, globals):
    gc.disable()
    estimated_ns = int(
        timeit(line, globals=globals, number=10, timer=perf_counter_ns) / 10
    )
    iterations = max(10_000_000 // estimated_ns, 100)
    if estimated_ns > 10_000_000:
        iterations = 10

    result = (
        timeit(line, globals=globals, number=iterations, timer=perf_counter_ns)
        // iterations
    )
    gc.enable()
    return result


def _validate_ns_per_iteration():
    elapsed_ns = ns_per_iteration("sleep(0.001)", globals())
    assert 900_000 < elapsed_ns < 1_100_000, elapsed_ns
    elapsed_ns = ns_per_iteration("(lambda: None)()", globals())
    assert elapsed_ns < 1000, elapsed_ns


_validate_ns_per_iteration()
del _validate_ns_per_iteration


def display_table(markdown_table: str):
    """Display a Markdown table in Jupyter."""
    if HELP_THIS_BOOK:
        display(
            Markdown(
                "```\n"
                + markdown_table
                + "```\n"
                + "(↑ helpthisbook.com doesn't support tables, this will be rendered correctly in the real book ↑)\n\n"
            )
        )
    else:
        display(Markdown(markdown_table))


MEASUREMENT_TITLES = {
    "instructions": "CPU instructions",
    "memory_cache_miss": "L3 memory cache miss %",
    "memory_cache_refs": "L3 memory cache references",
    "l1_memory_cache_miss": "L1 memory cache miss %",
    "l1_memory_cache_refs": "L1 memory cache references",
    "ll_memory_cache_miss": "LL memory cache miss %",
    "ll_memory_cache_refs": "LL memory cache references",
    "branch_mispredictions": "Branch misprediction %",
    "branches": "Branch instructions",
    "simd_256bit": "256-bit SIMD instructions",
    "simd_128bit": "128-bit SIMD instructions",
    "peak_memory": "Peak allocated memory (bytes)",
}


@magic_arguments()
@argument("--measure", default="")
@needs_local_scope
@register_cell_magic
def compare_timing(line, cell, local_ns):
    numba_config.DISABLE_JIT = True

    arguments = parse_argstring(compare_timing, line)
    measurements = [m for m in arguments.measure.split(",") if m]

    result = []
    for line in cell.splitlines():
        line = line.strip()
        if not line:
            continue
        result.append([f"`{line}`", ns_per_iteration(line, local_ns)])
        if measurements:
            result[-1].extend(get_measurements(measurements, line, local_ns))

    minimum_value = min(r[1] for r in result)
    for (units, factor) in [
        ("milliseconds", 1_000_000),
        ("microseconds", 1_000),
        ("nanoseconds", 1),
    ]:
        if minimum_value > factor * 10:
            break
    for row in result:
        row[1] /= factor
        # Round to whole numbers:
        row[1] = int(round(row[1]))

    headers = ["Code", f"Elapsed {units}"]
    for m in measurements:
        headers.append(MEASUREMENT_TITLES[m])

    table = MarkdownTableWriter(headers=headers, value_matrix=result)
    for i in range(1, len(headers)):
        table.set_style(i, Style(thousand_separator=",", align="right"))
    display_table(table.dumps())
    numba_config.DISABLE_JIT = False


@needs_local_scope
@register_line_magic
def display_image(line, local_ns):
    array_name = line.strip()
    array = local_ns[array_name]
    f = BytesIO()
    PIL.Image.fromarray(array).save(f, "png")
    display(Image(data=f.getvalue()))


@register_cell_magic
def maybe_table(line, cell):
    display_table(cell)


def load_ipython_extension(ipython):
    # Make sure turboboost is disabled; TODO add AMD, non-Linux?
    with open("/sys/devices/system/cpu/intel_pstate/no_turbo") as f:
        assert f.read().strip() == "1"
