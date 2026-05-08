

Calling C functions[¶](#calling-c-functions "Permalink to this headline")
=========================================================================



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



This tutorial describes shortly what you need to know in order to call
C library functions from Cython code. For a longer and more
comprehensive tutorial about using external C libraries, wrapping them
and handling errors, see [Using C libraries](clibraries.html).


For simplicity, let’s start with a function from the standard C
library. This does not add any dependencies to your code, and it has
the additional advantage that Cython already defines many such
functions for you. So you can just cimport and use them.


For example, let’s say you need a low-level way to parse a number from
a `char\*` value. You could use the `atoi()` function, as defined
by the `stdlib.h` header file. This can be done as follows:



Pure PythonCython
atoi.py[¶](#id1 "Permalink to this code")

```
from cython.cimports.libc.stdlib import atoi

@cython.cfunc
def parse\_charptr\_to\_py\_int(s: cython.p\_char):
    assert s is not cython.NULL, "byte string value is NULL"
    return atoi(s)  # note: atoi() has no error detection!

```




atoi.pyx[¶](#id2 "Permalink to this code")

```
from libc.stdlib cimport atoi


cdef parse\_charptr\_to\_py\_int(char\* s):
    assert s is not NULL, "byte string value is NULL"
    return atoi(s)  # note: atoi() has no error detection!

```




You can find a complete list of these standard cimport files in
Cython’s source package
[Cython/Includes/](https://github.com/cython/cython/tree/master/Cython/Includes).
They are stored in `.pxd` files, the standard way to provide reusable
Cython declarations that can be shared across modules
(see [Sharing Declarations Between Cython Modules](../userguide/sharing_declarations.html#sharing-declarations)).


Cython also has a complete set of declarations for CPython’s C-API.
For example, to test at C compilation time which CPython version
your code is being compiled with, you can do this:



Pure PythonCython
py\_version\_hex.py[¶](#id3 "Permalink to this code")

```
from cython.cimports.cpython.version import PY\_VERSION\_HEX

# Python version >= 3.2 final ?
print(PY\_VERSION\_HEX >= 0x030200F0)

```




py\_version\_hex.pyx[¶](#id4 "Permalink to this code")

```
from cpython.version cimport PY\_VERSION\_HEX

# Python version >= 3.2 final ?
print(PY\_VERSION\_HEX >= 0x030200F0)

```




Cython also provides declarations for the C math library:



Pure PythonCython
libc\_sin.py[¶](#id5 "Permalink to this code")

```
from cython.cimports.libc.math import sin

@cython.cfunc
def f(x: cython.double) -> cython.double:
    return sin(x \* x)

```




libc\_sin.pyx[¶](#id6 "Permalink to this code")

```
from libc.math cimport sin


cdef double f(double x):
    return sin(x \* x)

```





Dynamic linking[¶](#dynamic-linking "Permalink to this headline")
-----------------------------------------------------------------


The libc math library is special in that it is not linked by default
on some Unix-like systems, such as Linux. In addition to cimporting the
declarations, you must configure your build system to link against the
shared library `m`. For setuptools, it is enough to add it to the
`libraries` parameter of the `Extension()` setup:



```
from setuptools import Extension, setup
from Cython.Build import cythonize

ext\_modules = [
    Extension("demo",
              sources=["demo.pyx"],
              libraries=["m"]  # Unix-like specific
              )
]

setup(name="Demos",
      ext\_modules=cythonize(ext\_modules))

```




External declarations[¶](#external-declarations "Permalink to this headline")
-----------------------------------------------------------------------------


If you want to access C code for which Cython does not provide a ready
to use declaration, you must declare them yourself. For example, the
above `sin()` function is defined as follows:



```
cdef extern from "math.h":
    double sin(double x)

```


This declares the `sin()` function in a way that makes it available
to Cython code and instructs Cython to generate C code that includes
the `math.h` header file. The C compiler will see the original
declaration in `math.h` at compile time, but Cython does not parse
“math.h” and requires a separate definition.


Just like the `sin()` function from the math library, it is possible
to declare and call into any C library as long as the module that
Cython generates is properly linked against the shared or static
library.


Note that you can easily export an external C function from your Cython
module by declaring it as `cpdef`. This generates a Python wrapper
for it and adds it to the module dict. Here is a Cython module that
provides direct access to the C `sin()` function for Python code:



```
"""
>>> sin(0)
0.0
"""

cdef extern from "math.h":
    cpdef double sin(double x)

```


You get the same result when this declaration appears in the `.pxd`
file that belongs to the Cython module (i.e. that has the same name,
see [Sharing Declarations Between Cython Modules](../userguide/sharing_declarations.html#sharing-declarations)).
This allows the C declaration to be reused in other Cython modules,
while still providing an automatically generated Python wrapper in
this specific module.



Note


External declarations must be placed in a `.pxd` file in Pure
Python mode.





Naming parameters[¶](#naming-parameters "Permalink to this headline")
---------------------------------------------------------------------


Both C and Cython support signature declarations without parameter
names like this:



```
cdef extern from "string.h":
    char\* strstr(const char\*, const char\*)

```


However, this prevents Cython code from calling it with keyword
arguments. It is therefore preferable
to write the declaration like this instead:



```
cdef extern from "string.h":
    char\* strstr(const char \*haystack, const char \*needle)

```


You can now make it clear which of the two arguments does what in
your call, thus avoiding any ambiguities and often making your code
more readable:



Pure PythonCython
keyword\_args\_call.py[¶](#id7 "Permalink to this code")

```
from cython.cimports.strstr import strstr

def main():
    data: cython.p\_char = "hfvcakdfagbcffvschvxcdfgccbcfhvgcsnfxjh"

    pos = strstr(needle='akd', haystack=data)
    print(pos is not cython.NULL)

```




strstr.pxd[¶](#id8 "Permalink to this code")

```
cdef extern from "string.h":
    char\* strstr(const char \*haystack, const char \*needle)

```




keyword\_args\_call.pyx[¶](#id9 "Permalink to this code")

```
cdef extern from "string.h":
    char\* strstr(const char \*haystack, const char \*needle)

cdef char* data = "hfvcakdfagbcffvschvxcdfgccbcfhvgcsnfxjh"

cdef char* pos = strstr(needle='akd', haystack=data)
print(pos is not NULL)

```




Note that changing existing parameter names later is a backwards
incompatible API modification, just as for Python code. Thus, if
you provide your own declarations for external C or C++ functions,
it is usually worth the additional bit of effort to choose the
names of their arguments well.





