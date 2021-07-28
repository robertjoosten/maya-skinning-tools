from maya import cmds
from maya.api import OpenMaya


class Influence(object):
    def __init__(self, path):
        self.parent = None
        self.children = []
        self.path = path
        self.type = cmds.nodeType(path)

    # ------------------------------------------------------------------------

    def get_position(self):
        """
        :return: Position
        :rtype: OpenMaya.MVector
        """
        position = cmds.xform(self.path, query=True, worldSpace=True, translation=True)
        return OpenMaya.MVector(*position)

    def get_matrix(self, world_space=True):
        """
        :return: Matrix
        :rtype: OpenMaya.MMatrix
        """
        matrix = cmds.xform(self.path, query=True, worldSpace=world_space, matrix=True)
        return OpenMaya.MMatrix(*matrix)

    # ------------------------------------------------------------------------

    def rename(self, name):
        """
        :param str name:
        """
        self.path = cmds.rename(self.path, name)


class Skeleton(object):
    """
    The skeleton will sort all influences from a skin cluster based on their
    hierarchy and will allow the influence nodes to be looped via parent and
    children attributes.
    """
    def __init__(self, influences):
        self.parent = None
        self.children = []

        mapper = {}
        influences = zip(cmds.ls(influences, l=True), cmds.ls(influences))
        influences = sorted(influences, key=lambda x: x[0])

        for path, path_partial in influences:
            node = Influence(path_partial)
            for i in range(1, path.count("|")):
                parent_path = path.rsplit("|", i)[0]
                if parent_path in mapper:
                    parent = mapper[parent_path]
                    break
            else:
                parent = self

            node.parent = parent
            parent.children.append(node)
            mapper[path] = node


def add_influences(skin_cluster, influences):
    """
    Add influences to the skin cluster. Expects full path influences. Will
    try to reach the bind pose before attached the new influences to the skin
    cluster.

    :param str skin_cluster:
    :param list influences:
    """
    influences = cmds.ls(influences, l=True)
    influences_existing = cmds.skinCluster(skin_cluster, query=True, influence=True)

    try:
        cmds.dagPose(influences_existing, restore=True, g=True, bindPose=True)
    except RuntimeError:
        cmds.warning("Unable to reach dagPose!")

    influences_existing = cmds.ls(influences_existing, l=True)
    influences_existing = set(influences_existing)
    for influence in influences:
        if influence not in influences_existing:
            cmds.skinCluster(
                skin_cluster,
                edit=True,
                addInfluence=influence,
                weight=0.0
            )
