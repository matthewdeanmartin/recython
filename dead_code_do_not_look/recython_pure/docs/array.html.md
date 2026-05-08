

Working with Python arrays[¶](#working-with-python-arrays "Permalink to this headline")
=======================================================================================



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



Python has a builtin array module supporting dynamic 1-dimensional arrays of
primitive types. It is possible to access the underlying C array of a Python
array from within Cython. At the same time they are ordinary Python objects
which can be stored in lists and serialized between processes when using
[`multiprocessing`](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing "(in Python v3.12)").


Compared to the manual approach with `malloc()` and `free()`, this
gives the safe and automatic memory management of Python, and compared to a
Numpy array there is no need to install a dependency, as the [`array`](https://docs.python.org/3/library/array.html#module-array "(in Python v3.12)")
module is built into both Python and Cython.



Safe usage with memory views[¶](#safe-usage-with-memory-views "Permalink to this headline")
-------------------------------------------------------------------------------------------



Pure PythonCython
```
from cython.cimports.cpython import array
import array
a = cython.declare(array.array, array.array('i', [1, 2, 3]))
ca = cython.declare(cython.int[:], a)

print(ca[0])

```



```
from cpython cimport array
import array
cdef array.array a = array.array('i', [1, 2, 3])
cdef int[:] ca = a

print(ca[0])

```



NB: the import brings the regular Python array object into the namespace
while the cimport adds functions accessible from Cython.


A Python array is constructed with a type signature and sequence of
initial values. For the possible type signatures, refer to the Python
documentation for the [array module](https://docs.python.org/library/array.html).


Notice that when a Python array is assigned to a variable typed as
memory view, there will be a slight overhead to construct the memory
view. However, from that point on the variable can be passed to other
functions without overhead, so long as it is typed:



Pure PythonCython
```
from cython.cimports.cpython import array
import array

a = cython.declare(array.array, array.array('i', [1, 2, 3]))
ca = cython.declare(cython.int[:], a)

@cython.cfunc
def overhead(a: cython.object) -> cython.int:
    ca: cython.int[:] = a
    return ca[0]

@cython.cfunc
def no\_overhead(ca: cython.int[:]) -> cython.int:
    return ca[0]

print(overhead(a))  # new memory view will be constructed, overhead
print(no\_overhead(ca))  # ca is already a memory view, so no overhead

```



```
from cpython cimport array
import array

cdef array.array a = array.array('i', [1, 2, 3])
cdef int[:] ca = a


cdef int overhead(object a):
    cdef int[:] ca = a
    return ca[0]


cdef int no\_overhead(int[:] ca):
    return ca[0]

print(overhead(a))  # new memory view will be constructed, overhead
print(no\_overhead(ca))  # ca is already a memory view, so no overhead

```





Zero-overhead, unsafe access to raw C pointer[¶](#zero-overhead-unsafe-access-to-raw-c-pointer "Permalink to this headline")
----------------------------------------------------------------------------------------------------------------------------


To avoid any overhead and to be able to pass a C pointer to other
functions, it is possible to access the underlying contiguous array as a
pointer. There is no type or bounds checking, so be careful to use the
right type and signedness.



Pure PythonCython
```
from cython.cimports.cpython import array
import array

a = cython.declare(array.array, array.array('i', [1, 2, 3]))

# access underlying pointer:
print(a.data.as\_ints[0])

from cython.cimports.libc.string import memset

memset(a.data.as\_voidptr, 0, len(a) \* cython.sizeof(cython.int))

```



```
from cpython cimport array
import array

cdef array.array a = array.array('i', [1, 2, 3])

# access underlying pointer:
print(a.data.as\_ints[0])

from libc.string cimport memset

memset(a.data.as\_voidptr, 0, len(a) \* sizeof(int))

```



Note that any length-changing operation on the array object may invalidate the
pointer.




Cloning, extending arrays[¶](#cloning-extending-arrays "Permalink to this headline")
------------------------------------------------------------------------------------


To avoid having to use the array constructor from the Python module,
it is possible to create a new array with the same type as a template,
and preallocate a given number of elements. The array is initialized to
zero when requested.



Pure PythonCython
```
from cython.cimports.cpython import array
import array

int\_array\_template = cython.declare(array.array, array.array('i', []))
cython.declare(newarray=array.array)

# create an array with 3 elements with same type as template
newarray = array.clone(int\_array\_template, 3, zero=False)

```



```
from cpython cimport array
import array

cdef array.array int\_array\_template = array.array('i', [])
cdef array.array newarray

# create an array with 3 elements with same type as template
newarray = array.clone(int\_array\_template, 3, zero=False)

```



An array can also be extended and resized; this avoids repeated memory
reallocation which would occur if elements would be appended or removed
one by one.



Pure PythonCython
```
from cython.cimports.cpython import array
import array

a = cython.declare(array.array, array.array('i', [1, 2, 3]))
b = cython.declare(array.array, array.array('i', [4, 5, 6]))

# extend a with b, resize as needed
array.extend(a, b)
# resize a, leaving just original three elements
array.resize(a, len(a) - len(b))

```



```
from cpython cimport array
import array

cdef array.array a = array.array('i', [1, 2, 3])
cdef array.array b = array.array('i', [4, 5, 6])

# extend a with b, resize as needed
array.extend(a, b)
# resize a, leaving just original three elements
array.resize(a, len(a) - len(b))

```





API reference[¶](#api-reference "Permalink to this headline")
-------------------------------------------------------------



### Data fields[¶](#data-fields "Permalink to this headline")



```
data.as\_voidptr
data.as\_chars
data.as\_schars
data.as\_uchars
data.as\_shorts
data.as\_ushorts
data.as\_ints
data.as\_uints
data.as\_longs
data.as\_ulongs
data.as\_longlongs  # requires Python >=3
data.as\_ulonglongs  # requires Python >=3
data.as\_floats
data.as\_doubles
data.as\_pyunicodes

```


Direct access to the underlying contiguous C array, with given type;
e.g., `myarray.data.as\_ints`.




### Functions[¶](#functions "Permalink to this headline")


The following functions are available to Cython from the array module



Pure PythonCython
```
@cython.cfunc
@cython.exceptval(-1)
def resize(self: array.array, n: cython.Py\_ssize\_t) -> cython.int

```



```
cdef int resize(array.array self, Py\_ssize\_t n) except -1

```



Fast resize / realloc. Not suitable for repeated, small increments; resizes
underlying array to exactly the requested amount.




---



Pure PythonCython
```
@cython.cfunc
@cython.exceptval(-1)
def resize\_smart(self: array.array, n: cython.Py\_ssize\_t) -> cython.int

```



```
cdef int resize\_smart(array.array self, Py\_ssize\_t n) except -1

```



Efficient for small increments; uses growth pattern that delivers
amortized linear-time appends.




---



Pure PythonCython
```
@cython.cfunc
@cython.inline
def clone(template: array.array, length: cython.Py\_ssize\_t, zero: cython.bint) -> array.array

```



```
cdef inline array.array clone(array.array template, Py\_ssize\_t length, bint zero)

```



Fast creation of a new array, given a template array. Type will be same as
`template`. If zero is `True`, new array will be initialized with zeroes.




---



Pure PythonCython
```
@cython.cfunc
@cython.inline
def copy(self: array.array) -> array.array

```



```
cdef inline array.array copy(array.array self)

```



Make a copy of an array.




---



Pure PythonCython
```
@cython.cfunc
@cython.inline
@cython.exceptval(-1)
def extend\_buffer(self: array.array, stuff: cython.p\_char, n: cython.Py\_ssize\_t) -> cython.int

```



```
cdef inline int extend\_buffer(array.array self, char\* stuff, Py\_ssize\_t n) except -1

```



Efficient appending of new data of same type (e.g. of same array type)
`n`: number of elements (not number of bytes!)




---



Pure PythonCython
```
@cython.cfunc
@cython.inline
@cython.exceptval(-1)
def extend(self: array.array, other: array.array) -> cython.int

```



```
cdef inline int extend(array.array self, array.array other) except -1

```



Extend array with data from another array; types must match.




---



Pure PythonCython
```
@cython.cfunc
@cython.inline
def zero(self: array.array) -> cython.void

```



```
cdef inline void zero(array.array self)

```



Set all elements of array to zero.






