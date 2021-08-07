import logging
from maya import cmds
from maya.api import OpenMaya
from maya.api import OpenMayaAnim

from skinning.utils import api
from skinning.utils import math
from skinning.utils import skin
from skinning.utils import naming
from skinning.utils import influence
from skinning.utils import decorator
from skinning.utils.progress import Progress


__all__ = [
    "initialize_weights"
]
log = logging.getLogger(__name__)


class InfluenceConnectivity(object):
    """
    An influence connections is a connection between two influences. It has
    utility functions to find the closest point on this line between the
    two connections but also its parameter.
    """
    def __init__(self, source, target):
        self.source = source
        self.target = target

    # ------------------------------------------------------------------------

    def closest_point_on_line(self, point):
        """
        :param OpenMaya.MVector point:
        :return: Closest point
        :rtype: OpenMaya.MVector
        """
        return math.closest_point_on_line(
            self.source.get_position(),
            self.target.get_position(),
            point
        )

    def parameter_on_line(self, point):
        """
        :param OpenMaya.MVector point:
        :return: Parameter
        :rtype: float
        """
        closest_point = self.closest_point_on_line(point)
        return math.parameter_of_point_on_line(
            self.source.get_position(),
            self.target.get_position(),
            closest_point
        )


class SkeletonConnectivity(influence.Skeleton):
    """
    The skeleton connectivity class will allow for connectivity to be
    created between the influences in the skeleton. Closest points and
    parameters can be found from world space positions points.
    """
    def __init__(self, influences):
        super(SkeletonConnectivity, self).__init__(influences)
        self.connections = []

        for child in self.children:
            self.build_connections_map(child)

    # ------------------------------------------------------------------------

    def build_connections_map(self, parent):
        """
        :param Influence parent:
        """
        parent_point = parent.get_position()
        children = [child for child in parent.children if (parent_point - child.get_position()).length()]
        children.sort(key=lambda x: (parent_point - x.get_position()).length(), reverse=True)

        # check connectivity between children, this happens with twisters for
        # example, it will filter out the twisters rather than creating
        # overlapping connectivity.
        for child, child_next in zip(children, children[1:] + [parent]):
            child_point = child.get_position()
            child_next_point = child_next.get_position()
            if (child_point - child_next_point).length() < 0.001:
                continue

            closest_point = math.closest_point_on_line(parent_point, child_point, child_next_point)
            distance = (child_next_point - closest_point).length()
            if distance < 0.001:
                self.connections.append(InfluenceConnectivity(child_next, child))
            else:
                self.connections.append(InfluenceConnectivity(parent, child))

        for child in parent.children:
            self.build_connections_map(child)

    def get_closest_connection(self, point):
        """
        :param OpenMaya.MVector point:
        :return: Influence connection
        :rtype: OpenMaya.MVector, InfluenceConnectivity
        :raise RuntimeError: When no connections are mapped.
        """
        if not self.connections:
            raise RuntimeError("Unable to query closest connections "
                               "as no connections are mapped.")

        closest_connection = self.connections[0]
        closest_point = closest_connection.closest_point_on_line(point)
        closest_distance = (point - closest_point).length()

        for connection in self.connections[1:]:
            point_on_line = connection.closest_point_on_line(point)
            distance = (point - point_on_line).length()

            if distance < closest_distance:
                closest_point = point_on_line
                closest_distance = distance
                closest_connection = connection

        return closest_point, closest_connection


