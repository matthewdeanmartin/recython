from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

GRAVITATIONAL_CONSTANT = 6.67430e-11


@dataclass(slots=True)
class Body:
    mass: float
    x: float
    y: float
    vx: float
    vy: float


def advance_system(bodies: list[Body], dt: float, steps: int) -> None:
    softening = 1.0e3
    for _step in range(steps):
        accelerations: list[tuple[float, float]] = []
        for body in bodies:
            ax = 0.0
            ay = 0.0
            for other in bodies:
                if other is body:
                    continue
                dx = other.x - body.x
                dy = other.y - body.y
                distance_sq = dx * dx + dy * dy + softening
                distance = sqrt(distance_sq)
                scale = GRAVITATIONAL_CONSTANT * other.mass / (distance_sq * distance)
                ax += dx * scale
                ay += dy * scale
            accelerations.append((ax, ay))

        for body, (ax, ay) in zip(bodies, accelerations, strict=True):
            body.vx += ax * dt
            body.vy += ay * dt
            body.x += body.vx * dt
            body.y += body.vy * dt


def total_energy(bodies: list[Body]) -> float:
    kinetic = 0.0
    potential = 0.0
    for index, body in enumerate(bodies):
        kinetic += 0.5 * body.mass * (body.vx * body.vx + body.vy * body.vy)
        for other in bodies[index + 1 :]:
            dx = other.x - body.x
            dy = other.y - body.y
            distance = sqrt(dx * dx + dy * dy)
            potential -= GRAVITATIONAL_CONSTANT * body.mass * other.mass / distance
    return kinetic + potential


def run() -> None:
    bodies = [
        Body(1.9885e30, 0.0, 0.0, 0.0, 0.0),
        Body(5.972e24, 1.496e11, 0.0, 0.0, 29_780.0),
        Body(6.39e23, 2.279e11, 0.0, 0.0, 24_077.0),
    ]
    advance_system(bodies, dt=60.0 * 60.0, steps=2_000)
    print("final energy:", f"{total_energy(bodies):.6e}")
    for body in bodies:
        print(body)


if __name__ == "__main__":
    run()
