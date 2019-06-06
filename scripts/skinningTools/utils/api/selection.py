from maya import OpenMaya


__all__ = [
    "getSoftSelection"
]


def getSoftSelection():
    """
    Query the soft selection in the scene. If no soft selection is made empty
    lists will be returned. The active selection will be returned for easy
    reselection. The data structure of the soft selection weight is as
    followed.

    data = {
        mesh:{
            {index:weight},
            {index:weight},
        }

    }

    :return: Active selection list for re-selection and weight data.
    :rtype: tuple(OpenMaya.MSelectionList, dict)
    """
    # variables
    data = {}

    activeList = OpenMaya.MSelectionList()
    richList = OpenMaya.MSelectionList()
    softSelection = OpenMaya.MRichSelection()

    # get active selection
    OpenMaya.MGlobal.getActiveSelectionList(activeList)

    # get rich selection
    try:
        OpenMaya.MGlobal.getRichSelection(softSelection, False)
        softSelection.getSelection(richList)
    except:
        return activeList, data

    # iter selection
    selIter = OpenMaya.MItSelectionList(richList)
    while not selIter.isDone():
        # variables
        dep = OpenMaya.MObject()
        obj = OpenMaya.MObject()
        dag = OpenMaya.MDagPath()

        selIter.getDependNode(dep)
        selIter.getDagPath(dag, obj)

        # add path
        path = dag.fullPathName()
        if path not in data.keys():
            data[path] = {}

        # check is selection type is vertex components
        if obj.apiType() == OpenMaya.MFn.kMeshVertComponent:
            components = OpenMaya.MFnSingleIndexedComponent(obj)
            count = components.elementCount()

            # store index and weight
            for i in range(count):
                index = components.element(i)
                weight = components.weight(i).influence()

                data[path][index] = weight

        selIter.next()

    return activeList, data
