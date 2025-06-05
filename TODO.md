* Show examples when automatic hoisting by the compiler doesn't work (len()?) and check if it works with Rust because it knows it's immutable?
* Compiled language faster cause of specialized types
* ILP: mental model of window of instructions, whose execution order is rearranged?

* Explain why NumPy arrays are fast to access better (slide deck somewhere that covers this?)
* Go over all code samples, make sure they're using minimal NumPyisms.
* Document existence of `py-perf-event`, `perf` command-line tool.
* Hightlight changed code with https://github.com/shafayetShafee/line-highlight
* Something about deciding when it's worth it to optimize, re business goals
* Add link to more projects mentioned inline, e.g. `cibuildwheel`.
* Mark winning entries in performance with 🥇
* Make sure sad emojis are consistent
* Alt text for all charts/images
* Moving average can use same trick as median filter (subtract from start, add to end).
* Add docstring for every function


Process:

* Making sure your code doesn't regress, with benchmarks in CI

Parallelism chapters:

* Python's GIL and free-threading
* The embarrassingly parallel model: just run more processes, or a top-level thread pool
* How big should your pool be? Covering hyperthreading
