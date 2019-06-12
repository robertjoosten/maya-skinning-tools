from maya import cmds
from . import weight
from ..utils import ui, selection, conversion
from ..utils.ui import Qt, widgets


# ----------------------------------------------------------------------------


WINDOW_TITLE = "Initialize Skin Weights"
WINDOW_ICON = "ST_initializeWeights.png"


# ----------------------------------------------------------------------------


class MeshSelectionWidget(widgets.LabelButton):
    def __init__(self, parent):
        widgets.LabelButton.__init__(
            self,
            parent,
            label="0 Mesh(es) with 0 Component(s)",
            button="Select Mesh(es)"
        )

        # variables
        self._data = []

        # connect
        self.released.connect(self.setSelection)

    # ------------------------------------------------------------------------

    def getArguments(self):
        """
        Get arguments that are parsed in the setInitialWeights function, this
        function will return a dictionary that can be parsed into the function
        as keyword arguments. The arguments are returned in list format as
        multiple meshes can be processed at the same time

        :return: Arguments
        :rtype: list
        """
        return self._data

    # ------------------------------------------------------------------------

    def setSelection(self):
        # get selected skinned meshes
        objects = selection.getMeshesFromSelection()
        meshes, components = selection.splitComponents(objects, ".vtx")

        # populate meshes
        data = {mesh: [] for mesh in meshes}

        # populate components
        for component in components:
            # get mesh
            mesh = component.split(".")[0]

            # add mesh with empty component list
            if mesh not in data.keys():
                data[mesh] = []

            # add component index
            data[mesh].append(
                conversion.componentIndexFromString(component)
            )

        # set data
        self._data = [
            {"mesh": mesh, "components": components}
            for mesh, components in data.iteritems()
        ]

        # set label
        meshes = len(data.keys())
        components = max([len(v) for v in data.values()])

        self.setLabelText(
            "{} Mesh(es) with {} Component(s)".format(
                meshes,
                components
            )
        )


class JointSelectionWidget(widgets.LabelButton):
    def __init__(self, parent):
        widgets.LabelButton.__init__(
            self,
            parent,
            label="0 Joint(s)",
            button="Select Joint(s)"
        )

        # variables
        self._joints = []

        # connect
        self.released.connect(self.setSelection)

    # ------------------------------------------------------------------------

    def getArguments(self):
        """
        Get arguments that are parsed in the setInitialWeights function, this
        function will return a dictionary that can be parsed into the function
        as keyword arguments.

        :return: Arguments
        :rtype: dict
        """
        return {
            "joints": self._joints
        }

    # ------------------------------------------------------------------------

    def setSelection(self):
        # set data
        objects = cmds.ls(sl=True, l=True)
        self._joints = selection.filterByType(objects, types="joint")

        # set label
        self.setLabelText("{} Joint(s)".format(len(self._joints)))


# ----------------------------------------------------------------------------


class SmoothWidget(Qt.QWidget):
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create iterations
        self.iterations = widgets.LabelSpinBox(
            self,
            label="Iterations:",
            double=False,
            value=3,
            minValue=0,
            maxValue=25,
        )
        layout.addWidget(self.iterations)

        # create iterations
        self.projection = widgets.LabelSpinBox(
            self,
            label="Projection:",
            double=True,
            value=0.75,
            step=0.05,
            minValue=0,
            maxValue=1,
        )
        layout.addWidget(self.projection)

    # ------------------------------------------------------------------------

    def getArguments(self):
        """
        Get arguments that are parsed in the setInitialWeights function, this
        function will return a dictionary that can be parsed into the function
        as keyword arguments.

        :return: Arguments
        :rtype: dict
        """
        return {
            "iterations": self.iterations.value(),
            "projection": self.projection.value()
        }


