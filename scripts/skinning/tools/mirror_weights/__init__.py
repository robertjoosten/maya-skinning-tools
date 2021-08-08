"""
Mirror skin weights using topology.

.. figure:: _images/mirror-weights-example.png
   :align: center

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the skinning-tools.mel file in Maya to permanently install the script.

Note
====
Mirror skin weights using the topology of a mesh. By selecting the mirrored
edge of a mesh a symmetry mapping is generated which can be used to mirror
weights from side to side. The mirror mapping for the influences is created
using a string match between left and right rather than position or labels.
"""
from skinning.tools.mirror_weights.commands import *

__author__ = "Robert Joosten"
__version__ = "0.8.0"
__email__ = "rwm.joosten@gmail.com"
