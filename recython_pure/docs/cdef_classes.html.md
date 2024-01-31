

Extension types (aka. cdef classes)[¶](#extension-types-aka-cdef-classes "Permalink to this headline")
======================================================================================================



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



To support object-oriented programming, Cython supports writing normal
Python classes exactly as in Python:



```
class MathFunction(object):
    def \_\_init\_\_(self, name, operator):
        self.name = name
        self.operator = operator

    def \_\_call\_\_(self, \*operands):
        return self.operator(\*operands)

```


Based on what Python calls a “built-in type”, however, Cython supports
a second kind of class: *extension types*, sometimes referred to as
“cdef classes” due to the Cython language keywords used for their declaration.
They are somewhat restricted compared to Python classes, but are generally
more memory efficient and faster than generic Python classes. The
main difference is that they use a C struct to store their fields and methods
instead of a Python dict. This allows them to store arbitrary C types
in their fields without requiring a Python wrapper for them, and to
access fields and methods directly at the C level without passing
through a Python dictionary lookup.


Normal Python classes can inherit from cdef classes, but not the other
way around. Cython requires to know the complete inheritance
hierarchy in order to lay out their C structs, and restricts it to
single inheritance. Normal Python classes, on the other hand, can
inherit from any number of Python classes and extension types, both in
Cython code and pure Python code.



Pure PythonCython
```
@cython.cclass
class Function:
    @cython.ccall
    def evaluate(self, x: float) -> float:
        return 0

```



```
 
cdef class Function:

    cpdef double evaluate(self, double x) except \*:
        return 0

```



The `cpdef` command (or `@cython.ccall` in Python syntax) makes two versions
of the method available; one fast for use from Cython and one slower for use
from Python.


Now we can add subclasses of the `Function` class that implement different
math functions in the same `evaluate()` method.


Then:



Pure PythonCython
sin\_of\_square.py[¶](#id1 "Permalink to this code")

```
from cython.cimports.libc.math import sin

@cython.cclass
class Function:
    @cython.ccall
    def evaluate(self, x: float) -> float:
        return 0

@cython.cclass
class SinOfSquareFunction(Function):
    @cython.ccall
    def evaluate(self, x: float) -> float:
        return sin(x \*\* 2)

```




sin\_of\_square.pyx[¶](#id2 "Permalink to this code")

```
from libc.math cimport sin


cdef class Function:

    cpdef double evaluate(self, double x) except \*:
        return 0


cdef class SinOfSquareFunction(Function):

    cpdef double evaluate(self, double x) except \*:
        return sin(x \*\* 2)

```




This does slightly more than providing a python wrapper for a cdef
method: unlike a cdef method, a cpdef method is fully overridable by
methods and instance attributes in Python subclasses. This adds a
little calling overhead compared to a cdef method.


To make the class definitions visible to other modules, and thus allow for
efficient C-level usage and inheritance outside of the module that
implements them, we define them in a `.pxd` file with the same name
as the module. Note that we are using Cython syntax here, not Python syntax.



sin\_of\_square.pxd[¶](#id3 "Permalink to this code")

```
cdef class Function:
    cpdef double evaluate(self, double x) except \*

cdef class SinOfSquareFunction(Function):
    cpdef double evaluate(self, double x) except \*

```



With this way to implement different functions as subclasses with fast,
Cython callable methods, we can now pass these `Function` objects into
an algorithm for numeric integration, that evaluates an arbitrary user
provided function over a value interval.


Using this, we can now change our integration example:



Pure PythonCython
integrate.py[¶](#id4 "Permalink to this code")

```
from cython.cimports.sin\_of\_square import Function, SinOfSquareFunction

def integrate(f: Function, a: float, b: float, N: cython.int):
    i: cython.int

    if f is None:
        raise ValueError("f cannot be None")

    s: float = 0
    dx: float = (b - a) / N

    for i in range(N):
        s += f.evaluate(a + i \* dx)

    return s \* dx

print(integrate(SinOfSquareFunction(), 0, 1, 10000))

```




integrate.pyx[¶](#id5 "Permalink to this code")

```
from sin\_of\_square cimport Function, SinOfSquareFunction

def integrate(Function f, double a, double b, int N):
    cdef int i
    cdef double s, dx
    if f is None:
        raise ValueError("f cannot be None")

    s = 0
    dx = (b - a) / N

    for i in range(N):
        s += f.evaluate(a + i \* dx)

    return s \* dx

print(integrate(SinOfSquareFunction(), 0, 1, 10000))

```




We can even pass in a new `Function` defined in Python space, which overrides
the Cython implemented method of the base class:



```
>>> import integrate
>>> class MyPolynomial(integrate.Function):
...     def evaluate(self, x):
...         return 2\*x\*x + 3\*x - 10
...
>>> integrate(MyPolynomial(), 0, 1, 10000)
-7.8335833300000077

```


Since `evaluate()` is a Python method here, which requires Python objects
as input and output, this is several times slower than the straight C call
to the Cython method, but still faster than a plain Python variant.
This shows how large the speed-ups can easily be when whole computational
loops are moved from Python code into a Cython module.


Some notes on our new implementation of `evaluate`:


* The fast method dispatch here only works because `evaluate` was
declared in `Function`. Had `evaluate` been introduced in
`SinOfSquareFunction`, the code would still work, but Cython
would have used the slower Python method dispatch mechanism
instead.
* In the same way, had the argument `f` not been typed, but only
been passed as a Python object, the slower Python dispatch would
be used.
* Since the argument is typed, we need to check whether it is
`None`. In Python, this would have resulted in an `AttributeError`
when the `evaluate` method was looked up, but Cython would instead
try to access the (incompatible) internal structure of `None` as if
it were a `Function`, leading to a crash or data corruption.


There is a *compiler directive* `nonecheck` which turns on checks
for this, at the cost of decreased speed. Here’s how compiler directives
are used to dynamically switch on or off `nonecheck`:



Pure PythonCython
nonecheck.py[¶](#id6 "Permalink to this code")

```
# cython: nonecheck=True
# ^^^ Turns on nonecheck globally

import cython

@cython.cclass
class MyClass:
    pass

# Turn off nonecheck locally for the function
@cython.nonecheck(False)
def func():
    obj: MyClass = None
    try:
        # Turn nonecheck on again for a block
        with cython.nonecheck(True):
            print(obj.myfunc())  # Raises exception
    except AttributeError:
        pass
    print(obj.myfunc())  # Hope for a crash!

```




nonecheck.pyx[¶](#id7 "Permalink to this code")

```
# cython: nonecheck=True
# ^^^ Turns on nonecheck globally

import cython


cdef class MyClass:
    pass

# Turn off nonecheck locally for the function
@cython.nonecheck(False)
def func():
    cdef MyClass obj = None
    try:
        # Turn nonecheck on again for a block
        with cython.nonecheck(True):
            print(obj.myfunc())  # Raises exception
    except AttributeError:
        pass
    print(obj.myfunc())  # Hope for a crash!

```




Attributes in cdef classes behave differently from attributes in regular classes:


* All attributes must be pre-declared at compile-time
* Attributes are by default only accessible from Cython (typed access)
* Properties can be declared to expose dynamic attributes to Python-space



Pure PythonCython
wave\_function.py[¶](#id8 "Permalink to this code")

```
from cython.cimports.sin\_of\_square import Function

@cython.cclass
class WaveFunction(Function):

    # Not available in Python-space:
    offset: float

    # Available in Python-space:
    freq = cython.declare(cython.double, visibility='public')

    # Available in Python-space, but only for reading:
    scale = cython.declare(cython.double, visibility='readonly')

    # Available in Python-space:
    @property
    def period(self):
        return 1.0 / self.freq

    @period.setter
    def period(self, value):
        self.freq = 1.0 / value

```




wave\_function.pyx[¶](#id9 "Permalink to this code")

```
from sin\_of\_square cimport Function


cdef class WaveFunction(Function):

    # Not available in Python-space:
    cdef double offset

    # Available in Python-space:
    cdef public double freq

    # Available in Python-space, but only for reading:
    cdef readonly double scale

    # Available in Python-space:
    @property
    def period(self):
        return 1.0 / self.freq

    @period.setter
    def period(self, value):
        self.freq = 1.0 / value

```






