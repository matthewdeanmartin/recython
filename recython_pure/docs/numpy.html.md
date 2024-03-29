

Working with NumPy[¶](#working-with-numpy "Permalink to this headline")
=======================================================================



Note


Cython 0.16 introduced typed memoryviews as a successor to the NumPy
integration described here. They are easier to use than the buffer syntax
below, have less overhead, and can be passed around without requiring the GIL.
They should be preferred to the syntax presented in this page.
See [Cython for NumPy users](../userguide/numpy_tutorial.html#numpy-tutorial).



You can use NumPy from Cython exactly the same as in regular Python, but by
doing so you are losing potentially high speedups because Cython has support
for fast access to NumPy arrays. Let’s see how this works with a simple
example.


The code below does 2D discrete convolution of an image with a filter (and I’m
sure you can do better!, let it serve for demonstration purposes). It is both
valid Python and valid Cython code. I’ll refer to it as both
`convolve\_py.py` for the Python version and `convolve1.pyx` for
the Cython version – Cython uses “.pyx” as its file suffix.



```
import numpy as np


def naive\_convolve(f, g):
    # f is an image and is indexed by (v, w)
    # g is a filter kernel and is indexed by (s, t),
    # it needs odd dimensions
    # h is the output image and is indexed by (x, y),
    # it is not cropped
    if g.shape[0] % 2 != 1 or g.shape[1] % 2 != 1:
        raise ValueError("Only odd dimensions on filter supported")
    # smid and tmid are number of pixels between the center pixel
    # and the edge, ie for a 5x5 filter they will be 2.
    #
    # The output size is calculated by adding smid, tmid to each
    # side of the dimensions of the input image.
    vmax = f.shape[0]
    wmax = f.shape[1]
    smax = g.shape[0]
    tmax = g.shape[1]
    smid = smax // 2
    tmid = tmax // 2
    xmax = vmax + 2 \* smid
    ymax = wmax + 2 \* tmid
    # Allocate result image.
    h = np.zeros([xmax, ymax], dtype=f.dtype)
    # Do convolution
    for x in range(xmax):
        for y in range(ymax):
            # Calculate pixel value for h at (x,y). Sum one component
            # for each pixel (s, t) of the filter g.
            s\_from = max(smid - x, -smid)
            s\_to = min((xmax - x) - smid, smid + 1)
            t\_from = max(tmid - y, -tmid)
            t\_to = min((ymax - y) - tmid, tmid + 1)
            value = 0
            for s in range(s\_from, s\_to):
                for t in range(t\_from, t\_to):
                    v = x - smid + s
                    w = y - tmid + t
                    value += g[smid - s, tmid - t] \* f[v, w]
            h[x, y] = value
    return h

```


This should be compiled to produce `yourmod.so` (for Linux systems, on Windows
systems, it will be `yourmod.pyd`). We
run a Python session to test both the Python version (imported from
`.py`-file) and the compiled Cython module.



```
In [1]: import numpy as np
In [2]: import convolve\_py
In [3]: convolve\_py.naive\_convolve(np.array([[1, 1, 1]], dtype=np.int64),
... np.array([[1],[2],[1]], dtype=np.int64))
Out [3]:
array([[1, 1, 1],
 [2, 2, 2],
 [1, 1, 1]])
In [4]: import convolve1
In [4]: convolve1.naive\_convolve(np.array([[1, 1, 1]], dtype=np.int64),
... np.array([[1],[2],[1]], dtype=np.int64))
Out [4]:
array([[1, 1, 1],
 [2, 2, 2],
 [1, 1, 1]])
In [11]: N = 100
In [12]: f = np.arange(N\*N, dtype=np.int64).reshape((N,N))
In [13]: g = np.arange(81, dtype=np.int64).reshape((9, 9))
In [19]: %timeit -n2 -r3 convolve_py.naive_convolve(f, g)
2 loops, best of 3: 1.86 s per loop
In [20]: %timeit -n2 -r3 convolve1.naive_convolve(f, g)
2 loops, best of 3: 1.41 s per loop

```


There’s not such a huge difference yet; because the C code still does exactly
what the Python interpreter does (meaning, for instance, that a new object is
allocated for each number used). Look at the generated html file and see what
is needed for even the simplest statements you get the point quickly. We need
to give Cython more information; we need to add types.



Adding types[¶](#adding-types "Permalink to this headline")
-----------------------------------------------------------


To add types we use custom Cython syntax, so we are now breaking Python source
compatibility. Consider this code (*read the comments!*) :



```
# tag: numpy
# You can ignore the previous line.
# It's for internal testing of the cython documentation.

import numpy as np

# "cimport" is used to import special compile-time information
# about the numpy module (this is stored in a file numpy.pxd which is
# distributed with Numpy).
# Here we've used the name "cnp" to make it easier to understand what
# comes from the cimported module and what comes from the imported module,
# however you can use the same name for both if you wish.
cimport numpy as cnp

# It's necessary to call "import\_array" if you use any part of the
# numpy PyArray\_\* API. From Cython 3, accessing attributes like
# ".shape" on a typed Numpy array use this API. Therefore we recommend
# always calling "import\_array" whenever you "cimport numpy"
cnp.import\_array()

# We now need to fix a datatype for our arrays. I've used the variable
# DTYPE for this, which is assigned to the usual NumPy runtime
# type info object.
DTYPE = np.int64

# "ctypedef" assigns a corresponding compile-time type to DTYPE\_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a \_t-suffix.
ctypedef cnp.int64\_t DTYPE\_t

# "def" can type its arguments but not have a return type. The type of the
# arguments for a "def" function is checked at run-time when entering the
# function.
#
# The arrays f, g and h is typed as "np.ndarray" instances. The only effect
# this has is to a) insert checks that the function arguments really are
# NumPy arrays, and b) make some attribute access like f.shape[0] much
# more efficient. (In this example this doesn't matter though.)
def naive\_convolve(cnp.ndarray f, cnp.ndarray g):
    if g.shape[0] % 2 != 1 or g.shape[1] % 2 != 1:
        raise ValueError("Only odd dimensions on filter supported")
    assert f.dtype == DTYPE and g.dtype == DTYPE

    # The "cdef" keyword is also used within functions to type variables. It
    # can only be used at the top indentation level (there are non-trivial
    # problems with allowing them in other places, though we'd love to see
    # good and thought out proposals for it).
    #
    # For the indices, the "int" type is used. This corresponds to a C int,
    # other C types (like "unsigned int") could have been used instead.
    # Purists could use "Py\_ssize\_t" which is the proper Python type for
    # array indices.
    cdef int vmax = f.shape[0]
    cdef int wmax = f.shape[1]
    cdef int smax = g.shape[0]
    cdef int tmax = g.shape[1]
    cdef int smid = smax // 2
    cdef int tmid = tmax // 2
    cdef int xmax = vmax + 2 \* smid
    cdef int ymax = wmax + 2 \* tmid
    cdef cnp.ndarray h = np.zeros([xmax, ymax], dtype=DTYPE)
    cdef int x, y, s, t, v, w

    # It is very important to type ALL your variables. You do not get any
    # warnings if not, only much slower code (they are implicitly typed as
    # Python objects).
    cdef int s\_from, s\_to, t\_from, t\_to

    # For the value variable, we want to use the same data type as is
    # stored in the array, so we use "DTYPE\_t" as defined above.
    # NB! An important side-effect of this is that if "value" overflows its
    # datatype size, it will simply wrap around like in C, rather than raise
    # an error like in Python.
    cdef DTYPE\_t value
    for x in range(xmax):
        for y in range(ymax):
            s\_from = max(smid - x, -smid)
            s\_to = min((xmax - x) - smid, smid + 1)
            t\_from = max(tmid - y, -tmid)
            t\_to = min((ymax - y) - tmid, tmid + 1)
            value = 0
            for s in range(s\_from, s\_to):
                for t in range(t\_from, t\_to):
                    v = x - smid + s
                    w = y - tmid + t
                    value += g[smid - s, tmid - t] \* f[v, w]
            h[x, y] = value
    return h

```


After building this and continuing my (very informal) benchmarks, I get:



```
In [21]: import convolve2
In [22]: %timeit -n2 -r3 convolve2.naive_convolve(f, g)
2 loops, best of 3: 828 ms per loop

```




Efficient indexing[¶](#efficient-indexing "Permalink to this headline")
-----------------------------------------------------------------------


There’s still a bottleneck killing performance, and that is the array lookups
and assignments. The `[]`-operator still uses full Python operations –
what we would like to do instead is to access the data buffer directly at C
speed.


What we need to do then is to type the contents of the `ndarray` objects.
We do this with a special “buffer” syntax which must be told the datatype
(first argument) and number of dimensions (“ndim” keyword-only argument, if
not provided then one-dimensional is assumed).


These are the needed changes:



```
...
def naive\_convolve(cnp.ndarray[DTYPE\_t, ndim=2] f, cnp.ndarray[DTYPE\_t, ndim=2] g):
...
cdef cnp.ndarray[DTYPE\_t, ndim=2] h = ...

```


Usage:



```
In [18]: import convolve3
In [19]: %timeit -n3 -r100 convolve3.naive_convolve(f, g)
3 loops, best of 100: 11.6 ms per loop

```


Note the importance of this change.


*Gotcha*: This efficient indexing only affects certain index operations,
namely those with exactly `ndim` number of typed integer indices. So if
`v` for instance isn’t typed, then the lookup `f[v, w]` isn’t
optimized. On the other hand this means that you can continue using Python
objects for sophisticated dynamic slicing etc. just as when the array is not
typed.




Tuning indexing further[¶](#tuning-indexing-further "Permalink to this headline")
---------------------------------------------------------------------------------


The array lookups are still slowed down by two factors:


1. Bounds checking is performed.
2. Negative indices are checked for and handled correctly. The code above is
explicitly coded so that it doesn’t use negative indices, and it
(hopefully) always access within bounds. We can add a decorator to disable
bounds checking:



```
...
cimport cython
@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def naive\_convolve(cnp.ndarray[DTYPE\_t, ndim=2] f, cnp.ndarray[DTYPE\_t, ndim=2] g):
...

```


Now bounds checking is not performed (and, as a side-effect, if you ‘’do’’
happen to access out of bounds you will in the best case crash your program
and in the worst case corrupt data). It is possible to switch bounds-checking
mode in many ways, see [Compiler directives](../userguide/source_files_and_compilation.html#compiler-directives) for more
information.


Also, we’ve disabled the check to wrap negative indices (e.g. g[-1] giving
the last value). As with disabling bounds checking, bad things will happen
if we try to actually use negative indices with this disabled.


The function call overhead now starts to play a role, so we compare the latter
two examples with larger N:



```
In [11]: %timeit -n3 -r100 convolve4.naive_convolve(f, g)
3 loops, best of 100: 5.97 ms per loop
In [12]: N = 1000
In [13]: f = np.arange(N\*N, dtype=np.int64).reshape((N,N))
In [14]: g = np.arange(81, dtype=np.int64).reshape((9, 9))
In [17]: %timeit -n1 -r10 convolve3.naive_convolve(f, g)
1 loops, best of 10: 1.16 s per loop
In [18]: %timeit -n1 -r10 convolve4.naive_convolve(f, g)
1 loops, best of 10: 597 ms per loop

```


(Also this is a mixed benchmark as the result array is allocated within the
function call.)



Warning


Speed comes with some cost. Especially it can be dangerous to set typed
objects (like `f`, `g` and `h` in our sample code) to
`None`. Setting such objects to `None` is entirely
legal, but all you can do with them is check whether they are None. All
other use (attribute lookup or indexing) can potentially segfault or
corrupt data (rather than raising exceptions as they would in Python).


The actual rules are a bit more complicated but the main message is clear:
Do not use typed objects without knowing that they are not set to None.





What typing does not do[¶](#what-typing-does-not-do "Permalink to this headline")
---------------------------------------------------------------------------------


The main purpose of typing things as `ndarray` is to allow efficient
indexing of single elements, and to speed up access to a small number of
attributes such as `.shape`. Typing does not allow Cython to speed
up mathematical operations on the whole array (for example, adding two arrays
together). Typing does not allow Cython to speed up calls to Numpy global
functions or to methods of the array.




More generic code[¶](#more-generic-code "Permalink to this headline")
---------------------------------------------------------------------


It would be possible to do:



```
def naive\_convolve(object[DTYPE\_t, ndim=2] f, ...):

```


i.e. use [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.12)") rather than `cnp.ndarray`. Under Python 3.0 this
can allow your algorithm to work with any libraries supporting the buffer
interface; and support for e.g. the Python Imaging Library may easily be added
if someone is interested also under Python 2.x.


There is some speed penalty to this though (as one makes more assumptions
compile-time if the type is set to `cnp.ndarray`, specifically it is
assumed that the data is stored in pure strided mode and not in indirect
mode).





