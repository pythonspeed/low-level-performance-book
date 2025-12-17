from hypothesis.extra.numpy import arrays
from hypothesis import given
import numpy as np

def my_sum(arr):
    total = 0
    for value in arr.ravel():
        total += value
    return total

@given(arr=arrays(np.uint64, (2, 2)))
def test_my_sum(arr):
    assert my_sum(arr) == arr.sum(), type(my_sum(arr))
