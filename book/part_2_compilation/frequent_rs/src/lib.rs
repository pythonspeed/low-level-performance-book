//! A Rust extension that has different implementations of finding the most
//! common value in a Python list of integers.

use pyo3::buffer::PyBuffer;
use pyo3::types::{PyDict, PyInt, PyNone, PySequence};
use pyo3::{BoundObject, prelude::*};
use std::collections::HashMap;

/// One-to-one translation from Rust to Python code. All operations are done
/// with Python objects, specifically `PyDict` and `PyInt`.
#[pyfunction]
fn one_to_one<'py>(py: Python<'py>, values: Bound<'py, PySequence>) -> PyResult<Bound<'py, PyInt>> {
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

/// Wrap a Python object so that it can be used in Rust HashMaps.
struct HashEqWrapper<'a> {
    pyobject: Bound<'a, PyAny>,
}

/// Use the Python object's hash to support Rust hashing.
impl<'a> std::hash::Hash for HashEqWrapper<'a> {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        state.write_isize(self.pyobject.hash().unwrap());
    }
}

/// Use the Python object's equality to support Rust equality.
impl<'a> PartialEq for HashEqWrapper<'a> {
    fn eq(&self, other: &Self) -> bool {
        self.pyobject.eq(&other.pyobject).unwrap()
    }
}

impl<'a> Eq for HashEqWrapper<'a> {}

/// Use a Rust HashMap and Rust math, but still use Python objects as the keys in the HashMap.
#[pyfunction]
fn naive<'py>(values: &'py Bound<'py, PySequence>) -> PyResult<Bound<'py, PyAny>> {
    let mut counts = HashMap::new();
    for pyobject in values.try_iter()? {
        // Deal with case where iteration fails:
        let pyobject = pyobject?;
        // Wrap the object in a wrapper that uses Python's hashing and equality
        // to implement Rust's hashing and equality:
        let pyobject = HashEqWrapper { pyobject };
        // If there's an entry, increment count by 1, otherwise insert 1:
        counts
            .entry(pyobject)
            .and_modify(|count| *count += 1)
            .or_insert(1);
    }
    // Find the maximum count:
    let mut result = &PyNone::get(values.py()).into_any().into_bound();
    let mut max_count = 0;
    for (value, count) in &counts {
        if *count > max_count {
            max_count = *count;
            result = value.pyobject.as_any();
        }
    }
    Ok(result.clone())
}

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

/// Given a Python sequence of integers (which must fit in a signed 64-bit
/// integer), return the most frequent value. In this version the `HashMap` uses
/// `i64` instead of Python objects.
#[pyfunction]
fn python_iterator<'py>(values: &'py Bound<'py, PySequence>) -> PyResult<i64> {
    let result = frequent_algorithm(
        values
            .try_iter()?
            .map(|pyobject| pyobject.unwrap().extract::<i64>().unwrap()),
    );
    Ok(result)
}

/// Convert all the Python objects to a Rust data structure right at the start. Actually slower, so not shown in chapter.
#[pyfunction]
fn batch_conversion_up_front(values: Vec<i64>) -> PyResult<i64> {
    let result = frequent_algorithm(values.into_iter());
    Ok(result)
}

/// Use NumPy (or anything supporting Python's Buffer API, really) to access
/// integers without having to interact with Python objects at all (other than
/// the container).
#[pyfunction]
fn numpy(py: Python, values: Bound<PyAny>) -> PyResult<i64> {
    let buffer = PyBuffer::get(&values)?;
    let slice = buffer.as_slice(py).unwrap();
    let result = frequent_algorithm(slice.iter().map(|value| value.get()));
    Ok(result)
}

/// The module exposed to Python.
#[pymodule]
fn frequent_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(one_to_one, m)?)?;
    m.add_function(wrap_pyfunction!(naive, m)?)?;
    m.add_function(wrap_pyfunction!(python_iterator, m)?)?;
    m.add_function(wrap_pyfunction!(numpy, m)?)?;
    m.add_function(wrap_pyfunction!(batch_conversion_up_front, m)?)?;
    Ok(())
}
