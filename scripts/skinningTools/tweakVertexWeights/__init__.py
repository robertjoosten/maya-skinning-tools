"""		
Tweak influence weights on a vertex level.

.. figure:: _images/tweakVertexWeightsExample.png
   :align: center
   
`Link to Video <https://vimeo.com/120942200>`_

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the skinningTools.mel file in Maya to permanently install the script.

Note
====
Tweak vertex weights with sliders or spinbox input fields. This tool will
give the user a good overview of what influences are translating the 
vertex. At the same time being able to tweak those influence to a 0.001 
of precision, while setting the locked state of certain influences. It 
also shows if the maximum amount of influences is exceeded. The ui gets 
updated every time the selection is changed in Maya.

"""
__author__ = "Robert Joosten"
__version__ = "0.8.1"
__email__ = "rwm.joosten@gmail.com"
