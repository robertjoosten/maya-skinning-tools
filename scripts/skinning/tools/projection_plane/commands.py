from maya import cmds
from maya.api import OpenMaya
from maya.api import OpenMayaAnim

from skinning.utils import api
from skinning.utils import math
from skinning.utils import skin
from skinning.utils import decorator


__all__ = [
    "create_projection_plane"
]

AXIS = {
    "x": OpenMaya.MVector(1, 0, 0),
    "y": OpenMaya.MVector(0, 1, 0),
    "z": OpenMaya.MVector(0, 0, 1),
}


@decorator.preserve_selection
def create_projection_plane(joints, name=None, axis="z", width=25, padding=0, offset=0):
    """
    Create a projector plane for the given influences. The points of the
    plane are calculated using the provided width and axis. After that a
    skin cluster is created.

    :param list[str] joints:
    :param str/None name:
    :param str axis:
    :param int/float width:
    :param int padding:
    :param int offset:
    :return: Projection plane
    :rtype: str
    :raise ValueError: When not more than 2 influences is provided
    :raise ValueError: When axis is not valid.
    """
    num = len(joints)
    if num < 2:
        raise ValueError("Projection plane can only be created "
                         "when providing at least 2 joints.")
    elif axis not in AXIS:
        raise ValueError("Provided axis '{}' is not valid, "
                         "options are; {}.".format(axis, list(AXIS.keys())))

    name = name or "projector#"
    plane = cmds.polyPlane(subdivisionsX=1,  subdivisionsY=num - 1, constructionHistory=False, name=name)[0]
    matrices = [OpenMaya.MMatrix(cmds.xform(node, query=True, worldSpace=True, matrix=True)) for node in joints]
    weights = OpenMaya.MDoubleArray()
    influences = OpenMaya.MIntArray(range(num))

    # calculate new matrices by blending matrices using the provided padding.
    # this will ensure a smoother rotational transition between joints.
    if padding > 0:
        matrices_padded = []
        for i, matrix in enumerate(matrices):
            matrix = OpenMaya.MTransformationMatrix(matrix)
            translation = matrix.translation(OpenMaya.MSpace.kWorld)

            padding_value = min([min([i, padding]), min([num - i - 1, num - padding])])
            matrix_padding = [matrices[j] for j in range(i - padding_value, i + padding_value + 1) if 0 <= j < num]
            matrix_average = math.average_matrix(matrix_padding)
            matrix_average = OpenMaya.MTransformationMatrix(matrix_average)
            matrix_average = OpenMaya.MTransformationMatrix(matrix_average.asRotateMatrix())
            matrix_average.setTranslation(translation, OpenMaya.MSpace.kWorld)
            matrix_average.setScale(OpenMaya.MVector(1, 1, 1), OpenMaya.MSpace.kWorld)

            matrices_padded.append(matrix_average.asMatrix())

        matrices = matrices_padded

    # position plane vertices
    for i, matrix in enumerate(matrices):
        for j, multiplier in enumerate([-1, 1]):
            vertex = (i * 2) + j
            point = OpenMaya.MPoint(AXIS[axis] * width * multiplier) * matrix
            cmds.xform("{}.vtx[{}]".format(plane, vertex), translation=list(point)[:3])

            influence = min([max([0, i - offset]), num - 1])
            for k in range(num):
                weights.append(int(influence == k))

    # create skin cluster
    skin_cluster = cmds.skinCluster(
        joints,
        plane,
        name="{}_SK".format(name),
        toSelectedBones=True,
        removeUnusedInfluence=False,
        maximumInfluences=4,
        obeyMaxInfluences=True,
        bindMethod=0,
        skinMethod=0,  # linear
        normalizeWeights=1,  # interactive
        weightDistribution=0,  # distance
    )[0]

    # set weights
    dag, component = api.conversion.get_component(plane)
    skin_cluster_obj = api.conversion.get_object(skin_cluster)
    skin_cluster_fn = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj)

    skin.set_weights(skin_cluster_fn, dag, component, influences, weights,)
