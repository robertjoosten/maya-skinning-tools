"""
Remove a specific influence on vertices with the paint tool.

.. figure:: _images/remove-weights-context-example.png
   :align: center

`Link to Video <https://vimeo.com/122189210>`_

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the skinning-tools.mel file in Maya to permanently install the script.

Note
====
The paint tool calls a script that will select all the vertices that are
influenced by the parsed influence. You can then paint away the influence
on those vertices with the paint tool.
    * Undo-able / Redo-able

Based on the settings on the skinCluster the following attribute will be
respected while removing the influence weights:
    * Normalize Weights
    * Locked Influences

If you are working with a mesh that contains many influences it is possible to
filter then using the search box.
"""
from skinning.tools.remove_weights_context.commands import *

__author__ = "Robert Joosten"
__version__ = "1.0.2"
__email__ = "rwm.joosten@gmail.com"
