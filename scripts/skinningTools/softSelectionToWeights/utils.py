from maya import cmds, OpenMaya
from .. import utils


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
        weights = OpenMaya.MFloatArray()
    
        selIter.getDependNode(dep)
        selIter.getDagPath(dag, obj)
        
        # add path
        path = dag.fullPathName()
        if not path in data.keys():
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


def setSkinWeights(mesh, meshData, influences, filler=None):
    """
    Calculate and set the new skin weights. If no skin cluster is attached to
    the mesh, one will be created and all weights will be set to 1 with the 
    filler influence. If a skin cluster does exist, the current weights will
    be used to blend the new weights. Maintaining of maximum influences and 
    normalization of the weights will be taken into account if these 
    attributes are set on the skin cluster.
    
    meshData = {
        mesh:{
            {index:{
                influence:weight,
                influence:weight,
            },
            {index:{
                influence:weight,
                influence:weight,
            },
        }    
    }
    
    :param str mesh:
    :param dict meshData: skinning data for the mesh
    :param list influences: list of (new) influences
    :param str filler: Filler joint if no skin cluster is detected
    """
    with utils.UndoChunkContext():
        skinCluster = utils.getSkinCluster(mesh)
        
        # bind skin
        if not skinCluster:
            influences.append(filler)
            skinCluster = cmds.skinCluster(
                mesh, 
                influences, 
                omi=True, 
                mi=4, 
                tsb=True
            )[0]
                   
            # set weights with filler
            cmds.skinPercent(
                skinCluster, 
                "{0}.vtx[*]".format(mesh), 
                transformValue=[(filler, 1)]
            )
            
        # add influences
        else:
            filler = None
            utils.addInfluences(skinCluster, influences) 
            
        # get skinCluster data
        normalizeWeights = cmds.getAttr(
            "{0}.normalizeWeights".format(skinCluster)
        )
        maxInfluences = cmds.getAttr(
            "{0}.maxInfluences".format(skinCluster)
        )
        maintainMaxInfluences = cmds.getAttr(
            "{0}.maintainMaxInfluences".format(skinCluster)
        )

        # loop indices
        for index, weights in meshData.iteritems():
            vertex = "{0}.vtx[{1}]".format(mesh, index)
            total = sum(weights.values())
            
            if filler and total < 1:
                # add filler weight
                weights[filler] = 1-total
            elif not filler and total < 1:
                multiplier = 1-total
                
                # query existing
                transforms = cmds.skinPercent(
                    skinCluster, 
                    vertex, 
                    query=True, 
                    transform=None
                )
                transforms = cmds.ls(transforms, l=True)
                
                values = cmds.skinPercent(
                    skinCluster, 
                    vertex, 
                    query=True, 
                    value=True
                )
                 
                # add normalized existing weights
                for t, v in zip(transforms, values):
                    if not t in weights.keys():
                         weights[t] = 0
                         
                    weights[t] += v * multiplier
                    
            if maintainMaxInfluences:
                # maintain influences, set excess influences to 0.0
                temp = zip(weights.values(), weights.keys())
                excess = sorted(temp, reverse=True)[maxInfluences:]
                
                for v, t in excess:
                    weights[t] = 0.0
            
            if normalizeWeights == 1:
                # normalize all weights
                total = sum(weights.values())
                multiplier = 1/total
                
                for t, v in weights.iteritems():
                    weights[t] = v * multiplier
            
            # set weights
            weights = [(t, v) for t, v in weights.iteritems()]
            cmds.skinPercent(skinCluster, vertex, transformValue=weights)
