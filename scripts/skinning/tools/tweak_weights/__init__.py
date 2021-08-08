"""
Tweak influence weights on a component level.

.. figure:: _images/tweak-weights-example.png
   :align: center

`Link to Video <https://vimeo.com/120942200>`_

Installation
============
* Extract the content of the .rar file anywhere on disk.
* Drag the skinning-tools.mel file in Maya to permanently install the script.

Note
====
Tweak component weights with sliders or spinbox input fields. This tool will
give the user a good overview of what influences are translating the
component. At the same time being able to tweak those influence to a 0.001 of
precision, while setting the locked state of certain influences. It also
shows if the maximum amount of influences is exceeded. The ui gets updated
every time the selection is changed in Maya.
"""
__author__ = "Robert Joosten"
__version__ = "2.0.0"
__email__ = "rwm.joosten@gmail.com"
