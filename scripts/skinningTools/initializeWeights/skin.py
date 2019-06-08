from maya import cmds
from ..utils import skin, influence


def getSkinCluster(mesh, joints):
    """
    This function will check if the provided mesh has a skin cluster attached
    to it. If it doesn't a new skin cluster will be created with the provided
    joints as influences. No additional arguments are used to setup the skin
    cluster. This is something that needs to be done afterwards by the user.
    If a skin cluster already exists all provided joints will be added to the
    skin cluster as an influence.

    :param str mesh:
    :param list joints:
    :return: Skin cluster
    :rtype: str
    """
    # full path joints
    joints = cmds.ls(joints, l=True)

    # get skin cluster
    sk = skin.getSkinCluster(mesh)
    if not sk:
        # create skin cluster
        sk = cmds.skinCluster(
            joints,
            mesh,
            dropoffRate=0.1,
            name="{}_sk".format(mesh)
        )[0]

    else:
        # make sure all provided joints are an influence of the skin cluster
        # that is already attached to the mesh
        influence.addInfluences(sk, joints)

    return sk