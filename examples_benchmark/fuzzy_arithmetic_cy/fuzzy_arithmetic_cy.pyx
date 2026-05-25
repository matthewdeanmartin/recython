# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

from libc.math cimport fmin, fmax


cdef class TriangularFuzzyNumber:
    cdef public double low, peak, high

    def __init__(self, double low, double peak, double high):
        self.low = low
        self.peak = peak
        self.high = high

    cpdef TriangularFuzzyNumber add(self, TriangularFuzzyNumber other):
        return TriangularFuzzyNumber(self.low + other.low, self.peak + other.peak, self.high + other.high)

    cpdef TriangularFuzzyNumber scale(self, double factor):
        if factor >= 0.0:
            return TriangularFuzzyNumber(self.low * factor, self.peak * factor, self.high * factor)
        return TriangularFuzzyNumber(self.high * factor, self.peak * factor, self.low * factor)

    cpdef TriangularFuzzyNumber multiply(self, TriangularFuzzyNumber other):
        cdef double a = self.low * other.low
        cdef double b = self.low * other.high
        cdef double c = self.high * other.low
        cdef double d = self.high * other.high
        cdef double lo = fmin(fmin(a, b), fmin(c, d))
        cdef double hi = fmax(fmax(a, b), fmax(c, d))
        return TriangularFuzzyNumber(lo, self.peak * other.peak, hi)

    cpdef double centroid(self):
        return (self.low + self.peak + self.high) / 3.0


cpdef TriangularFuzzyNumber combine_sensor_readings(list signals, list weights, int iterations=400):
    cdef TriangularFuzzyNumber combined = TriangularFuzzyNumber(0.0, 0.0, 0.0)
    cdef TriangularFuzzyNumber accumulator, signal, weighted
    cdef double weight
    cdef int i, n
    n = len(signals)

    for _iteration in range(iterations):
        accumulator = TriangularFuzzyNumber(0.0, 0.0, 0.0)
        for i in range(n):
            signal = signals[i]
            weight = weights[i]
            weighted = signal.scale(weight)
            accumulator = accumulator.add(weighted.multiply(signal))
        combined = combined.add(accumulator.scale(1.0 / n))
    return combined.scale(1.0 / iterations)
