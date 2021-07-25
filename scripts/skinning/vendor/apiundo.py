"""Commit to Maya's internal Undo queue"""

import os
import sys
import types

from maya import cmds
from maya.api import OpenMaya as om

__version__ = "0.2.2"

# Public API
__all__ = [
    "commit",
    "install",
    "uninstall",
]


def maya_useNewAPI():
    """Plug-in boilerplate"""


# Support for multiple co-existing versions of apiundo.
# NOTE: This is important for vendoring, as otherwise a vendored apiundo
# could register e.g. cmds.apiUndo() first, causing a newer version
# to inadvertently use this older command (or worse yet, throwing an
# error when trying to register it again).
command = "_apiUndo_%s" % __version__.replace(".", "_")

# This module is both a Python module and Maya plug-in.
# Data is shared amongst the two through this "module"
name = "_apiundoShared"
if name not in sys.modules:
    sys.modules[name] = types.ModuleType(name)

shared = sys.modules[name]
shared.undo = None
shared.redo = None


def commit(undo, redo=lambda: None):
    """Commit `undo` and `redo` to history

    Arguments:
        undo (func): Call this function on next undo
        redo (func, optional): Like `undo`, for for redo

    """

    if not hasattr(cmds, command):
        install()

    # Precautionary measure.
    # If this doesn't pass, odds are we've got a race condition.
    # NOTE: This assumes calls to `commit` can only be done
    # from a single thread, which should already be the case
    # given that Maya's API is not threadsafe.
    assert shared.redo is None
    assert shared.undo is None

    # Temporarily store the functions at module-level,
    # they are later picked up by the command once called.
    shared.undo = undo
    shared.redo = redo

    # Let Maya know that something is undoable
    getattr(cmds, command)()


def install():
    """Load this module as a plug-in

    Call this prior to using the module.

    """

    cmds.loadPlugin(__file__.replace('.pyc', '.py'), quiet=True)


def uninstall():
    """Undo `install()`

    This unregisters the associated plug-in.

    """

    # Plug-in may exist in undo queue and
    # therefore cannot be unloaded until flushed.
    cmds.flushUndo()

    cmds.unloadPlugin(os.path.basename(__file__.replace('.pyc', '.py')))


def reinstall():
    """Automatically reload both Maya plug-in and Python module

    FOR DEVELOPERS

    Call this when changes have been made to this module.

    """

    uninstall()
    sys.modules.pop(__name__)
    module = __import__(__name__, globals(), locals(), ['*'], -1)
    module.install()
    return module


class _apiUndo(om.MPxCommand):
    def doIt(self, args):
        self.undo = shared.undo
        self.redo = shared.redo

        # Facilitate the above precautionary measure
        shared.undo = None
        shared.redo = None

    def undoIt(self):
        self.undo()

    def redoIt(self):
        self.redo()

    def isUndoable(self):
        # Without this, the above undoIt and redoIt will not be called
        return True


def initializePlugin(plugin):
    """Plug-in boilerplate"""
    om.MFnPlugin(plugin).registerCommand(
        command,
        _apiUndo
    )


def uninitializePlugin(plugin):
    """Plug-in boilerplate"""
    om.MFnPlugin(plugin).deregisterCommand(command)
