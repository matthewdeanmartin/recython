

Using C libraries[¶](#using-c-libraries "Permalink to this headline")
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



Apart from writing fast code, one of the main use cases of Cython is
to call external C libraries from Python code. As Cython code
compiles down to C code itself, it is actually trivial to call C
functions directly in the code. The following gives a complete
example for using (and wrapping) an external C library in Cython code,
including appropriate error handling and considerations about
designing a suitable API for Python and Cython code.


Imagine you need an efficient way to store integer values in a FIFO
queue. Since memory really matters, and the values are actually
coming from C code, you cannot afford to create and store Python
`int` objects in a list or deque. So you look out for a queue
implementation in C.


After some web search, you find the C-algorithms library [[CAlg]](#calg) and
decide to use its double ended queue implementation. To make the
handling easier, however, you decide to wrap it in a Python extension
type that can encapsulate all memory management.



[CAlg](#id2)
Simon Howard, C Algorithms library, <https://fragglet.github.io/c-algorithms/>





Defining external declarations[¶](#defining-external-declarations "Permalink to this headline")
-----------------------------------------------------------------------------------------------


You can download CAlg [here](https://codeload.github.com/fragglet/c-algorithms/zip/master).


The C API of the queue implementation, which is defined in the header
file `c-algorithms/src/queue.h`, essentially looks like this:



queue.h[¶](#id9 "Permalink to this code")

```
/\* queue.h \*/

typedef struct \_Queue Queue;
typedef void \*QueueValue;

Queue \*queue\_new(void);
void queue\_free(Queue \*queue);

int queue\_push\_head(Queue \*queue, QueueValue data);
QueueValue queue\_pop\_head(Queue \*queue);
QueueValue queue\_peek\_head(Queue \*queue);

int queue\_push\_tail(Queue \*queue, QueueValue data);
QueueValue queue\_pop\_tail(Queue \*queue);
QueueValue queue\_peek\_tail(Queue \*queue);

int queue\_is\_empty(Queue \*queue);

```



To get started, the first step is to redefine the C API in a `.pxd`
file, say, `cqueue.pxd`:



cqueue.pxd[¶](#id10 "Permalink to this code")

```
cdef extern from "c-algorithms/src/queue.h":
    ctypedef struct Queue:
        pass
    ctypedef void\* QueueValue

    Queue\* queue\_new()
    void queue\_free(Queue\* queue)

    int queue\_push\_head(Queue\* queue, QueueValue data)
    QueueValue  queue\_pop\_head(Queue\* queue)
    QueueValue queue\_peek\_head(Queue\* queue)

    int queue\_push\_tail(Queue\* queue, QueueValue data)
    QueueValue queue\_pop\_tail(Queue\* queue)
    QueueValue queue\_peek\_tail(Queue\* queue)

    bint queue\_is\_empty(Queue\* queue)

```



Note how these declarations are almost identical to the header file
declarations, so you can often just copy them over. However, you do
not need to provide *all* declarations as above, just those that you
use in your code or in other declarations, so that Cython gets to see
a sufficient and consistent subset of them. Then, consider adapting
them somewhat to make them more comfortable to work with in Cython.


Specifically, you should take care of choosing good argument names
for the C functions, as Cython allows you to pass them as keyword
arguments. Changing them later on is a backwards incompatible API
modification. Choosing good names right away will make these
functions more pleasant to work with from Cython code.


One noteworthy difference to the header file that we use above is the
declaration of the `Queue` struct in the first line. `Queue` is
in this case used as an *opaque handle*; only the library that is
called knows what is really inside. Since no Cython code needs to
know the contents of the struct, we do not need to declare its
contents, so we simply provide an empty definition (as we do not want
to declare the `\_Queue` type which is referenced in the C header)
[1](#id4).



[1](#id3)
There’s a subtle difference between `cdef struct Queue: pass`
and `ctypedef struct Queue: pass`. The former declares a
type which is referenced in C code as `struct Queue`, while
the latter is referenced in C as `Queue`. This is a C
language quirk that Cython is not able to hide. Most modern C
libraries use the `ctypedef` kind of struct.




Another exception is the last line. The integer return value of the
`queue\_is\_empty()` function is actually a C boolean value, i.e. the
only interesting thing about it is whether it is non-zero or zero,
indicating if the queue is empty or not. This is best expressed by
Cython’s `bint` type, which is a normal `int` type when used in C
but maps to Python’s boolean values `True` and `False` when
converted to a Python object. This way of tightening declarations in
a `.pxd` file can often simplify the code that uses them.


It is good practice to define one `.pxd` file for each library that
you use, and sometimes even for each header file (or functional group)
if the API is large. That simplifies their reuse in other projects.
Sometimes, you may need to use C functions from the standard C
library, or want to call C-API functions from CPython directly. For
common needs like this, Cython ships with a set of standard `.pxd`
files that provide these declarations in a readily usable way that is
adapted to their use in Cython. The main packages are `cpython`,
`libc` and `libcpp`. The NumPy library also has a standard
`.pxd` file `numpy`, as it is often used in Cython code. See
Cython’s `Cython/Includes/` source package for a complete list of
provided `.pxd` files.




Writing a wrapper class[¶](#writing-a-wrapper-class "Permalink to this headline")
---------------------------------------------------------------------------------


After declaring our C library’s API, we can start to design the Queue
class that should wrap the C queue. It will live in a file called
`queue.pyx`/`queue.py`. [2](#id6)



[2](#id5)
Note that the name of the `.pyx`/`.py` file must be different from
the `cqueue.pxd` file with declarations from the C library,
as both do not describe the same code. A `.pxd` file next to
a `.pyx`/`.py` file with the same name defines exported
declarations for code in the `.pyx`/`.py` file. As the
`cqueue.pxd` file contains declarations of a regular C
library, there must not be a `.pyx`/`.py` file with the same name
that Cython associates with it.




Here is a first start for the Queue class:



Pure PythonCython
queue.py[¶](#id11 "Permalink to this code")

```
from cython.cimports import cqueue

@cython.cclass
class Queue:
    \_c\_queue: cython.pointer(cqueue.Queue)

    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()

```




queue.pyx[¶](#id12 "Permalink to this code")

```
cimport cqueue


cdef class Queue:
    cdef cqueue.Queue* \_c\_queue

    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()

```




Note that it says `\_\_cinit\_\_` rather than `\_\_init\_\_`. While
`\_\_init\_\_` is available as well, it is not guaranteed to be run (for
instance, one could create a subclass and forget to call the
ancestor’s constructor). Because not initializing C pointers often
leads to hard crashes of the Python interpreter, Cython provides
`\_\_cinit\_\_` which is *always* called immediately on construction,
before CPython even considers calling `\_\_init\_\_`, and which
therefore is the right place to initialise static attributes
(`cdef` fields) of the new instance. However, as `\_\_cinit\_\_` is
called during object construction, `self` is not fully constructed yet,
and one must avoid doing anything with `self` but assigning to static
attributes (`cdef` fields).


Note also that the above method takes no parameters, although subtypes
may want to accept some. A no-arguments `\_\_cinit\_\_()` method is a
special case here that simply does not receive any parameters that
were passed to a constructor, so it does not prevent subclasses from
adding parameters. If parameters are used in the signature of
`\_\_cinit\_\_()`, they must match those of any declared `\_\_init\_\_`
method of classes in the class hierarchy that are used to instantiate
the type.




Memory management[¶](#memory-management "Permalink to this headline")
---------------------------------------------------------------------


Before we continue implementing the other methods, it is important to
understand that the above implementation is not safe. In case
anything goes wrong in the call to `queue\_new()`, this code will
simply swallow the error, so we will likely run into a crash later on.
According to the documentation of the `queue\_new()` function, the
only reason why the above can fail is due to insufficient memory. In
that case, it will return `NULL`, whereas it would normally return a
pointer to the new queue.


The Python way to get out of this is to raise a `MemoryError` [3](#id8).
We can thus change the init function as follows:



Pure PythonCython
queue.py[¶](#id13 "Permalink to this code")

```
from cython.cimports import cqueue

@cython.cclass
class Queue:
    \_c\_queue = cython.declare(cython.pointer(cqueue.Queue))

    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()
        if self.\_c\_queue is cython.NULL:
            raise MemoryError()

```




queue.pyx[¶](#id14 "Permalink to this code")

```
cimport cqueue


cdef class Queue:
    cdef cqueue.Queue* \_c\_queue

    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()
        if self.\_c\_queue is NULL:
            raise MemoryError()

```





[3](#id7)
In the specific case of a `MemoryError`, creating a new
exception instance in order to raise it may actually fail because
we are running out of memory. Luckily, CPython provides a C-API
function `PyErr\_NoMemory()` that safely raises the right
exception for us. Cython automatically
substitutes this C-API call whenever you write `raise
MemoryError` or `raise MemoryError()`. If you use an older
version, you have to cimport the C-API function from the standard
package `cpython.exc` and call it directly.




The next thing to do is to clean up when the Queue instance is no
longer used (i.e. all references to it have been deleted). To this
end, CPython provides a callback that Cython makes available as a
special method `\_\_dealloc\_\_()`. In our case, all we have to do is
to free the C Queue, but only if we succeeded in initialising it in
the init method:



Pure PythonCython
```
def \_\_dealloc\_\_(self):
    if self.\_c\_queue is not cython.NULL:
        cqueue.queue\_free(self.\_c\_queue)

```



```
def \_\_dealloc\_\_(self):
    if self.\_c\_queue is not NULL:
        cqueue.queue\_free(self.\_c\_queue)

```





Compiling and linking[¶](#compiling-and-linking "Permalink to this headline")
-----------------------------------------------------------------------------


At this point, we have a working Cython module that we can test. To
compile it, we need to configure a `setup.py` script for setuptools.
Here is the most basic script for compiling a Cython module



Pure PythonCython
```
from setuptools import Extension, setup
from Cython.Build import cythonize

setup(
    ext\_modules = cythonize([Extension("queue", ["queue.py"])])
)

```



```
from setuptools import Extension, setup
from Cython.Build import cythonize

setup(
    ext\_modules = cythonize([Extension("queue", ["queue.pyx"])])
)

```



To build against the external C library, we need to make sure Cython finds the necessary libraries.
There are two ways to archive this. First we can tell setuptools where to find
the c-source to compile the `queue.c` implementation automatically. Alternatively,
we can build and install C-Alg as system library and dynamically link it. The latter is useful
if other applications also use C-Alg.



### Static Linking[¶](#static-linking "Permalink to this headline")


To build the c-code automatically we need to include compiler directives in `queue.pyx`/`queue.py`



Pure PythonCython
```
# distutils: sources = c-algorithms/src/queue.c
# distutils: include\_dirs = c-algorithms/src/

import cython
from cython.cimports import cqueue

@cython.cclass
class Queue:
    \_c\_queue = cython.declare(cython.pointer(cqueue.Queue))

    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()
        if self.\_c\_queue is cython.NULL:
            raise MemoryError()

    def \_\_dealloc\_\_(self):
        if self.\_c\_queue is not cython.NULL:
            cqueue.queue\_free(self.\_c\_queue)

```



```
# distutils: sources = c-algorithms/src/queue.c
# distutils: include\_dirs = c-algorithms/src/


cimport cqueue


cdef class Queue:
    cdef cqueue.Queue* \_c\_queue

    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()
        if self.\_c\_queue is NULL:
            raise MemoryError()

    def \_\_dealloc\_\_(self):
        if self.\_c\_queue is not NULL:
            cqueue.queue\_free(self.\_c\_queue)

```



The `sources` compiler directive gives the path of the C
files that setuptools is going to compile and
link (statically) into the resulting extension module.
In general all relevant header files should be found in `include\_dirs`.
Now we can build the project using:



```
$ python setup.py build_ext -i

```


And test whether our build was successful:



```
$ python -c 'import queue; Q = queue.Queue()'

```




### Dynamic Linking[¶](#dynamic-linking "Permalink to this headline")


Dynamic linking is useful, if the library we are going to wrap is already
installed on the system. To perform dynamic linking we first need to
build and install c-alg.


To build c-algorithms on your system:



```
$ cd c-algorithms
$ sh autogen.sh
$ ./configure
$ make

```


to install CAlg run:



```
$ make install

```


Afterwards the file `/usr/local/lib/libcalg.so` should exist.



Note


This path applies to Linux systems and may be different on other platforms,
so you will need to adapt the rest of the tutorial depending on the path
where `libcalg.so` or `libcalg.dll` is on your system.



In this approach we need to tell the setup script to link with an external library.
To do so we need to extend the setup script to install change the extension setup from



Pure PythonCython
```
ext\_modules = cythonize([Extension("queue", ["queue.py"])])

```



```
ext\_modules = cythonize([Extension("queue", ["queue.pyx"])])

```



to



Pure PythonCython
```
ext\_modules = cythonize([
    Extension("queue", ["queue.py"],
              libraries=["calg"])
    ])

```



```
ext\_modules = cythonize([
    Extension("queue", ["queue.pyx"],
              libraries=["calg"])
    ])

```



Now we should be able to build the project using:



```
$ python setup.py build_ext -i

```


If the libcalg is not installed in a ‘normal’ location, users can provide the
required parameters externally by passing appropriate C compiler
flags, such as:



```
CFLAGS="-I/usr/local/otherdir/calg/include" \
LDFLAGS="-L/usr/local/otherdir/calg/lib" \
 python setup.py build_ext -i

```


Before we run the module, we also need to make sure that libcalg is in
the LD\_LIBRARY\_PATH environment variable, e.g. by setting:



```
$ export LD\_LIBRARY\_PATH=$LD\_LIBRARY\_PATH:/usr/local/lib

```


Once we have compiled the module for the first time, we can now import
it and instantiate a new Queue:



```
$ export PYTHONPATH=.
$ python -c 'import queue; Q = queue.Queue()'

```


However, this is all our Queue class can do so far, so let’s make it
more usable.




### Mapping functionality[¶](#mapping-functionality "Permalink to this headline")


Before implementing the public interface of this class, it is good
practice to look at what interfaces Python offers, e.g. in its
`list` or `collections.deque` classes. Since we only need a FIFO
queue, it’s enough to provide the methods `append()`, `peek()` and
`pop()`, and additionally an `extend()` method to add multiple
values at once. Also, since we already know that all values will be
coming from C, it’s best to provide only `cdef`/`@cfunc` methods for now, and
to give them a straight C interface.


In C, it is common for data structures to store data as a `void\*` to
whatever data item type. Since we only want to store `int` values,
which usually fit into the size of a pointer type, we can avoid
additional memory allocations through a trick: we cast our `int` values
to `void\*` and vice versa, and store the value directly as the
pointer value.


Here is a simple implementation for the `append()` method:



Pure PythonCython
```
@cython.cfunc
def append(self, value: cython.int):
    cqueue.queue\_push\_tail(self.\_c\_queue, cython.cast(cython.p\_void, value))

```



```
cdef append(self, int value):
    cqueue.queue\_push\_tail(self.\_c\_queue, <void\*>value)

```



Again, the same error handling considerations as for the
`\_\_cinit\_\_()` method apply, so that we end up with this
implementation instead:



Pure PythonCython
```
@cython.cfunc
def append(self, value: cython.int):
    if not cqueue.queue\_push\_tail(self.\_c\_queue,
                                  cython.cast(cython.p\_void, value)):
        raise MemoryError()

```



```
cdef append(self, int value):
    if not cqueue.queue\_push\_tail(self.\_c\_queue,
                                  <void\*>value):
        raise MemoryError()

```



Adding an `extend()` method should now be straight forward:



Pure PythonCython
```
@cython.cfunc
def extend(self, values: cython.p\_int, count: cython.size\_t):
 """Append all ints to the queue.
 """
    value: cython.int
    for value in values[:count]:  # Slicing pointer to limit the iteration boundaries.
        self.append(value)

```



```
cdef extend(self, int\* values, size\_t count):
 """Append all ints to the queue.
 """
    cdef int value
    for value in values[:count]:  # Slicing pointer to limit the iteration boundaries.
        self.append(value)

```



This becomes handy when reading values from a C array, for example.


So far, we can only add data to the queue. The next step is to write
the two methods to get the first element: `peek()` and `pop()`,
which provide read-only and destructive read access respectively.
To avoid compiler warnings when casting `void\*` to `int` directly,
we use an intermediate data type that is big enough to hold a `void\*`.
Here, `Py\_ssize\_t`:



Pure PythonCython
```
@cython.cfunc
def peek(self) -> cython.int:
    return cython.cast(cython.Py\_ssize\_t, cqueue.queue\_peek\_head(self.\_c\_queue))

@cython.cfunc
def pop(self) -> cython.int:
    return cython.cast(cython.Py\_ssize\_t, cqueue.queue\_pop\_head(self.\_c\_queue))

```



```
cdef int peek(self):
    return <Py\_ssize\_t>cqueue.queue\_peek\_head(self.\_c\_queue)

cdef int pop(self):
    return <Py\_ssize\_t>cqueue.queue\_pop\_head(self.\_c\_queue)

```



Normally, in C, we risk losing data when we convert a larger integer type
to a smaller integer type without checking the boundaries, and `Py\_ssize\_t`
may be a larger type than `int`. But since we control how values are added
to the queue, we already know that all values that are in the queue fit into
an `int`, so the above conversion from `void\*` to `Py\_ssize\_t` to `int`
(the return type) is safe by design.




### Handling errors[¶](#handling-errors "Permalink to this headline")


Now, what happens when the queue is empty? According to the
documentation, the functions return a `NULL` pointer, which is
typically not a valid value. But since we are simply casting to and
from ints, we cannot distinguish anymore if the return value was
`NULL` because the queue was empty or because the value stored in
the queue was `0`. In Cython code, we want the first case to
raise an exception, whereas the second case should simply return
`0`. To deal with this, we need to special case this value,
and check if the queue really is empty or not:



Pure PythonCython
```
@cython.cfunc
def peek(self) -> cython.int:
    value: cython.int = cython.cast(cython.Py\_ssize\_t, cqueue.queue\_peek\_head(self.\_c\_queue))
    if value == 0:
        # this may mean that the queue is empty, or
        # that it happens to contain a 0 value
        if cqueue.queue\_is\_empty(self.\_c\_queue):
            raise IndexError("Queue is empty")
    return value

```



```
cdef int peek(self):
    cdef int value = <Py\_ssize\_t>cqueue.queue\_peek\_head(self.\_c\_queue)
    if value == 0:
        # this may mean that the queue is empty, or
        # that it happens to contain a 0 value
        if cqueue.queue\_is\_empty(self.\_c\_queue):
            raise IndexError("Queue is empty")
    return value

```



Note how we have effectively created a fast path through the method in
the hopefully common cases that the return value is not `0`. Only
that specific case needs an additional check if the queue is empty.


If the `peek` function was a Python function returning a
Python object value, CPython would simply return `NULL` internally
instead of a Python object to indicate an exception, which would
immediately be propagated by the surrounding code. The problem is
that the return type is `int` and any `int` value is a valid queue
item value, so there is no way to explicitly signal an error to the
calling code.


The only way calling code can deal with this situation is to call
`PyErr\_Occurred()` when returning from a function to check if an
exception was raised, and if so, propagate the exception. This
obviously has a performance penalty. Cython therefore uses a dedicated value
that it implicitly returns in the case of an
exception, so that the surrounding code only needs to check for an
exception when receiving this exact value.


By default, the value `-1` is used as the exception return value.
All other return values will be passed through almost
without a penalty, thus again creating a fast path for ‘normal’
values. See [Error return values](../userguide/language_basics.html#error-return-values) for more details.


Now that the `peek()` method is implemented, the `pop()` method
also needs adaptation. Since it removes a value from the queue,
however, it is not enough to test if the queue is empty *after* the
removal. Instead, we must test it on entry:



Pure PythonCython
```
@cython.cfunc
def pop(self) -> cython.int:
    if cqueue.queue\_is\_empty(self.\_c\_queue):
        raise IndexError("Queue is empty")
    return cython.cast(cython.Py\_ssize\_t, cqueue.queue\_pop\_head(self.\_c\_queue))

```



```
cdef int pop(self):
    if cqueue.queue\_is\_empty(self.\_c\_queue):
        raise IndexError("Queue is empty")
    return <Py\_ssize\_t>cqueue.queue\_pop\_head(self.\_c\_queue)

```



The return value for exception propagation is declared exactly as for
`peek()`.


Lastly, we can provide the Queue with an emptiness indicator in the
normal Python way by implementing the `\_\_bool\_\_()` special method
(note that Python 2 calls this method `\_\_nonzero\_\_`, whereas Cython
code can use either name):



```
def \_\_bool\_\_(self):
    return not cqueue.queue\_is\_empty(self.\_c\_queue)

```


Note that this method returns either `True` or `False` as we
declared the return type of the `queue\_is\_empty()` function as
`bint` in `cqueue.pxd`.




### Testing the result[¶](#testing-the-result "Permalink to this headline")


Now that the implementation is complete, you may want to write some
tests for it to make sure it works correctly. Especially doctests are
very nice for this purpose, as they provide some documentation at the
same time. To enable doctests, however, you need a Python API that
you can call. C methods are not visible from Python code, and thus
not callable from doctests.


A quick way to provide a Python API for the class is to change the
methods from `cdef`/`@cfunc` to `cpdef`/`@ccall`. This will
let Cython generate two entry points, one that is callable from normal
Python code using the Python call semantics and Python objects as arguments,
and one that is callable from C code with fast C semantics and without requiring
intermediate argument conversion from or to Python types. Note that
`cpdef`/`@ccall` methods ensure that they can be appropriately overridden
by Python methods even when they are called from Cython. This adds a tiny overhead
compared to `cdef`/`@cfunc` methods.


Now that we have both a C-interface and a Python interface for our
class, we should make sure that both interfaces are consistent.
Python users would expect an `extend()` method that accepts arbitrary
iterables, whereas C users would like to have one that allows passing
C arrays and C memory. Both signatures are incompatible.


We will solve this issue by considering that in C, the API could also
want to support other input types, e.g. arrays of `long` or `char`,
which is usually supported with differently named C API functions such as
`extend\_ints()`, `extend\_longs()`, `extend\_chars()`, etc. This allows
us to free the method name `extend()` for the duck typed Python method,
which can accept arbitrary iterables.


The following listing shows the complete implementation that uses
`cpdef`/`@ccall` methods where possible:



Pure PythonCython
queue.py[¶](#id15 "Permalink to this code")

```
from cython.cimports import cqueue
from cython import cast

@cython.cclass
class Queue:
 """A queue class for C integer values.

 >>> q = Queue()
 >>> q.append(5)
 >>> q.peek()
 5
 >>> q.pop()
 5
 """
    \_c\_queue = cython.declare(cython.pointer(cqueue.Queue))
    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()
        if self.\_c\_queue is cython.NULL:
            raise MemoryError()

    def \_\_dealloc\_\_(self):
        if self.\_c\_queue is not cython.NULL:
            cqueue.queue\_free(self.\_c\_queue)

    @cython.ccall
    def append(self, value: cython.int):
        if not cqueue.queue\_push\_tail(self.\_c\_queue,
                cast(cython.p\_void, cast(cython.Py\_ssize\_t, value))):
            raise MemoryError()

    # The `cpdef` feature is obviously not available for the original "extend()"
    # method, as the method signature is incompatible with Python argument
    # types (Python does not have pointers). However, we can rename
    # the C-ish "extend()" method to e.g. "extend\_ints()", and write
    # a new "extend()" method that provides a suitable Python interface by
    # accepting an arbitrary Python iterable.
    @cython.ccall
    def extend(self, values):
        for value in values:
            self.append(value)

    @cython.cfunc
    def extend\_ints(self, values: cython.p\_int, count: cython.size\_t):
        value: cython.int
        for value in values[:count]:  # Slicing pointer to limit the iteration boundaries.
            self.append(value)

    @cython.ccall
    @cython.exceptval(-1, check=True)
    def peek(self) -> cython.int:
        value: cython.int = cast(cython.Py\_ssize\_t, cqueue.queue\_peek\_head(self.\_c\_queue))

        if value == 0:
            # this may mean that the queue is empty,
            # or that it happens to contain a 0 value
            if cqueue.queue\_is\_empty(self.\_c\_queue):
                raise IndexError("Queue is empty")
        return value

    @cython.ccall
    @cython.exceptval(-1, check=True)
    def pop(self) -> cython.int:
        if cqueue.queue\_is\_empty(self.\_c\_queue):
            raise IndexError("Queue is empty")
        return cast(cython.Py\_ssize\_t, cqueue.queue\_pop\_head(self.\_c\_queue))

    def \_\_bool\_\_(self):
        return not cqueue.queue\_is\_empty(self.\_c\_queue)

```




queue.pyx[¶](#id16 "Permalink to this code")

```
cimport cqueue



cdef class Queue:
 """A queue class for C integer values.

 >>> q = Queue()
 >>> q.append(5)
 >>> q.peek()
 5
 >>> q.pop()
 5
 """
    cdef cqueue.Queue* \_c\_queue
    def \_\_cinit\_\_(self):
        self.\_c\_queue = cqueue.queue\_new()
        if self.\_c\_queue is NULL:
            raise MemoryError()

    def \_\_dealloc\_\_(self):
        if self.\_c\_queue is not NULL:
            cqueue.queue\_free(self.\_c\_queue)


    cpdef append(self, int value):
        if not cqueue.queue\_push\_tail(self.\_c\_queue,
                                      <void\*> <Py\_ssize\_t> value):
            raise MemoryError()

    # The `cpdef` feature is obviously not available for the original "extend()"
    # method, as the method signature is incompatible with Python argument
    # types (Python does not have pointers). However, we can rename
    # the C-ish "extend()" method to e.g. "extend\_ints()", and write
    # a new "extend()" method that provides a suitable Python interface by
    # accepting an arbitrary Python iterable.

    cpdef extend(self, values):
        for value in values:
            self.append(value)


    cdef extend\_ints(self, int\* values, size\_t count):
        cdef int value
        for value in values[:count]:  # Slicing pointer to limit the iteration boundaries.
            self.append(value)



    cpdef int peek(self) except? -1:
        cdef int value = <Py\_ssize\_t> cqueue.queue\_peek\_head(self.\_c\_queue)

        if value == 0:
            # this may mean that the queue is empty,
            # or that it happens to contain a 0 value
            if cqueue.queue\_is\_empty(self.\_c\_queue):
                raise IndexError("Queue is empty")
        return value



    cpdef int pop(self) except? -1:
        if cqueue.queue\_is\_empty(self.\_c\_queue):
            raise IndexError("Queue is empty")
        return <Py\_ssize\_t> cqueue.queue\_pop\_head(self.\_c\_queue)

    def \_\_bool\_\_(self):
        return not cqueue.queue\_is\_empty(self.\_c\_queue)

```




Now we can test our Queue implementation using a python script,
for example here `test\_queue.py`:



```
from \_\_future\_\_ import print\_function

import time

import queue

Q = queue.Queue()

Q.append(10)
Q.append(20)
print(Q.peek())
print(Q.pop())
print(Q.pop())
try:
    print(Q.pop())
except IndexError as e:
    print("Error message:", e)  # Prints "Queue is empty"

i = 10000

values = range(i)

start\_time = time.time()

Q.extend(values)

end\_time = time.time() - start\_time

print("Adding {} items took {:1.3f} msecs.".format(i, 1000 \* end\_time))

for i in range(41):
    Q.pop()

Q.pop()
print("The answer is:")
print(Q.pop())

```


As a quick test with 10000 numbers on the author’s machine indicates,
using this Queue from Cython code with C `int` values is about five
times as fast as using it from Cython code with Python object values,
almost eight times faster than using it from Python code in a Python
loop, and still more than twice as fast as using Python’s highly
optimised `collections.deque` type from Cython code with Python
integers.




### Callbacks[¶](#callbacks "Permalink to this headline")


Let’s say you want to provide a way for users to pop values from the
queue up to a certain user defined event occurs. To this end, you
want to allow them to pass a predicate function that determines when
to stop, e.g.:



```
def pop\_until(self, predicate):
    while not predicate(self.peek()):
        self.pop()

```


Now, let us assume for the sake of argument that the C queue
provides such a function that takes a C callback function as
predicate. The API could look as follows:



```
/\* C type of a predicate function that takes a queue value and returns
 \* -1 for errors
 \*  0 for reject
 \*  1 for accept
 \*/
typedef int (\*predicate\_func)(void\* user\_context, QueueValue data);

/\* Pop values as long as the predicate evaluates to true for them,
 \* returns -1 if the predicate failed with an error and 0 otherwise.
 \*/
int queue\_pop\_head\_until(Queue \*queue, predicate\_func predicate,
                         void\* user\_context);

```


It is normal for C callback functions to have a generic `void\*`
argument that allows passing any kind of context or state through the
C-API into the callback function. We will use this to pass our Python
predicate function.


First, we have to define a callback function with the expected
signature that we can pass into the C-API function:



Pure PythonCython
```
@cython.cfunc
@cython.exceptval(check=False)
def evaluate\_predicate(context: cython.p\_void, value: cqueue.QueueValue) -> cython.int:
    "Callback function that can be passed as predicate\_func"
    try:
        # recover Python function object from void\* argument
        func = cython.cast(object, context)
        # call function, convert result into 0/1 for True/False
        return bool(func(cython.cast(int, value)))
    except:
        # catch any Python errors and return error indicator
        return -1

```



Note


`@cfunc` functions in pure python are defined as `@exceptval(-1, check=True)`
by default. Since `evaluate\_predicate()` should be passed to function as parameter,
we need to turn off exception checking entirely.




```
cdef int evaluate\_predicate(void\* context, cqueue.QueueValue value):
    "Callback function that can be passed as predicate\_func"
    try:
        # recover Python function object from void\* argument
        func = <object>context
        # call function, convert result into 0/1 for True/False
        return bool(func(<int>value))
    except:
        # catch any Python errors and return error indicator
        return -1

```



The main idea is to pass a pointer (a.k.a. borrowed reference) to the
function object as the user context argument. We will call the C-API
function as follows:



Pure PythonCython
```
def pop\_until(self, python\_predicate\_function):
    result = cqueue.queue\_pop\_head\_until(
        self.\_c\_queue, evaluate\_predicate,
        cython.cast(cython.p\_void, python\_predicate\_function))
    if result == -1:
        raise RuntimeError("an error occurred")

```



```
def pop\_until(self, python\_predicate\_function):
    result = cqueue.queue\_pop\_head\_until(
        self.\_c\_queue, evaluate\_predicate,
        <void\*>python\_predicate\_function)
    if result == -1:
        raise RuntimeError("an error occurred")

```



The usual pattern is to first cast the Python object reference into
a `void\*` to pass it into the C-API function, and then cast
it back into a Python object in the C predicate callback function.
The cast to `void\*` creates a borrowed reference. On the cast
to `<object>`, Cython increments the reference count of the object
and thus converts the borrowed reference back into an owned reference.
At the end of the predicate function, the owned reference goes out
of scope again and Cython discards it.


The error handling in the code above is a bit simplistic. Specifically,
any exceptions that the predicate function raises will essentially be
discarded and only result in a plain `RuntimeError()` being raised
after the fact. This can be improved by storing away the exception
in an object passed through the context parameter and re-raising it
after the C-API function has returned `-1` to indicate the error.






