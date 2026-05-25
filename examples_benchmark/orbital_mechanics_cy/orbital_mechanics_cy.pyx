# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

from libc.math cimport sqrt

DEF G = 6.67430e-11


cdef class Body:
    cdef public double mass, x, y, vx, vy

    def __init__(self, double mass, double x, double y, double vx, double vy):
        self.mass = mass
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def __repr__(self):
        return f"Body(mass={self.mass}, x={self.x}, y={self.y}, vx={self.vx}, vy={self.vy})"


cpdef void advance_system(list bodies, double dt, int steps):
    cdef int n = len(bodies)
    cdef int step, i, j
    cdef Body body, other
    cdef double ax, ay, dx, dy, distance_sq, distance, scale
    cdef double softening = 1.0e3
    cdef double[:] ax_buf
    cdef double[:] ay_buf

    import array as _array

    for step in range(steps):
        ax_arr = _array.array('d', [0.0] * n)
        ay_arr = _array.array('d', [0.0] * n)
        ax_buf = ax_arr
        ay_buf = ay_arr

        for i in range(n):
            body = bodies[i]
            ax = 0.0
            ay = 0.0
            for j in range(n):
                if i == j:
                    continue
                other = bodies[j]
                dx = other.x - body.x
                dy = other.y - body.y
                distance_sq = dx * dx + dy * dy + softening
                distance = sqrt(distance_sq)
                scale = G * other.mass / (distance_sq * distance)
                ax += dx * scale
                ay += dy * scale
            ax_buf[i] = ax
            ay_buf[i] = ay

        for i in range(n):
            body = bodies[i]
            body.vx += ax_buf[i] * dt
            body.vy += ay_buf[i] * dt
            body.x += body.vx * dt
            body.y += body.vy * dt


cpdef double total_energy(list bodies):
    cdef int n = len(bodies)
    cdef int i, j
    cdef Body body, other
    cdef double kinetic = 0.0, potential = 0.0
    cdef double dx, dy, distance

    for i in range(n):
        body = bodies[i]
        kinetic += 0.5 * body.mass * (body.vx * body.vx + body.vy * body.vy)
        for j in range(i + 1, n):
            other = bodies[j]
            dx = other.x - body.x
            dy = other.y - body.y
            distance = sqrt(dx * dx + dy * dy)
            potential -= G * body.mass * other.mass / distance
    return kinetic + potential
