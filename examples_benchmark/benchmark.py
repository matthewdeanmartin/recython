"""Benchmark pure-Python examples vs Cython-compiled equivalents."""

from __future__ import annotations

import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "examples" / "src_fuzzy_arithmetic"))
sys.path.insert(0, str(Path(__file__).parent.parent / "examples" / "src_multiple_regression"))
sys.path.insert(0, str(Path(__file__).parent.parent / "examples" / "src_orbital_mechanics"))
sys.path.insert(0, str(Path(__file__).parent / "fuzzy_arithmetic_cy"))
sys.path.insert(0, str(Path(__file__).parent / "multiple_regression_cy"))
sys.path.insert(0, str(Path(__file__).parent / "orbital_mechanics_cy"))


REPS = 5


def bench(label: str, stmt: str, setup: str, reps: int = REPS) -> float:
    times = timeit.repeat(stmt=stmt, setup=setup, repeat=reps, number=1)
    best = min(times)
    print(f"  {label:45s}  {best:.4f}s")
    return best


def benchmark_fuzzy() -> tuple[float, float]:
    print("\n=== Fuzzy Arithmetic ===")
    setup_py = (
        "from fuzzy_arithmetic.__main__ import TriangularFuzzyNumber, combine_sensor_readings\n"
        "signals = [TriangularFuzzyNumber(1.0,1.3,1.8), TriangularFuzzyNumber(0.9,1.1,1.6),"
        " TriangularFuzzyNumber(1.2,1.4,1.9), TriangularFuzzyNumber(1.1,1.5,2.0)]\n"
        "weights = [0.25, 0.35, 0.2, 0.2]"
    )
    setup_cy = (
        "from fuzzy_arithmetic_cy import TriangularFuzzyNumber, combine_sensor_readings\n"
        "signals = [TriangularFuzzyNumber(1.0,1.3,1.8), TriangularFuzzyNumber(0.9,1.1,1.6),"
        " TriangularFuzzyNumber(1.2,1.4,1.9), TriangularFuzzyNumber(1.1,1.5,2.0)]\n"
        "weights = [0.25, 0.35, 0.2, 0.2]"
    )
    t_py = bench("Pure Python", "combine_sensor_readings(signals, weights)", setup_py)
    t_cy = bench("Cython     ", "combine_sensor_readings(signals, weights)", setup_cy)
    return t_py, t_cy


def benchmark_regression() -> tuple[float, float]:
    print("\n=== Multiple Regression ===")
    setup_py = (
        "from multiple_regression.__main__ import build_dataset, fit_multiple_regression, score_model\n"
        "features, targets = build_dataset(800, 5)"
    )
    setup_cy = (
        "from multiple_regression_cy import build_dataset, fit_multiple_regression, score_model\n"
        "features, targets = build_dataset(800, 5)"
    )
    t_py = bench("Pure Python", "fit_multiple_regression(features, targets)", setup_py)
    t_cy = bench("Cython     ", "fit_multiple_regression(features, targets)", setup_cy)
    return t_py, t_cy


def benchmark_orbital() -> tuple[float, float]:
    print("\n=== Orbital Mechanics ===")
    setup_py = (
        "from orbital_mechanics.__main__ import Body, advance_system\n"
        "bodies = [Body(1.9885e30,0.0,0.0,0.0,0.0), Body(5.972e24,1.496e11,0.0,0.0,29780.0),"
        " Body(6.39e23,2.279e11,0.0,0.0,24077.0)]"
    )
    setup_cy = (
        "from orbital_mechanics_cy import Body, advance_system\n"
        "bodies = [Body(1.9885e30,0.0,0.0,0.0,0.0), Body(5.972e24,1.496e11,0.0,0.0,29780.0),"
        " Body(6.39e23,2.279e11,0.0,0.0,24077.0)]"
    )
    t_py = bench("Pure Python", "advance_system(bodies, 3600.0, 2000)", setup_py)
    t_cy = bench("Cython     ", "advance_system(bodies, 3600.0, 2000)", setup_cy)
    return t_py, t_cy


def main() -> None:
    print("Running benchmarks (best of 5 runs each)...")

    fuzzy_py, fuzzy_cy = benchmark_fuzzy()
    reg_py, reg_cy = benchmark_regression()
    orb_py, orb_cy = benchmark_orbital()

    print("\n=== Summary ===")
    results = [
        ("Fuzzy Arithmetic", fuzzy_py, fuzzy_cy),
        ("Multiple Regression", reg_py, reg_cy),
        ("Orbital Mechanics", orb_py, orb_cy),
    ]
    for name, t_py, t_cy in results:
        speedup = t_py / t_cy if t_cy > 0 else float("inf")
        print(f"  {name:25s}  Python={t_py:.4f}s  Cython={t_cy:.4f}s  Speedup={speedup:.2f}x")


if __name__ == "__main__":
    main()
