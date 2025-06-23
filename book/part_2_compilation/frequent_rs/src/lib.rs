//! A Rust extension that has different implementations of finding the most
//! common value in a Python list of integers.

use pyo3::types::{PyNone, PySequence};
use pyo3::{BoundObject, prelude::*};
use std::collections::HashMap;

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

/// Given a Python sequence of integers (which must fit in a signed 64-bit
/// integer), return the most frequent value.
#[pyfunction]
fn most_frequent_naive<'py>(values: &'py Bound<'py, PySequence>) -> PyResult<Bound<'py, PyAny>> {
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
fn most_frequent_impl(values: impl Iterator<Item = i64>) -> i64 {
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
fn most_frequent_optimized<'py>(values: &'py Bound<'py, PySequence>) -> PyResult<i64> {
    let result = most_frequent_impl(
        values
            .try_iter()?
            .map(|pyobject| pyobject.unwrap().extract::<i64>().unwrap()),
    );
    Ok(result)
}

#[pymodule]
fn frequent_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(most_frequent_naive, m)?)?;
    m.add_function(wrap_pyfunction!(most_frequent_optimized, m)?)?;
    Ok(())
}
