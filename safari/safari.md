# Safari

## Jargon

* data-parallel multithreading
* best practices
* dependency hell
* zero cost abstraction

## Pains

### Other

* Out of date code examples!
* Python is slow: "Python implementations are always the bottleneck"
* Nested iterators in Rust are hard.
* Benchmarking Rust is tricky, optimizer can optimize code away!
* Benchmarking in general is hard.
* Figuring out which part of Python code to optimize
* `ndarray` (not as well maintained?) vs `nalgebra` (2d/3d only) vs `faer` (linear algebra only?) vs `rapl`
* Is it worth investing time in learning Rust
* When is using Rust worth it

### With Polars

* "All that said, there are a very few instances where Polars can't do exactly what I need, just because it doesn't have the decades of maturity that pandas does - for instance, text qualifying fields with double quotes. Easy to do with pandas, real sucky with Polars."

### With NumPy

* Some operations require creating whole new arrays, which uses lots of memory, because `for` loop isn't possible.
* `for` loops aren't possible

### With alternatives like C etc.
* "OpenMP requires a runtime library, and different Python libraries can rely on different incompatible versions" (similar issue to libstdc++ linking)
* race condition
* Segmentation faults. "A recurrent complaint among the programmers in these languages is the dreadful bugs related to unsafe memory management that can take days to trace and reproduce." "Fortran programmers are famously known for having segmentation faults for breakfast."
* Learning `CMake`
* Installing correct compiler and dependencies (no package manager)
* "In addition, looking for the right compiler version and installing the correct dependencies without messing up the other libraries make things so complicated that people literally prefer to write and maintain their own set of tools instead of having to deal with the dependency hell"
* Dependency hell for users too
* parallelism makes unsafe memory worse: "parallel implementation in C/C+/Fortran means that all your unknown unknowns about unsafe memory management suddenly uncover all the obnoxious bugs that you didn’t know about until now, and that you need to track for endless hours."
* Garbage collection can add unpredictable performance (probably not relevant?)

### With PyO3/rust-numpy
* cost of copying objects from Rust to Python (e.g. structured objects), and calling PyO3 functions, and vice versa
* who allocates memory?
* Rust errors aren't the same as Python errors
* Who controls number of threads?
* Python is dynamically typed, Rust is not
* How to convert NumPy arrays on Rust side into somethign meaningful on Rust side; plus, what is meaningful on the Rust side? Should it be a Vec? (no)
* Not knowing when PyO3 copies data, specifically for arrays
* GIL limits: wanting to use multiple cores
* How to use a slice of an array in a calculation
* How to safely write to Numpy arrays in Rust
* Insufficient examples
* Can't use PyArray directly, e.g. as attribute of `#[pyclass]` since it's not `Send`.
* How to get underlying object from `Py<PyArray>`, e.g. when it's attribute of a struct.
  Need more hoops than direct function arguments.
* Not understanding how to get `py: Python<_>` instance, not realizing that `#[pyfunction]` can automatically get it.
* Bad mental model of what is expensive and what isn't in terms of performance
* `Vec` vs `PyArray`: what is difference? (maybe... not understanding slices)
* Ownership, and when copying happens. "I can't get my head around the different types, and who (python or rust) owns what/ what that means for me especially with the use of other 3rd party libraries. I don't want to be copying things around more than I have to, but I also don't want to slow the whole progam down by accessing python memory through another layer."
* Example of having arrays as attributes of pyclasses
* Understanding _when_ Rust will help. Sometimes it will, sometimes it won't.

### Using Rust

* Introducing compiled code makes CI, packaging, and working with macs vs pcs harder
* Underdeveloped ecosystem

## Recommendations

### Why Rust is good
* Rust for thread-safety
* Rust for parallelism
* Memory safety
* Zero size types allow for things like physical units to be enforced throughout algorithms without a runtime overhead

### Alternatives

* Numba
* Cython

### Practices
* Same directory for Rust and Python
* Separate low-level Rust level from Python integration layer
* Pre-allocate memory on Python side
* Translate Python errors to Rust errors
* Avoid `panic`
* Allow user to control number of threads
* Dispatch to Rust translator functions based on Python data type.
* Both Python and Rust tests
* Use efficient memory layout: 2D array rather than Vec of Vecs.
* Use `ArrayView2<_>` as return by `as_array` on a `PyArray`.
* `PyReadwriteArray` for safe writing to arrays
* Hold GIL while doing Rayon thread pool (using `rust-numpy`'s `par_map_collect`') ensures other Python threads don't mess with an array while still giving parallelism
* You can't use PyArray directly, so you use either reference (`&'py PyArray`) or reference counter ownership `Py<PyArray<_>>`.
* Convert Python to Rust object, process, convert back to Python object
* `.for_each()` on iterator. Good when you want to chain, otherwise probably doesn't add much.
* Make arrays mutable with `unsafe { x.as_array_mut() }` (bad idea, probably).
* "TL;DR: benchmark real code, not toy examples." because compiler can can larger-scale analysis of code, it might get performance benefits in real code you don't see if you're just recreating something NumPy already does quickly.
* Don't optimize or rewrite unnecessarily; do just enough work to get the speed you need
* Don't force people to learn new language unnecessarily
* Profile Python to figure out which parts to optimize
* ★ When optimizing Python version, start with Rust code that just looks like the Python code, and translate
* move class definition from Python into Rust for faster access from Rust (https://ohadravid.github.io/posts/2023-03-rusty-python/)
* Add getters to make Rust struct attributes accessible from Python
* Use new scopes to reduce how long borrows live
* Compile with debug info in release mode to enable profiling
* Speed of coding is important in exploratory mode, since code might get thrown out. Python is good for this. For production use, Rust's speed and correctness can help.

### Bounds checks

* To figure out if bounds checks are an issue, remove them with `get_unchecked()`, if that helps a lot then spend time figuring out how to do it safely.
* `assert!()` can ehlp
* establish, before loop, that all iterations are valid
* Rewrite using iterators might help (probably especially with exact size iterator?)

### Tools

* Maturin
* Github Actions CI
* Rayon
* ndarray::parallel for Rayon for arrays
    * try_for_each
    * par_azip!, store errors in result list
* `ordered-float` crat
* Just use `numba`
* `nalgebra`
* Criterion + blackbox for benchmarking
* `py-spy`'s combined Python + native stacks is helpful for figuring out Rust bottlenecks too
* `perf` + `inferno`
* `flamegraph` (same as above probably)
* https://github.com/wnorcbrown/serde-numpy for faster loading of images into NumPy arrays
* https://github.com/SunDoge/dlpark for dlpack format (N-dimensional array/tensor format)

### Optimizations

* Avoid square roots, compare squared values for distance
* Multiplication instead of division
* Faster hash functions, e.g. `fxhash`
* Reusing memory
* Use `ExactSizeIterator` so compiler can optimize out bounds checks
* Runtime feature detection for SIMD
* If you support storing any random Python object, you'll lose the benefits of Rust

### Type annotations

* You can make generics in Python: https://github.com/entity-neural-network/ragged-buffer/blob/78657b4603d8dc9680e3d166064f73b289aa2ac1/ragged_buffer/__init__.py

### Understanding hardware

* If you know how RAM and caches are (memory bandwidth), you can figure out if that'll be bottleneck compared to CPU

## Worldview

* Development speed and maintainability is more important performance
* Memory safety is a beginner issue
* "business or scientific constraints don’t incentivize this degree of optimization"
* Working software beats theoretical speed
