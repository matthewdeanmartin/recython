cpdef list fit_multiple_regression(list features, list targets, double learning_rate=0.000001, int epochs=300):
    cdef int feature_count = len(features[0])
    cdef list weights = [0.0] * (feature_count + 1)
    cdef list gradients
    cdef list row
    cdef double target
    cdef double prediction
    cdef double error
    cdef double row_count = float(len(features))
    cdef int epoch
    cdef int feature_index
    cdef int weight_index

    for epoch in range(epochs):
        gradients = [0.0] * (feature_count + 1)
        for row, target in zip(features, targets):
            prediction = weights[0]
            for feature_index, value in enumerate(row):
                prediction += weights[feature_index + 1] * value
            error = prediction - target
            gradients[0] += error
            for feature_index, value in enumerate(row):
                gradients[feature_index + 1] += error * value

        for weight_index in range(len(weights)):
            weights[weight_index] -= learning_rate * gradients[weight_index] / row_count
    return weights


cpdef double score_model(list features, list targets, list weights):
    cdef list row
    cdef double target
    cdef double prediction
    cdef double diff
    cdef double squared_error = 0.0
    cdef int feature_index

    for row, target in zip(features, targets):
        prediction = weights[0]
        for feature_index, value in enumerate(row):
            prediction += weights[feature_index + 1] * value
        diff = prediction - target
        squared_error += diff * diff
    return squared_error / float(len(features))
