# Task: Translate Python to Cython Classic Style (.pyx)

You are an expert Python and Cython developer. Translate the Python source below into a Cython 3.x `.pyx` file.

## Output contract

- Return **only** a single fenced code block: ` ```cython ... ``` `
- Do **not** include prose, explanation, or multiple blocks — just the one block
- The block must contain the complete, compilable `.pyx` file
- If any part cannot be safely Cythonized, leave it as plain `def` and add a one-line `# NOTE:` comment explaining why

## Cython 3.x rules

- `cpdef` functions: put the return type **before** the function name, remove the `-> type` suffix
  - Correct: `cpdef double compute(double x):`
  - Wrong:   `cpdef compute(double x) -> double:`
- Variables: declare with `cdef`, never `cpdef`
- `__init__`, `__repr__`, `__str__`, `__eq__`, and all other dunder methods stay as plain `def`
- Functions using `*args` or `**kwargs` stay as plain `def`
- `print(...)` always needs parentheses — this is Python 3
- `cdef class` extension types give the best speedup for data-holding objects
- Add `# cython: language_level=3` at the top of the file
- Prefer `cdef` locals inside hot loops: `cdef int i`, `cdef double x`
- Use `libc.math` imports (`from libc.math cimport sqrt, sin`) instead of Python’s `math` module where possible

## What to cythonize

- Numeric loops → typed `cdef` locals + `cpdef` or `cdef` functions
- Data classes with numeric fields → `cdef class` with `cdef public` attributes
- Module-level constants that are plain numbers → `DEF` or typed `cdef`

## What NOT to change

- `__init__.py` files with only imports or docstrings — return them verbatim
- Lines that use dynamic Python features (e.g. `**kwargs`, `getattr`, `zip` with `strict=`) — keep as `def`

## Source to translate

```python
XXXCODEXXX
```