from maya import cmds
from .skin import isSkinned


def extendWithShapes(selection):
    """
    :param list selection:
    :return: Extended selection
    :rtype: list
    """
    extended = []
    extended.extend(selection)
    extended.extend(cmds.listRelatives(selection, s=True, ni=True, f=True))

    return extended


def filterByType(selection, types):
    """
    :param list selection:
    :param str/list types:
    :return: Filtered selection
    :rtype: list
    """
    return cmds.ls(selection, l=True, type=types)


def splitComponents(selection, component="."):
    """
    :param list selection:
    :param str component:
    :return: tuple(objects, components)
    """
    # variables
    objects = []
    components = []

    # filter components from objects
    for sel in selection:
        if sel.count("."):
            if sel.count(component):
                components.append(sel)
        else:
            objects.append(sel)

    return objects, components


# ----------------------------------------------------------------------------


def getMeshesFromSelection():
    """
    Loop over the current selection, excluding intermediate shapes. If the
    current selected object is not a mesh. The selection will be extended with
    the shapes of that object. It can also contain component selection.

    :return: List of meshes
    :rtype: list of strings
    """
    selection = cmds.ls(sl=True, l=True, fl=True, ni=True) or []
    selection = extendWithShapes(selection)
    selection = filterByType(selection, "mesh")

    return selection


def getSkinnedMeshesFromSelection():
    """
    Loop over the current selection, excluding intermediate shapes. If the
    current selected is a mesh and has a skin cluster attached to it. The
    selection will be extended with the shapes of that object. It can also
    contain component selection.

    :return: List of skinned meshes
    :rtype: list of strings
    """
    return [
        mesh
        for mesh in getMeshesFromSelection()
        if isSkinned(mesh)
    ]

