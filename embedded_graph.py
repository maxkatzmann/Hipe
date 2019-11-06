from collections import deque
import networkx as nx
import native_coordinates
import math


class embedded_graph:
    def __init__(self):
        self.graph = nx.Graph()
        self.embedding = {}

    @staticmethod
    def add_grid_root_with_neighbors(grid, p, q, layers):
        # Add the root of the grid
        grid.graph.add_node(grid.graph.number_of_nodes())

        # The root has layer 0.
        layers.append(0)

        # Add edges from the root to its neighbors.
        for v in range(1, q + 1):
            grid.graph.add_node(grid.graph.number_of_nodes())

            # All these nodes have layer 1.
            layers.append(1)

            # Add the edge from the root to the node.
            grid.graph.add_edge(0, v)

        # Add the edges between the neighbors of the root.
        for v in range(1, q):
            grid.graph.add_edge(v, v + 1)
        grid.graph.add_edge(q, 1)

    # Adds the grid neighbors of a node and returns the vertices that have been
    # added in the process.
    @staticmethod
    def add_grid_neighbors(v, grid, p, q, max_depth, layers):
        # We do not add anything, if we have already reached the desired
        # maximum depth.
        layer = layers[v]
        if layer >= max_depth:
            return []

        current_neighbors = []
        for u in grid.graph.neighbors(v):
            current_neighbors.append(u)

        predecessor = current_neighbors[-1]
        successor = current_neighbors[-2]

        num_missing_neighbors = q - len(current_neighbors)

        new_neighbors = []

        for i in range(0, num_missing_neighbors):
            new_index = grid.graph.number_of_nodes()
            grid.graph.add_node(new_index)
            layers.append(layer + 1)
            grid.graph.add_edge(v, new_index)
            new_neighbors.append(new_index)

        grid.graph.add_edge(predecessor, new_neighbors[0])
        for i in range(0, len(new_neighbors) - 1):
            grid.graph.add_edge(new_neighbors[i], new_neighbors[i + 1])

        grid.graph.add_edge(new_neighbors[-1], successor)

        return new_neighbors

    # Embedds the root of a grid.
    @staticmethod
    def embed_grid_root(grid, p, q, angle, edge_length):
        for v in range(1, 8):
            grid.embedding[v] = native_coordinates.polar_coordinate(
                edge_length,
                float(v) * angle)

    # Embeds the childen of a node and returns the new vertices that now need
    # coordinates.
    @staticmethod
    def embed_children_of_node(v, grid, p, q, angle, edge_length):
        nodes_to_embed = []
        last_embedded_node = -1
        for neighbor in grid.graph.neighbors(v):
            # We don't want to embed the root again.
            if neighbor == 0:
                continue

            if grid.embedding[neighbor].r == 0.0 or grid.embedding[
                    neighbor].phi == 0.0:
                nodes_to_embed.append(neighbor)
            else:
                last_embedded_node = neighbor

        # If we don't have to embed any nodes, we can stop here.
        if not nodes_to_embed:
            return []

        if last_embedded_node <= 0:
            print("ERROR: Did not find node to rotate from.")
            return

        # Translate the current node v to the origin and perform the same
        # translation to the last embedded node.
        v_coordinate = grid.embedding[v]
        last_embedded_coordinate = grid.embedding[last_embedded_node]

        # Rotate both vertices such that v is on the reference ray (x-axis).
        rotation_angle = v_coordinate.phi
        last_embedded_coordinate_rotated = native_coordinates.coordinate_rotated_around_origin_by_angle(
            last_embedded_coordinate, -rotation_angle)

        # Now we translate both vertices such that v is on the origin.
        distance = v_coordinate.r
        last_embedded_coordinate_rotated_translated = native_coordinates.coordinate_translated_along_x_axis_by_hyperbolic_distance(
            last_embedded_coordinate_rotated, -distance)

        # Position the vertices around the translated vertex.
        for index, node in enumerate(nodes_to_embed):
            new_coordinate = native_coordinates.coordinate_rotated_around_origin_by_angle(
                last_embedded_coordinate_rotated_translated,
                float(index + 1) * angle)

            new_coordinate_translated = native_coordinates.coordinate_translated_along_x_axis_by_hyperbolic_distance(
                new_coordinate, distance)

            new_coordinate_translated_rotated = native_coordinates.coordinate_rotated_around_origin_by_angle(
                new_coordinate_translated, rotation_angle)

            grid.embedding[node] = new_coordinate_translated_rotated

        return nodes_to_embed

    # Creates a regular 3,7 grid with the passed depth.
    @staticmethod
    def create_grid(depth):
        # The parameters of the tiling.
        p = 3
        q = 7

        grid = embedded_graph()

        # We keep track of the layers of the nodes.
        layers = []

        # Add the root of the grid, including the neighbors.
        embedded_graph.add_grid_root_with_neighbors(grid, p, q, layers)

        priority_queue = deque([])
        for v in range(1, q + 1):
            priority_queue.append(v)

        # While there is something in the priority_queue...
        while priority_queue:
            v = priority_queue.popleft()
            new_nodes = embedded_graph.add_grid_neighbors(
                v, grid, p, q, depth, layers)
            if new_nodes:
                priority_queue.extend(new_nodes)

        # Now we have the final graph data structure, it remains to compute the
        # coordinates of the nodes.

        # We first determine the angle between neighbors of a node and the
        # length of the edges, which is defined by this angle.
        angle = 2.0 * math.pi / float(q)

        # The edge length is determined by using the second law of hyperbolic
        # cosines, solving it for the side length and setting all three angles
        # to the angular distance.
        edge_length = math.acosh(
            (math.cos(angle) + math.cos(angle) * math.cos(angle)) /
            (math.sin(angle) * math.sin(angle)))

        # Initialize the embedding by setting all coordinates to be the origin.
        for v in grid.graph.nodes:
            grid.embedding[v] = native_coordinates.polar_coordinate(0, 0)

        # We start by embedding the root of the grid.
        embedded_graph.embed_grid_root(grid, p, q, angle, edge_length)

        # Then we embed the children one after another.
        priority_queue = deque([])
        for v in range(1, q + 1):
            priority_queue.append(v)

        while priority_queue:
            v = priority_queue.popleft()
            new_nodes = embedded_graph.embed_children_of_node(
                v, grid, p, q, angle, edge_length)

            priority_queue.extend(new_nodes)

        return grid
