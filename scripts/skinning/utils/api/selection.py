from maya.api import OpenMaya


def get_rich_selection_mapping(rich_selection):
    """
    Query the weighting of the provided rich selection. That saved data
    structure looks like below where all the objects are grouped under its
    node with a dictionary of element and weight values.

    data = {
        dag: {
            {element: weight},
            {element: weight},
        }
    }

    :param OpenMaya.MRichSelection rich_selection:
    :return: Weight data
    :rtype: dict
    """
    data = {}
    selection = rich_selection.getSelection()
    iterator = OpenMaya.MItSelectionList(selection)
    while not iterator.isDone():
        dag, component = iterator.getComponent()
        path = dag.partialPathName()

        if path not in data:
            data[path] = {}

        if component.hasFn(OpenMaya.MFn.kSingleIndexedComponent):
            component_fn = OpenMaya.MFnSingleIndexedComponent(component)
        elif component.hasFn(OpenMaya.MFn.kDoubleIndexedComponent):
            component_fn = OpenMaya.MFnDoubleIndexedComponent(component)
        elif component.hasFn(OpenMaya.MFn.kTripleIndexedComponent):
            component_fn = OpenMaya.MFnTripleIndexedComponent(component)
        else:
            raise RuntimeError("Unable to query soft selection weights, "
                               "component of type '{}' not supported.".format(component.apiTypeStr))

        for i in range(component_fn.elementCount):
            index = component_fn.element(i)
            weight = component_fn.weight(i).influence
            data[path][index] = weight

        iterator.next()

    return data
