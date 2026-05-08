# Task: Translate Python to Cython Pure-Python Style

You are an expert Python and Cython developer. Translate the Python source below into Cython's **pure-Python** style — valid Python syntax that uses `cython` module annotations so it can be compiled by Cython or run as plain Python.

## Output contract

- Return **only** a single fenced code block: ` ```python ... ``` `
- Do **not** include prose, explanation, or multiple blocks — just the one block
- The block must contain the complete, valid Python file

## Pure-Python Cython rules

- Add `import cython` at the top
- Annotate function signatures with PEP-484 types where Cython can use them
- Use `@cython.cfunc` for internal C-speed functions (replaces `cdef`)
- Use `@cython.ccall` for functions callable from both Python and C (replaces `cpdef`)
- Declare typed local variables with `x: cython.double = 0.0` inside functions
- Use `@cython.cclass` for extension types (replaces `cdef class`)
- Module-level constants: `PI: cython.double = 3.14159`
- Keep all dunder methods (`__init__`, `__repr__`, etc.) as plain `def` — do not annotate them with `@cython.cfunc`
- The file must remain importable by plain Python without Cython installed

## What to annotate

- Numeric loops → typed local variables + `@cython.cfunc`/`@cython.ccall`
- Data classes with numeric fields → `@cython.cclass`
- Functions called in tight inner loops → `@cython.cfunc`

## What NOT to change

- Functions that use `*args`, `**kwargs`, or other dynamic features — leave as plain `def`
- `__init__.py` files with only imports or docstrings — return them verbatim

## Source to translate

```python
XXXCODEXXX
```