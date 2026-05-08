# Task: Extract Cython Header Declarations (.pxd)

You are an expert Cython developer. Extract the public declarations from the `.pyx` source below to produce the matching `.pxd` header file.

## Output contract

- Return **only** a single fenced code block: ` ```cython ... ``` `
- Do **not** include prose, explanation, or multiple blocks — just the one block
- The block must be a complete, valid `.pxd` file

## .pxd rules

- Declare all `cdef class` types with their `cdef public` attributes
- Declare all `cpdef` and `cdef` functions with their signatures
- Default parameter values become `=?` (unknown default) in `.pxd` signatures
  - Correct: `cpdef double fit(list features, double lr=?)`
  - Wrong:   `cpdef double fit(list features, double lr=0.001)`
- Plain `def` functions do **not** appear in `.pxd` files
- `__init__` and other dunder methods do **not** appear in `.pxd` files
- If the source has no `cpdef`/`cdef` functions or classes, return an empty `.pxd` with just a comment: `# No declarations`
- Do **not** import anything in the `.pxd` unless it is a `cimport` of a C-level type

## .pyx source to extract from

```cython
XXXRESULTXXX
```