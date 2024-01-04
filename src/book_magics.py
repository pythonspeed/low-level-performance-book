from timeit import timeit
from io import BytesIO
import locale

from IPython.core.magic import (
    register_cell_magic,
    register_line_magic,
    needs_local_scope,
)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.display import display, Markdown, Image
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style
import numpy as np
import PIL.Image
from py_perf_event import measure, Hardware

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


def ns_per_iteration(line, globals):
    elapsed_secs = timeit(line, globals=globals, number=1_00)
    return int((elapsed_secs * 1_000_000_000) / 1_000)


MEASUREMENTS = {
    "instructions": (
        "CPU instruction",
        [Hardware.INSTRUCTIONS],
        lambda instructions: instructions,
    ),
}


@magic_arguments()
@argument("--measure")
@needs_local_scope
@register_cell_magic
def compare_timing(line, cell, local_ns):
    arguments = parse_argstring(compare_timing, line)
    measurements = arguments.measure.split(",")

    result = []
    for line in cell.splitlines():
        line = line.strip()
        if not line:
            continue
        result.append([f"`{line}`", ns_per_iteration(line, local_ns)])
        if measurements:
            for m in measurements:
                _, events, post_process = MEASUREMENTS[m]
                results = measure(events, exec, line, local_ns)
                result[-1].append(post_process(*results))

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

    headers = ["Code", f"Time to run ({units})"]
    for m in measurements:
        headers.append(MEASUREMENTS[m][0])

    table = MarkdownTableWriter(headers=headers, value_matrix=result)
    table.set_style(1, Style(thousand_separator=","))
    table.set_style(2, Style(thousand_separator=","))
    display(Markdown(table.dumps()))


@needs_local_scope
@register_line_magic
def display_image(line, local_ns):
    array_name = line.strip()
    array = local_ns[array_name]
    f = BytesIO()
    PIL.Image.fromarray(array).save(f, "png")
    display(Image(data=f.getvalue()))


def load_ipython_extension(ipython):
    # Make sure turboboost is disabled; TODO add AMD, non-Linux?
    with open("/sys/devices/system/cpu/intel_pstate/no_turbo") as f:
        assert f.read().strip() == "1"
