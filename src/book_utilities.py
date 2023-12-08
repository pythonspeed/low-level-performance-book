from contextlib import contextmanager
import sys
import os

@contextmanager
def disabled_simd():
    """
    Temporarily disable SIMD when creating an `@njit`-decorated function.

    This is a horrible hack, but Numba doesn't have any other way of doing this
    at the time of writing.

    Usage:

        with disabled_simd() as njit_no_simd:
            @njit_no_simd
            def this_will_not_use_simd():
                # ... your Numba code ...
    """
    def clear_numba():
        """Remove already imported modules for Numba and LLVMLite."""
        for mod in list(sys.modules):
            if mod.startswith("numba") or mod.startswith("llvmlite"):
                del sys.modules[mod]

    clear_numba()
    os.environ["NUMBA_LOOP_VECTORIZE"] = "0"
    try:
        from numba import njit
        yield njit
    finally:
        os.environ["NUMBA_LOOP_VECTORIZE"] = "1"
        clear_numba()
