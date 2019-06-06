from maya import OpenMaya


__all__ = [
    "getSkinWeights",
]


def getSkinWeights(dag, skinCluster, component):
    """
    Get the skin weights of the original vertex and of its connected vertices.

    :param OpenMaya.MDagPath dag:
    :param OpenMayaAnim.MFnSkinCluster skinCluster:
    :param OpenMaya.MFn.kMeshVertComponent component:
    :return: skin weights and number of influences
    :rtype: tuple(OpenMaya.MDoubleArray, int)
    """
    # weights variables
    weights = OpenMaya.MDoubleArray()

    # influences variables
    influenceMSU = OpenMaya.MScriptUtil()
    influencePTR = influenceMSU.asUintPtr()

    # get weights
    skinCluster.getWeights(dag, component, weights, influencePTR)

    # get num influences
    num = OpenMaya.MScriptUtil.getUint(influencePTR)

    return weights, num