class WeightWidget(Qt.QWidget):
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # create layout
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create blend weight widget
        self.blend = widgets.LabelCheckbox(self, "Blend Weights:")
        self.blend.stateChanged.connect(self.refresh)
        layout.addWidget(self.blend)

        # create delinear widget
        self.delinear = widgets.LabelCheckbox(self, "De-Linearize Weights:")
        self.delinear.stateChanged.connect(self.refresh)
        layout.addWidget(self.delinear)

        # create delinear options widget
        self.tweening = widgets.TweeningOptions(self)
        layout.addWidget(self.tweening)

        # refresh
        self.refresh()

    # ------------------------------------------------------------------------

    def getArguments(self):
        """
        Get arguments that are parsed in the setInitialWeights function, this
        function will return a dictionary that can be parsed into the function
        as keyword arguments.

        :return: Arguments
        :rtype: dict
        """
        # get data
        blend = self.blend.isChecked()
        method = self.tweening.currentMethod() \
            if self.blend.isChecked() and self.delinear.isChecked() \
            else None

        # return data
        return {
            "blend": blend,
            "blendMethod": method
        }

    # ------------------------------------------------------------------------

    def refresh(self, *args, **kwargs):
        with ui.BlockSignals(self.blend, self.delinear, self.tweening):
            # turn of delinear weights off by default
            self.delinear.setEnabled(False)
            self.tweening.setEnabled(False)

            # if blend is turned on, we can also enable the delinear weights
            # widget
            if self.blend.isChecked():
                self.delinear.setEnabled(True)

                # if the delinear is turned on, we must also show the delinear
                # options widget
                if self.delinear.isChecked():
                    self.tweening.setEnabled(True)

            else:
                self.delinear.setChecked(False)


# ----------------------------------------------------------------------------


class InitializeWeightsWidget(Qt.QWidget):
    """
    Widget used to initialize the weights of the selected meshes and/or
    vertices.
    
    :param QWidget parent:   
    """
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        # ui
        self.setParent(parent)        
        self.setWindowFlags(Qt.Qt.Window)

        self.setWindowTitle(WINDOW_TITLE)           
        self.resize(400, 25)

        # set icon
        path = ui.getIconPath(WINDOW_ICON)
        self.setWindowIcon(Qt.QIcon(path))

        # create layout
        layout = Qt.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # create mesh selection
        self.mesh = MeshSelectionWidget(self)
        layout.addWidget(self.mesh)

        # create joint selection
        self.joints = JointSelectionWidget(self)
        layout.addWidget(self.joints)

        # create divider
        divider = widgets.Divider(self)
        layout.addWidget(divider)

        # create smooth label
        label = Qt.QLabel(self)
        label.setText("Smooth Options")
        label.setFont(ui.BOLT_FONT)
        layout.addWidget(label)

        # create smooth widget
        self.smooth = SmoothWidget(self)
        layout.addWidget(self.smooth)

        # create divider
        divider = widgets.Divider(self)
        layout.addWidget(divider)

        # create weights label
        label = Qt.QLabel(self)
        label.setText("Weight Options")
        label.setFont(ui.BOLT_FONT)
        layout.addWidget(label)

        # create weights widget
        self.weights = WeightWidget(self)
        layout.addWidget(self.weights)

        # create divider
        divider = widgets.Divider(self)
        layout.addWidget(divider)

        # create button
        apply = Qt.QPushButton(self)
        apply.setFont(ui.FONT)
        apply.setText("Apply")
        apply.released.connect(self.apply)
        layout.addWidget(apply)

    # ------------------------------------------------------------------------
    
    def apply(self):
        """
        :raise ValueError: When no mesh(es) are specified
        :raise ValueError: When no joint(s) are specified
        """
        # meshes
        meshes = self.mesh.getArguments()

        # validate meshes
        if not meshes:
            raise ValueError("No mesh(es) specified!")

        # get arguments
        arguments = {}
        arguments.update(self.joints.getArguments())
        arguments.update(self.smooth.getArguments())
        arguments.update(self.weights.getArguments())

        # validate joints
        if not arguments.get("joints"):
            raise ValueError("No joint(s) specified!")

        # loop meshes
        for mesh in meshes:
            # update arguments
            arguments.update(mesh)

            # call function
            weight.setInitialWeights(**arguments)


def show():
    initializeWeights = InitializeWeightsWidget(ui.getMayaMainWindow())
    initializeWeights.show()
