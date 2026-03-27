from __future__ import annotations

from math import sin


def build_dataset(sample_count: int, feature_count: int) -> tuple[list[list[float]], list[float]]:
    rows: list[list[float]] = []
    targets: list[float] = []
    for row_index in range(sample_count):
        row = []
        for feature_index in range(feature_count):
            value = ((row_index + 1) * (feature_index + 2)) / (feature_index + 3)
            value += sin(row_index * 0.01 + feature_index)
            row.append(value)
        target = 3.0
        for feature_index, value in enumerate(row):
            target += value * (feature_index + 1.5)
        rows.append(row)
        targets.append(target)
    return rows, targets


def fit_multiple_regression(
    features: list[list[float]],
    targets: list[float],
    learning_rate: float = 0.000001,
    epochs: int = 300,
) -> list[float]:
    feature_count = len(features[0])
    weights = [0.0] * (feature_count + 1)

    for _epoch in range(epochs):
        gradients = [0.0] * (feature_count + 1)
        for row, target in zip(features, targets, strict=True):
            prediction = weights[0]
            for feature_index, value in enumerate(row):
                prediction += weights[feature_index + 1] * value
            error = prediction - target
            gradients[0] += error
            for feature_index, value in enumerate(row):
                gradients[feature_index + 1] += error * value

        row_count = float(len(features))
        for weight_index in range(len(weights)):
            weights[weight_index] -= learning_rate * gradients[weight_index] / row_count

    return weights


def score_model(features: list[list[float]], targets: list[float], weights: list[float]) -> float:
    squared_error = 0.0
    for row, target in zip(features, targets, strict=True):
        prediction = weights[0]
        for feature_index, value in enumerate(row):
            prediction += weights[feature_index + 1] * value
        diff = prediction - target
        squared_error += diff * diff
    return squared_error / float(len(features))


def run() -> None:
    features, targets = build_dataset(sample_count=800, feature_count=5)
    weights = fit_multiple_regression(features, targets)
    mean_squared_error = score_model(features, targets, weights)
    print("weights:", weights)
    print("mse:", round(mean_squared_error, 6))


if __name__ == "__main__":
    run()