@decorator.preserve_selection
def initialize_weights(
        geometry,
        joints,
        components=None,
        iterations=3,
        projection=0,
        blend=False,
        blend_method=None
):
    """
    The set initial weights function will set the skin weights on a mesh and
    the isolate only the provided components of any. Each vertex will only
    have one influence, the best influence is determined by generating lines
    for each of the joints and determining the line closest to the vertex. The
    vertex points can be altered as well using smoothing operations to details
    or overlapping and the project can be used to project the point along its
    normal to get it closer to the preferred joints.

    :param str geometry:
    :param list joints:
    :param list/None components:
    :param int iterations: Number of smoothing iterations
    :param float/int projection: Value between 0-1
    :param bool blend:
    :param str blend_method:
    :raise ValueError: When geometry is not a mesh.
    :raise ValueError: When blend method is not supported
    """
    if blend_method and not hasattr(math.ease, blend_method):
        raise ValueError("Blend method '{}' is not supported.".format(blend_method))

    points = []
    normals = []
    connections = {}
    blend_method = getattr(math.ease, blend_method) if blend_method else None

    if not components:
        geometry_dag, geometry_component = api.conversion.get_component(geometry)
    else:
        cmds.select(components)
        selection = OpenMaya.MGlobal.getActiveSelectionList()
        geometry_dag, geometry_component = selection.getComponent(0)

    if not geometry_dag.hasFn(OpenMaya.MFn.kMesh):
        raise RuntimeError("Unable to initialize weights, "
                           "node '{}' is not a mesh.".format(geometry))

    try:
        skin_cluster = skin.get_cluster(geometry)
        influence.add_influences(skin_cluster, joints)
    except RuntimeError:
        skin_cluster_name = "{}_SK".format(naming.get_leaf_name(geometry))
        skin_cluster = cmds.skinCluster(
            joints,
            geometry,
            name=skin_cluster_name,
            toSelectedBones=True,
            removeUnusedInfluence=False,
            maximumInfluences=4,
            obeyMaxInfluences=True,
            bindMethod=0,
            skinMethod=0,  # linear
            normalizeWeights=1,  # interactive
            weightDistribution=0,  # distance
        )[0]

    skin_cluster_obj = api.conversion.get_object(skin_cluster)
    skin_cluster_fn = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj)
    influences_mapper = {
        influence_dag.partialPathName(): i
        for i, influence_dag in enumerate(skin_cluster_fn.influenceObjects())
    }

    component_fn = OpenMaya.MFnSingleIndexedComponent(geometry_component)
    num_elements = component_fn.elementCount

    with Progress(num_elements + 6) as progress:
        # query geometry
        geometry_iter = OpenMaya.MItMeshVertex(geometry_dag)
        while not geometry_iter.isDone():
            points.append(OpenMaya.MVector(geometry_iter.position(OpenMaya.MSpace.kWorld)))
            normals.append(math.average_vector(geometry_iter.getNormals(OpenMaya.MSpace.kWorld)))
            connections[geometry_iter.index()] = geometry_iter.getConnectedVertices()

            geometry_iter.next()

        progress.next()

        # smooth points
        points = math.smooth_vectors(points, connections, iterations)
        progress.next()

        # smooth normals
        normals = math.smooth_vectors(normals, connections, iterations)
        progress.next()

        # initialize skeleton
        skeleton = SkeletonConnectivity(joints)
        progress.next()

        # initialize weights
        weights_old, num_influences = skin_cluster_fn.getWeights(geometry_dag, geometry_component)
        weights_new = OpenMaya.MDoubleArray([0.0] * num_elements * num_influences)
        progress.next()

        # loop components
        for i in range(num_elements):
            element = component_fn.element(i)
            point = points[element]
            normal = normals[element]
            closest_point, connection = skeleton.get_closest_connection(point)

            if projection:
                # get new point moving the point along the normal using the
                # project value as a multiplier to the closest distance.
                distance = (point - closest_point).length()
                point = point + (normal * distance * projection * -1)
                closest_point, connection = skeleton.get_closest_connection(point)

            parameter = connection.parameter_on_line(closest_point)
            if blend and blend_method:
                parameter = blend_method(parameter)
            elif not blend:
                parameter = int(parameter)

            weights_new[(i * num_influences) + influences_mapper[connection.source.path]] = 1 - parameter
            weights_new[(i * num_influences) + influences_mapper[connection.target.path]] = parameter
            progress.next()

        skin.set_weights(
            skin_cluster_fn,
            dag=geometry_dag,
            components=geometry_component,
            influences=OpenMaya.MIntArray(range(num_influences)),
            weights_old=weights_old,
            weights_new=weights_new
        )

        progress.next()

    log.info("Successfully initialize weights for '{}'.".format(geometry))
