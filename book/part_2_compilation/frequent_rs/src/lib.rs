//! A Rust extension that has different implementations of finding the most
//! common value in a Python list of integers.

use pyo3::buffer::PyBuffer;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyInt, PySequence};
use std::collections::HashMap;

// start snippet one_to_one
/// One-to-one translation from Rust to Python code. All operations are done
/// with Python objects, specifically `PyDict` and `PyInt`.
#[pyfunction]
fn one_to_one<'py>(
    py: Python<'py>,
    values: Bound<'py, PySequence>,
) -> PyResult<Bound<'py, PyInt>> {
    let counts = PyDict::new(py);
    let zero = PyInt::new(py, 0);
    let one = PyInt::new(py, 1);
    for pyobject in values.try_iter()? {
        // Deal with case where iteration fails:
        let pyobject = pyobject?;
        let current_count = counts
            .get_item(&pyobject)?
            .unwrap_or_else(|| zero.as_any().clone());
        counts.set_item(pyobject, current_count.add(&one)?)?;
    }
    // Find the maximum count:
    let mut result = zero.clone();
    let mut max_count = zero;
    for (value, count) in &counts {
        if count.gt(&max_count)? {
            max_count = count.downcast_into()?;
            result = value.downcast_into()?;
        }
    }
    Ok(result.clone())
}
// end snippet one_to_one

// start snippet rust_calculations
/// Given an Iterator over `i64`, return the most frequent value.
fn frequent_algorithm<I>(values: I) -> i64
where
    I: Iterator<Item = i64>,
{
    let mut counts = HashMap::new();
    for value in values {
        counts
            .entry(value)
            .and_modify(|count| *count += 1)
            .or_insert(1);
    }
    // Find the maximum count:
    let mut result = 0;
    let mut max_count = 0;
    for (value, count) in &counts {
        if *count > max_count {
            max_count = *count;
            result = *value;
        }
    }
    result
}

/// Use a Rust `HashMap` and do math with Rust `i64`s, instead of using Python
/// objects.
#[pyfunction]
fn rust_calculations<'py>(
    values: &'py Bound<'py, PySequence>,
) -> PyResult<i64> {
    let result = frequent_algorithm(
        values
            .try_iter()?
            .map(|pyobject| pyobject.unwrap().extract::<i64>().unwrap()),
    );
    Ok(result)
}
// end snippet rust_calculations

// start snippet numpy
/// Use NumPy (or anything supporting Python's Buffer API, really) to access
/// integers without having to interact with Python objects for individual
/// integers.
#[pyfunction]
fn numpy(py: Python, values: Bound<PyAny>) -> PyResult<i64> {
    let buffer = PyBuffer::get(&values)?;
    let slice = buffer.as_slice(py).unwrap();
    let result = frequent_algorithm(slice.iter().map(|value| value.get()));
    Ok(result)
}
// end snippet numpy

/// The module exposed to Python.
#[pymodule]
fn frequent_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(one_to_one, m)?)?;
    m.add_function(wrap_pyfunction!(rust_calculations, m)?)?;
    m.add_function(wrap_pyfunction!(numpy, m)?)?;
    Ok(())
}
