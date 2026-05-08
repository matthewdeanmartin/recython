

Memory Allocation[¶](#memory-allocation "Permalink to this headline")
=====================================================================



Note


This page uses two different syntax variants:


* Cython specific `cdef` syntax, which was designed to make type declarations
concise and easily readable from a C/C++ perspective.
* Pure Python syntax which allows static Cython type declarations in
[pure Python code](pure.html#pep484-type-annotations),
following [PEP-484](https://www.python.org/dev/peps/pep-0484/) type hints
and [PEP 526](https://www.python.org/dev/peps/pep-0526/) variable annotations.


To make use of C data types in Python syntax, you need to import the special
`cython` module in the Python module that you want to compile, e.g.



```
import cython

```


If you use the pure Python syntax we strongly recommend you use a recent
Cython 3 release, since significant improvements have been made here
compared to the 0.29.x releases.



Dynamic memory allocation is mostly a non-issue in Python. Everything is an
object, and the reference counting system and garbage collector automatically
return memory to the system when it is no longer being used.


When it comes to more low-level data buffers, Cython has special support for
(multi-dimensional) arrays of simple types via NumPy, memory views or Python’s
stdlib array type. They are full featured, garbage collected and much easier
to work with than bare pointers in C, while still retaining the speed and static
typing benefits.
See [Working with Python arrays](array.html#array-array) and [Typed Memoryviews](../userguide/memoryviews.html#memoryviews).


In some situations, however, these objects can still incur an unacceptable
amount of overhead, which can then makes a case for doing manual memory
management in C.


Simple C values and structs (such as a local variable `cdef double x` / `x: cython.double`) are
usually [allocated on the stack](../userguide/glossary.html#term-Stack-allocation) and passed by value, but for larger and more
complicated objects (e.g. a dynamically-sized list of doubles), the memory must
be [manually requested and released](../userguide/glossary.html#term-Dynamic-allocation-or-Heap-allocation). C provides the functions `malloc()`,
`realloc()`, and `free()` for this purpose, which can be imported
in cython from `clibc.stdlib`. Their signatures are:



```
void\* malloc(size\_t size)
void\* realloc(void\* ptr, size\_t size)
void free(void\* ptr)

```


A very simple example of malloc usage is the following:



Pure PythonCython
```
import random
from cython.cimports.libc.stdlib import malloc, free

def random\_noise(number: cython.int = 1):
    i: cython.int
    # allocate number \* sizeof(double) bytes of memory
    my\_array: cython.p\_double = cython.cast(cython.p\_double, malloc(
        number \* cython.sizeof(cython.double)))
    if not my\_array:
        raise MemoryError()

    try:
        ran = random.normalvariate
        for i in range(number):
            my\_array[i] = ran(0, 1)

        # ... let's just assume we do some more heavy C calculations here to make up
        # for the work that it takes to pack the C double values into Python float
        # objects below, right after throwing away the existing objects above.

        return [x for x in my\_array[:number]]
    finally:
        # return the previously allocated memory to the system
        free(my\_array)

```



```
import random
from libc.stdlib cimport malloc, free

def random\_noise(int number=1):
    cdef int i
    # allocate number \* sizeof(double) bytes of memory
    cdef double *my\_array = <double \*> malloc(
        number \* sizeof(double))
    if not my\_array:
        raise MemoryError()

    try:
        ran = random.normalvariate
        for i in range(number):
            my\_array[i] = ran(0, 1)

        # ... let's just assume we do some more heavy C calculations here to make up
        # for the work that it takes to pack the C double values into Python float
        # objects below, right after throwing away the existing objects above.

        return [x for x in my\_array[:number]]
    finally:
        # return the previously allocated memory to the system
        free(my\_array)

```



Note that the C-API functions for allocating memory on the Python heap
are generally preferred over the low-level C functions above as the
memory they provide is actually accounted for in Python’s internal
memory management system. They also have special optimisations for
smaller memory blocks, which speeds up their allocation by avoiding
costly operating system calls.


The C-API functions can be found in the `cpython.mem` standard
declarations file:



Pure PythonCython
```
from cython.cimports.cpython.mem import PyMem\_Malloc, PyMem\_Realloc, PyMem\_Free

```



```
from cpython.mem cimport PyMem\_Malloc, PyMem\_Realloc, PyMem\_Free

```



Their interface and usage is identical to that of the corresponding
low-level C functions.


One important thing to remember is that blocks of memory obtained with
`malloc()` or [`PyMem\_Malloc()`](https://docs.python.org/3/c-api/memory.html#c.PyMem_Malloc "(in Python v3.12)") *must* be manually released
with a corresponding call to `free()` or [`PyMem\_Free()`](https://docs.python.org/3/c-api/memory.html#c.PyMem_Free "(in Python v3.12)")
when they are no longer used (and *must* always use the matching
type of free function). Otherwise, they won’t be reclaimed until the
python process exits. This is called a memory leak.


If a chunk of memory needs a larger lifetime than can be managed by a
`try..finally` block, another helpful idiom is to tie its lifetime
to a Python object to leverage the Python runtime’s memory management,
e.g.:



Pure PythonCython
```
from cython.cimports.cpython.mem import PyMem\_Malloc, PyMem\_Realloc, PyMem\_Free

@cython.cclass
class SomeMemory:
    data: cython.p\_double

    def \_\_cinit\_\_(self, number: cython.size\_t):
        # allocate some memory (uninitialised, may contain arbitrary data)
        self.data = cython.cast(cython.p\_double, PyMem\_Malloc(
            number \* cython.sizeof(cython.double)))
        if not self.data:
            raise MemoryError()

    def resize(self, new\_number: cython.size\_t):
        # Allocates new\_number \* sizeof(double) bytes,
        # preserving the current content and making a best-effort to
        # reuse the original data location.
        mem = cython.cast(cython.p\_double, PyMem\_Realloc(
            self.data, new\_number \* cython.sizeof(cython.double)))
        if not mem:
            raise MemoryError()
        # Only overwrite the pointer if the memory was really reallocated.
        # On error (mem is NULL), the originally memory has not been freed.
        self.data = mem

    def \_\_dealloc\_\_(self):
        PyMem\_Free(self.data)  # no-op if self.data is NULL

```



```
from cpython.mem cimport PyMem\_Malloc, PyMem\_Realloc, PyMem\_Free


cdef class SomeMemory:
    cdef double* data

    def \_\_cinit\_\_(self, size\_t number):
        # allocate some memory (uninitialised, may contain arbitrary data)
        self.data = <double\*> PyMem\_Malloc(
            number \* sizeof(double))
        if not self.data:
            raise MemoryError()

    def resize(self, size\_t new\_number):
        # Allocates new\_number \* sizeof(double) bytes,
        # preserving the current content and making a best-effort to
        # reuse the original data location.
        mem = <double\*> PyMem\_Realloc(
            self.data, new\_number \* sizeof(double))
        if not mem:
            raise MemoryError()
        # Only overwrite the pointer if the memory was really reallocated.
        # On error (mem is NULL), the originally memory has not been freed.
        self.data = mem

    def \_\_dealloc\_\_(self):
        PyMem\_Free(self.data)  # no-op if self.data is NULL

```





