def normalizeWeights(weights):
    """
    Normalize a list of weights so the sum of the list is equal to one.

    :return: List of normalized weights
    :rtype: list of floats
    """
    multiplier = 1 / sum(weights)

    if multiplier == 1:
        return weights

    return [w * multiplier for w in weights]
