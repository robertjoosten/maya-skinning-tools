from maya import cmds, OpenMaya
from ..utils import api


AXIS = {
    "x": OpenMaya.MVector(1, 0, 0),
    "y": OpenMaya.MVector(0, 1, 0),
    "z": OpenMaya.MVector(0, 0, 1),
}


def createProjectionPlane(joints, axis="z", width=10, orientation_padding=0, skinning_offset=0):
    """
    Create a poly plane that is positioned at the joints. The plane is
    oriented to the provided side. It is possible to blend the orientation
    using the padding argument. The plane is skinned to the provided joints
    with its influences set to 1. The provided joint order is respected.

    :param list joints:
    :param str axis:
    :param int/float width:
    :param int orientation_padding:
    :param int skinning_offset:
    :return: Projection plane
    :rtype: str
    :raise RuntimeError: When less than 2 joints are provided.
    :raise ValueError: When provided axis is not valid.
    """
    # validate settings
    if len(joints) < 2:
        raise RuntimeError("Need more than 2 joints to create a plane.")
    elif axis.lower() not in AXIS.keys():
        raise ValueError("Axis '{}' is not supported, options are {}".format(axis, AXIS.keys()))

    # get matrices
    matrices = [api.asMDagPath(api.asMObject(joint)).inclusiveMatrix() for joint in joints]

    # get rotation matrices from padding
    rotation_matrices = []
    for i in range((len(joints))):

        [[j for j in range(i-orientation_padding, i+orientation_padding + 1)] for i in range(len(joints))]
        print(rotation_matrices)