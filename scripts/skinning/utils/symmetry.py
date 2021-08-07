from maya.api import OpenMaya
from collections import OrderedDict

from skinning.utils import api
from skinning.utils import math


CENTER = 0
LEFT = 1
RIGHT = 2


class Symmetry(object):
    """
    Create a symmetry map for a provided mesh using an edge that lies on the
    symmetry plane. This map can be used to link a face, edge or vertex index
    to its symmetrical counter part. The face, edge and vertex mappers are
    stored at a class level which will result in a cache that can be used when
    to be able to use the symmetry class multiple times without having to
    recalculate the mapping.
    """
    _faces = {}
    _edges = {}
    _vertices = {}
    _matrices = {}

    def __init__(self, node):
        self.dag = api.conversion.get_dag(node)
        self.dag.extendToShape()
        self.path = self.dag.partialPathName()

        self.mesh_fn = OpenMaya.MFnMesh(self.dag)
        self.mesh_edge_iter = OpenMaya.MItMeshEdge(self.dag)
        self.mesh_face_iter = OpenMaya.MItMeshPolygon(self.dag)

    # ------------------------------------------------------------------------

    @property
    def edges(self):
        """
        :return: Edges
        :rtype: OrderedDict
        """
        if self.path not in self._edges:
            raise RuntimeError("Symmetry not calculated for mesh '{}'.".format(self.path))

        return self._edges[self.path]

    @property
    def faces(self):
        """
        :return: Faces
        :rtype: OrderedDict
        """
        if self.path not in self._faces:
            raise RuntimeError("Symmetry not calculated for mesh '{}'.".format(self.path))

        return self._faces[self.path]

    @property
    def vertices(self):
        """
        :return: Vertices
        :rtype: OrderedDict
        """
        if self.path not in self._vertices:
            raise RuntimeError("Symmetry not calculated for mesh '{}'.".format(self.path))

        return self._vertices[self.path]

    @property
    def matrices(self):
        """
        :return: Matrix
        :rtype: OpenMaya.MMatrix
        """
        if self.path not in self._matrices:
            raise RuntimeError("Symmetry not calculated for mesh '{}'.".format(self.path))

        return self._matrices[self.path]

    # ------------------------------------------------------------------------

    @staticmethod
    def filter(data, mode=0):
        """
        :param OrderedDict data:
        :param int mode:
        :return: Indices
        :rtype: list[int]
        :raise RuntimeError: When node is not valid.
        """
        seen = set()
        indices = []

        if mode == CENTER:
            return [k for k, v in data.items() if k == v]
        elif mode == LEFT:
            for k, v in data.items():
                if k not in seen and k != v:
                    indices.append(k)
                seen.add(v)
            return indices
        elif mode == RIGHT:
            for k, v in data.items():
                if v not in seen and k != v:
                    indices.append(v)
                seen.add(k)
            return indices
        else:
            raise ValueError("Mode '{}' is not valid.".format(mode))

    # ------------------------------------------------------------------------

    def calculate_symmetry(self, edge_index, use_cache=False):
        """
        :param int edge_index:
        :param bool use_cache:
        :raise RuntimeError: When mesh is not symmetrical.
        """
        def get_connected_edges(face, edge, reverse):
            """
            :param int face:
            :param int edge:
            :param bool reverse:
            :return: Edges
            :rtype: list[int]
            """
            self.mesh_face_iter.setIndex(face)

            edges_connected = self.mesh_face_iter.getEdges()
            edges_connected = list(reversed(edges_connected)) if reverse else list(edges_connected)
            edges_num = len(edges_connected)
            edges_start = edges_connected.index(edge)
            edges_connected = (edges_connected * 2)[edges_start: edges_start + edges_num]

            return [index for index in edges_connected if index not in edges_seen]

        def get_connected_vertices(edge, reverse=True):
            """
            :param int edge:
            :param bool reverse:
            :return: Vertices
            :rtype: list[int]
            """
            self.mesh_edge_iter.setIndex(edge)
            vertices_connected = [self.mesh_edge_iter.vertexId(i) for i in (0, 1)]
            vertices_connected = list(reversed(vertices_connected)) if reverse else list(vertices_connected)

            return [index for index in vertices_connected if index not in vertices_seen]

        def get_connected_faces(edge, reverse=True):
            """
            :param int edge:
            :param bool reverse:
            :return: Faces
            :rtype: list[int]
            """
            self.mesh_edge_iter.setIndex(edge)

            faces_connected = self.mesh_edge_iter.getConnectedFaces()
            faces_connected = reversed(faces_connected) if reverse else faces_connected

            return [index for index in faces_connected if index not in faces_seen]

        if use_cache and self.path in self._vertices:
            return

        # declare sets, these will allow for quick look ups to make sure check if the
        # components have been processed or not.
        faces_seen = set()
        edges_seen = set()
        vertices_seen = set()

        # empty lists that get populated when processing the mesh, the count is the
        # number of edges connected to a face. This will help validating symmetry.
        processing = []
        faces = OrderedDict()
        edges = OrderedDict()
        vertices = OrderedDict()

        self.mesh_edge_iter.setIndex(edge_index)
        edges[edge_index] = edge_index

        vertex_indices = [self.mesh_edge_iter.vertexId(0), self.mesh_edge_iter.vertexId(1)]
        vertices[vertex_indices[0]] = vertex_indices[0]
        vertices[vertex_indices[1]] = vertex_indices[1]
        vertices_seen.update(vertex_indices)

        face_indices = self.mesh_edge_iter.getConnectedFaces()
        faces[face_indices[0]] = face_indices[1]
        processing.append((face_indices[0], edge_index))

        while processing:
            face_index, edge_index = processing.pop(0)
            edge_indices = get_connected_edges(face_index, edge_index, reverse=False)
            edge_indices_reverse = get_connected_edges(faces[face_index], edges[edge_index], reverse=True)

            if len(edge_indices) != len(edge_indices_reverse):
                raise RuntimeError("Unable to calculate symmetry for mesh '{}', "
                                   "mesh is not symmetrical.".format(self.path))

            for edge_index, edge_reverse_index in zip(edge_indices, edge_indices_reverse):
                edges[edge_index] = edge_reverse_index
                edges_seen.add(edge_index)
                edges_seen.add(edge_reverse_index)

                vertex_indices = get_connected_vertices(edge_index, reverse=False)
                vertex_reverse_indices = get_connected_vertices(edge_reverse_index, reverse=True)

                if len(vertex_indices) != len(vertex_reverse_indices):
                    raise RuntimeError("Unable to calculate symmetry for mesh '{}', "
                                       "mesh is not symmetrical.".format(self.path))

                for vertex_index, vertex_reverse_index in zip(vertex_indices, vertex_reverse_indices):
                    vertices[vertex_index] = vertex_reverse_index
                    vertices_seen.add(vertex_index)
                    vertices_seen.add(vertex_reverse_index)

                face_indices = get_connected_faces(edge_index, reverse=False)
                face_reverse_indices = get_connected_faces(edge_reverse_index, reverse=True)

                for face_index, face_reverse_index in zip(face_indices, face_reverse_indices):
                    faces[face_index] = face_reverse_index
                    faces_seen.add(face_index)
                    faces_seen.add(face_reverse_index)

                    processing.append((face_index, edge_index))

        # calculate matrix using the all of the center vertices and an up
        # vector of +y.
        points = self.mesh_fn.getPoints(OpenMaya.MSpace.kWorld)
        points_center = [OpenMaya.MVector(points[k]) for k, v in vertices.items() if k == v]

        centroid = math.average_vector(points_center)
        up = OpenMaya.MVector(0, 1, 0)
        side = OpenMaya.MVector(1, 0, 0)

        for i, (vector1, vector2) in enumerate(zip(points_center[:-1], points_center[1:])):
            cross = vector1 ^ vector2
            cross.normalize()

            if i == 0:
                multiplier = 1 if side * cross > 0 else -1
                side = cross * multiplier
            else:
                angle = side.angle(cross)
                if angle > math.pi * 0.5:
                    cross *= -1

            side += cross

        side.normalize()
        forward = side ^ up
        up = forward ^ side

        matrix = OpenMaya.MMatrix(
            list(side) + [0] +
            list(up.normal()) + [0] +
            list(forward.normal()) + [0] +
            list(centroid) + [1]
        )

        # determine side order by checking of the vertex is positive or
        # negative when multiplying with the inverse matrix.
        for k, v in vertices.items():
            if k == v:
                continue

            point = OpenMaya.MPoint(points[k]) * matrix.inverse()
            point_reverse = OpenMaya.MPoint(points[v]) * matrix.inverse()

            if point.x > 0 and point_reverse.x < 0:
                break
            elif point.x < 0 and point_reverse.x > 0:
                faces = OrderedDict((v, k) for k, v in faces.items())
                edges = OrderedDict((v, k) for k, v in edges.items())
                vertices = OrderedDict((v, k) for k, v in vertices.items())
                break

        # add the reverse of the mappings to the same dictionary. This will
        # allow us to map from left to right and right to left.
        for k, v in list(faces.items()):
            faces[v] = k
        for k, v in list(edges.items()):
            edges[v] = k
        for k, v in list(vertices.items()):
            vertices[v] = k

        self._faces[self.path] = faces
        self._edges[self.path] = edges
        self._vertices[self.path] = vertices
        self._matrices[self.path] = matrix

    # ------------------------------------------------------------------------

    @classmethod
    def clear(cls):
        """
        Clear any symmetry data stored on the class, this will make sure that
        any symmetry data needs to be freshly calculated.
        """
        cls._faces.clear()
        cls._edges.clear()
        cls._vertices.clear()
