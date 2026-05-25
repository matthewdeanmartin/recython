# examples_benchmark

Cython-compiled equivalents of the three `examples/` mini-projects, with a benchmark harness that compares pure-Python vs compiled performance.

## Structure

```
examples_benchmark/
├── benchmark.py                   # benchmark runner
├── Makefile                       # build + bench targets
├── fuzzy_arithmetic_cy/
│   ├── fuzzy_arithmetic_cy.pyx    # Cython source
│   └── setup.py
├── multiple_regression_cy/
│   ├── multiple_regression_cy.pyx
│   └── setup.py
└── orbital_mechanics_cy/
    ├── orbital_mechanics_cy.pyx
    └── setup.py
```

## Building

From `examples_benchmark/`:

```bash
make build   # compile all three extensions in-place
make bench   # run benchmarks (requires built extensions)
make all     # build + bench
make clean   # remove compiled artifacts
```

Or manually per extension:

```bash
cd fuzzy_arithmetic_cy && python setup.py build_ext --inplace
cd multiple_regression_cy && python setup.py build_ext --inplace
cd orbital_mechanics_cy && python setup.py build_ext --inplace
```

## Benchmark Results

Environment: Python 3.12.10 · Cython 3.0.11 · Windows 11 x64 · MSVC 2022

| Benchmark           | Pure Python | Cython  | Speedup |
|---------------------|-------------|---------|---------|
| Fuzzy Arithmetic    | 0.0017 s    | 0.0004 s | **4.70×** |
| Multiple Regression | 0.1821 s    | 0.0669 s | **2.72×** |
| Orbital Mechanics   | 0.0043 s    | 0.0014 s | **3.16×** |

*(Best of 5 runs, `timeit.repeat`)*

### Notes on speedups

- **Fuzzy Arithmetic** benefits most from typed `cdef class` fields and `cpdef` methods — the tight loop over 400 iterations with object creation bottlenecks Python's attribute lookup overhead.
- **Multiple Regression** gains from typed loop variables and direct `double` arithmetic, but the gradient-descent hot loop still boxes/unboxes Python `list` elements, which caps the ceiling.
- **Orbital Mechanics** uses `libc.math sqrt` and typed `cdef class Body` fields; the O(n²) gravitational step runs fully in C-typed arithmetic.

## Cython techniques used

| Technique | Purpose |
|-----------|---------|
| `cdef class` | Typed extension types — attribute access in C, no `__dict__` |
| `cpdef` functions | Callable from Python and C; fast intra-module dispatch |
| `cdef double/int` locals | Eliminate boxing/unboxing in hot loops |
| `libc.math` imports | Direct C `sqrt`, `sin`, `fmin`, `fmax` — no Python call overhead |
| Compiler directives | `boundscheck=False`, `wraparound=False`, `cdivision=True` |
