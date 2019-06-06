from maya import OpenMaya


__all__ = [
    "asMIntArray",
    "asComponent"
]


def asMIntArray(index):
    """
    index -> OpenMaya.MIntArray

    :param int/list of ints/OpenMaya.MIntArray index: indices
    :return: Array of indices
    :rtype: OpenMaya.MIntArray
    """
    if type(index) != OpenMaya.MIntArray:
        array = OpenMaya.MIntArray()
        if type(index) == list:
            for i in index:
                array.append(i)
        else:
            array.append(index)

        return array

    return index


def asComponent(index):
    """
    index -> OpenMaya.MFn.kMeshVertComponent

    :param int/OpenMaya.MIntArray index: indices to create component for
    :return: Initialized component(s)
    :rtype: OpenMaya.MFn.kMeshVertComponent
    """
    # convert input to an MIntArray if it not already is one
    indices = asMIntArray(index)

    # initialize component(s)
    t = OpenMaya.MFn.kMeshVertComponent
    component = OpenMaya.MFnSingleIndexedComponent().create(t)
    OpenMaya.MFnSingleIndexedComponent(component).addElements(indices)

    return component
