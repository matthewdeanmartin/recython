# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True

from libc.math cimport sin as c_sin


cpdef tuple build_dataset(int sample_count, int feature_count):
    cdef list rows = []
    cdef list targets = []
    cdef list row
    cdef int row_index, feature_index
    cdef double value, target

    for row_index in range(sample_count):
        row = []
        for feature_index in range(feature_count):
            value = (<double>(row_index + 1) * (feature_index + 2)) / (feature_index + 3)
            value += c_sin(row_index * 0.01 + feature_index)
            row.append(value)
        target = 3.0
        for feature_index in range(feature_count):
            target += row[feature_index] * (feature_index + 1.5)
        rows.append(row)
        targets.append(target)
    return rows, targets


cpdef list fit_multiple_regression(list features, list targets, double learning_rate=0.000001, int epochs=300):
    cdef int feature_count = len((<list>features[0]))
    cdef list weights = [0.0] * (feature_count + 1)
    cdef list gradients
    cdef list row
    cdef double target, prediction, error, row_count
    cdef int epoch, feature_index, weight_index
    row_count = <double>len(features)

    for epoch in range(epochs):
        gradients = [0.0] * (feature_count + 1)
        for i in range(<int>len(features)):
            row = features[i]
            target = targets[i]
            prediction = weights[0]
            for feature_index in range(feature_count):
                prediction += weights[feature_index + 1] * <double>row[feature_index]
            error = prediction - target
            gradients[0] += error
            for feature_index in range(feature_count):
                gradients[feature_index + 1] += error * <double>row[feature_index]
        for weight_index in range(feature_count + 1):
            weights[weight_index] -= learning_rate * <double>gradients[weight_index] / row_count
    return weights


cpdef double score_model(list features, list targets, list weights):
    cdef list row
    cdef double target, prediction, diff, squared_error = 0.0
    cdef int feature_index, i, n
    n = len(features)
    cdef int feature_count = len((<list>features[0]))

    for i in range(n):
        row = features[i]
        target = targets[i]
        prediction = weights[0]
        for feature_index in range(feature_count):
            prediction += weights[feature_index + 1] * <double>row[feature_index]
        diff = prediction - target
        squared_error += diff * diff
    return squared_error / <double>n
