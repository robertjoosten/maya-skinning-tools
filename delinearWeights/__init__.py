"""		
De-linearize skin weights.

.. figure:: https://github.com/robertjoosten/rjSkinningTools/raw/master/delinearWeights/README.png
   :align: center
   
Installation
============
Copy the **rjSkinningTools** folder to your Maya scripts directory
::
    C:/Users/<USER>/Documents/maya/scripts
    
Usage
=====
Display UI
::
    import rjSkinningTools.delinearWeights.ui
    rjSkinningTools.delinearWeights.ui.show()
			
Note
====
Delinear weights applies an easing algorithm to the skin weights. This tool 
is best used if skin weights have been copied from a low polygon source, when 
this is done sometimes it is very obvious that the weights are linearly 
divided between the vertices of the low polygon source. This tool will tween 
those weights.

Code
====
"""

from maya import cmds, mel, OpenMayaAnim
from rjSkinningTools import utils

from . import tweening

__author__    = "Robert Joosten"
__version__   = "0.7.0"
__email__     = "rwm.joosten@gmail.com"

# ----------------------------------------------------------------------------

def getTweeningMethod(method):
	"""
	Get the tweening method from a string, if the function doesn't exists
	None will be returned.

	:return: Tweening function
	:rtype: func/None
	"""
	if method in dir(tweening):
		return getattr(tweening, method)
		
# ----------------------------------------------------------------------------

def getSelectedVertices():
	"""
    Get all of the selected vertices. If no component mode selection is made
	all vertices of a selected mesh will be appended to the selection. 
    
    :return: List of selected vertices
    :rtype: list of strings
    """
	# get vertices
	vertices = [
		vtx 
		for vtx in cmds.ls(sl=True, fl=True, l=True) 
		if vtx.count(".vtx")
	]

	# append meshes
	meshes = utils.getMeshesFromSelection()
	for mesh in meshes:
		vertices.extend(
			cmds.ls(
			"{0}.vtx[*]".format(mesh),
			fl=True,
			l=True
		)
	)

	return vertices
	
# ----------------------------------------------------------------------------

def getIndexFromString(vtx):
	"""
	Get the index from a component string.
	
	:param str vtx: Path to component
	:return: Index of component string
    :rtype: int
	"""
	return int(vtx.split("[")[-1][:-1])
	
def splitByInfluences(weights, num):
	"""
	Split a list of weights into the size of the number of influences.
	
	:param list weights: List of weights
	:param int num: Size of split
	:return: Index of component string
    :rtype: int
	"""
	chunks = []
	for i in xrange(0, len(weights), num):
		chunks.append(weights[i:i + num])

	return chunks

# ----------------------------------------------------------------------------
	
def deLinearSkinWeightsOnSelection(method):
	"""
	All of the selected vertices will be queried with the
	:func:`getSelectedVertices` function, these vertices will then be parsed 
	to the :func:`deLinearSkinWeights` function that will process the weights.
	
	:param str method: De-linearization method
	"""
	vertices = getSelectedVertices()
	deLinearSkinWeights(vertices, method)
	
def deLinearSkinWeights(vertices, method):
	"""
	Loop over all of the provided vertices. Loop over all of the vertices and 
	see if these vertices are deformed by a skin cluster. If this is the case, 
	the weights will be de-linearized by the function provided. This function
	is found in the tweening module using :func:`getTweeningMethod`.
	
	:param list vertices: List of vertices
	:param str method: De-linearization method
	"""
	func = getTweeningMethod(method)
	if not func:
		raise ValueError("Tweening method is not supported.")

	data = {}
	objects = list(set([vtx.split(".")[0] for vtx in vertices]))
	
	with utils.UndoChunkContext():
		for obj in objects:
			# get skin cluster
			sk = utils.getSkinCluster(obj)
			if not sk:
				continue
			
			# get indices
			indices = [
				getIndexFromString(vtx) 
				for vtx in vertices 
				if vtx.startswith(obj)
			]
			
			# get api objects
			meshObj = utils.asMObject(obj)
			meshDag = utils.asMDagPath(meshObj)
			meshDag.extendToShape()
			
			skObj = utils.asMObject(sk)
			skMfn = OpenMayaAnim.MFnSkinCluster(skObj)
			
			# get weights
			components = utils.asComponent(indices)
			weightsAll, num = utils.getSkinWeights(
				meshDag, 
				skMfn, 
				components
			)
			
			# split weights
			weightChunks = splitByInfluences(weightsAll, num)

			for i, weights in enumerate(weightChunks):
				# calculate per vertex weights
				weights = utils.normalizeWeights(weights)
				weights = [func(w) for w in weights]
				weights = utils.normalizeWeights(weights)
				
				# set weights
				for j, w in enumerate(weights):
					cmds.setAttr(
						"{0}.weightList[{1}].weights[{2}]".format(
							sk, 
							indices[i],
							j
						), 
						w
					)
