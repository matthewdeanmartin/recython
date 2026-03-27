from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TriangularFuzzyNumber:
    low: float
    peak: float
    high: float

    def add(self, other: "TriangularFuzzyNumber") -> "TriangularFuzzyNumber":
        return TriangularFuzzyNumber(self.low + other.low, self.peak + other.peak, self.high + other.high)

    def scale(self, factor: float) -> "TriangularFuzzyNumber":
        if factor >= 0:
            return TriangularFuzzyNumber(self.low * factor, self.peak * factor, self.high * factor)
        return TriangularFuzzyNumber(self.high * factor, self.peak * factor, self.low * factor)

    def multiply(self, other: "TriangularFuzzyNumber") -> "TriangularFuzzyNumber":
        candidates = [
            self.low * other.low,
            self.low * other.high,
            self.high * other.low,
            self.high * other.high,
        ]
        return TriangularFuzzyNumber(min(candidates), self.peak * other.peak, max(candidates))

    def centroid(self) -> float:
        return (self.low + self.peak + self.high) / 3.0


def combine_sensor_readings(
    signals: list[TriangularFuzzyNumber],
    weights: list[float],
    iterations: int = 400,
) -> TriangularFuzzyNumber:
    combined = TriangularFuzzyNumber(0.0, 0.0, 0.0)
    for _iteration in range(iterations):
        accumulator = TriangularFuzzyNumber(0.0, 0.0, 0.0)
        for signal, weight in zip(signals, weights, strict=True):
            weighted = signal.scale(weight)
            accumulator = accumulator.add(weighted.multiply(signal))
        combined = combined.add(accumulator.scale(1.0 / float(len(signals))))
    return combined.scale(1.0 / float(iterations))


def run() -> None:
    signals = [
        TriangularFuzzyNumber(1.0, 1.3, 1.8),
        TriangularFuzzyNumber(0.9, 1.1, 1.6),
        TriangularFuzzyNumber(1.2, 1.4, 1.9),
        TriangularFuzzyNumber(1.1, 1.5, 2.0),
    ]
    weights = [0.25, 0.35, 0.2, 0.2]
    combined = combine_sensor_readings(signals, weights)
    print("combined:", combined)
    print("centroid:", round(combined.centroid(), 6))


if __name__ == "__main__":
    run()
