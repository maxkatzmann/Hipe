# This program visualizes hyperbolic circles using the native representation.
# Copyright (C) 2018    Maximilian Katzmann
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# You can contact the author via email: max.katzmann@gmail.com

from tkinter import *
import euclidean_coordinates
import embedded_graph
import native_coordinates
import math


class point:
    def __init__(self, coordinate, color):
        self.coordinate = coordinate
        self.color = color
        self.drawn_items = None


class circle:
    def __init__(self, coordinate, radius, color):
        self.coordinate = coordinate
        self.radius = radius
        self.color = color
        self.circle_points = []
        self.drawn_items = None


class edge:
    def __init__(self, index1, index2):
        self.index1 = index1
        self.index2 = index2
        self.edge_points = []
        self.drawn_items = None

        self.hypercycle_radius = 0
        self.hypercycle_points = None
        self.drawn_hypercycle_items = None

    def __str__(self):
        return "(" + str(self.index1) + ", " + str(self.index2) + ")"


def is_circle_item(item):
    return isinstance(item, circle)


class drawer:

    colors = [
        "black", "green", "blue", "purple", "deep pink", "red4", "orange",
        "gold"
    ]
    selection_border_size = 1
    selection_radius = 30
    primary_selection_color = "red"
    secondary_selection_color = "magenta"
    point_size = 3

    def __init__(self, canvas, scale):
        self.canvas = canvas
        self.scale = scale

        # The embedded graph
        self.embedded_graph = None

        # The drawn items associated with the embedded graph.
        self.embedded_graph_items = None

        # The grid
        self.grid_radius = 0

        # The regular grid
        self.regular_grid = None
        self.regular_grid_depth = 0

        # The drawn items associated with regular grid.
        self.regular_grid_items = None

        # The drawn items associated with the snapping feature.
        self.snap_items = None

        # The drawn items that are used to draw the circle showing what the
        # mouse would select.
        self.mouse_location_cirlce_items = None

    def canvas_point_from_hyperbolic_coordinate(self, point):

        center = euclidean_coordinates.euclidean_coordinate(
            self.canvas.winfo_width() / 2.0,
            self.canvas.winfo_height() / 2.0)

        euclidean_point = point.to_euclidean_coordinate_with_scale(self.scale)

        euclidean_point.x = center.x - euclidean_point.x
        euclidean_point.y = center.y - euclidean_point.y

        return euclidean_point

    def hyperbolic_coordinate_from_canvas_point(self, point):
        center = euclidean_coordinates.euclidean_coordinate(
            self.canvas.winfo_width() / 2.0,
            self.canvas.winfo_height() / 2.0)
        relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(
            point, center)
        native_point = relative_point.to_native_coordinate_with_scale(
            self.scale)
        return native_point

    def draw(self, items, edges, selected_nodes, mouse_location,
             snapped_item_radial, snapped_item_angular):
        self.draw_with_functions(items, edges, selected_nodes, mouse_location,
                                 self.draw_path, self.draw_circle)

        # Clear mouse location circle.
        if self.mouse_location_cirlce_items:
            for item in self.mouse_location_cirlce_items:
                self.canvas.delete(item)
            self.mouse_location_cirlce_items = None

        # Clear snap guides.
        if self.snap_items:
            for item in self.snap_items:
                self.canvas.delete(item)
            self.snap_items = None

        # Drawing the selection circle, if there is one.
        if mouse_location is not None:
            self.mouse_location_cirlce_items = self.draw_circle(
                mouse_location, self.selection_radius, 0.0, 2.0 * math.pi,
                False, "", self.secondary_selection_color, 1.0)

        # Drawing the snapping guides if there are any.
        if len(selected_nodes) > 0:
            center = euclidean_coordinates.euclidean_coordinate(
                self.canvas.winfo_width() / 2.0,
                self.canvas.winfo_height() / 2.0)
            selected_index = selected_nodes[-1]
            selected_coordinate = items[selected_index].coordinate
            selected_coordinate_relative = euclidean_coordinates.coordinate_relative_to_coordinate(
                selected_coordinate, center)
            radius = selected_coordinate_relative.to_native_coordinate_with_scale(
                1.0).r
            selected_coordinate_native = self.hyperbolic_coordinate_from_canvas_point(
                selected_coordinate)

            self.snap_items = []

            if snapped_item_radial is not None:
                snapped_coordinate = items[snapped_item_radial].coordinate
                snapped_coordinate_native = self.hyperbolic_coordinate_from_canvas_point(
                    snapped_coordinate)

                # The radii of the two coordinate should match since we snapped to it.
                # We now draw the circle connecting the two
                circle_from_select_to_snapped = True

                signed_angular_distance = snapped_coordinate_native.phi - \
                    selected_coordinate_native.phi
                if signed_angular_distance > 0:
                    if signed_angular_distance < math.pi:
                        circle_from_select_to_snapped = False
                else:
                    if signed_angular_distance < -math.pi:
                        circle_from_select_to_snapped = False

                start_angle = selected_coordinate_native.phi
                end_angle = snapped_coordinate_native.phi

                if not circle_from_select_to_snapped:
                    start_angle = snapped_coordinate_native.phi
                    end_angle = selected_coordinate_native.phi

                drawing_start_angle = ((math.pi - start_angle) +
                                       (2.0 * math.pi)) % (2.0 * math.pi)
                drawing_end_angle = ((math.pi - end_angle) +
                                     (2.0 * math.pi)) % (2.0 * math.pi)

                radial_snap_items = self.draw_circle(
                    center, radius, drawing_start_angle, drawing_end_angle,
                    circle_from_select_to_snapped, "",
                    self.secondary_selection_color, 1.0)
                self.snap_items += radial_snap_items

            if snapped_item_angular is not None:
                snapped_coordinate = items[snapped_item_angular].coordinate
                angular_snap_items = self.draw_line_from_coordinate_to_coordinate(
                    selected_coordinate, snapped_coordinate,
                    self.secondary_selection_color, 1.0)
                self.snap_items.append(angular_snap_items)

    def draw_embedded_graph(self, center, path_func, circle_func):
        if not self.embedded_graph:
            return

        if self.embedded_graph_items:
            return

        self.embedded_graph_items = []

        items = []
        for node in self.embedded_graph.embedding:
            coordinate = self.embedded_graph.embedding[node]
            canvas_coordinate = self.canvas_point_from_hyperbolic_coordinate(
                coordinate)
            items.append(point(canvas_coordinate, 0))

        self.embedded_graph_items += self.draw_points(items, [], center,
                                                      circle_func)

        # Create the edges.
        edges = []
        for u, v in self.embedded_graph.graph.edges:
            edges.append(edge(u, v))

        self.embedded_graph_items += self.draw_edges(edges, items, center,
                                                     path_func)

    def draw_regular_grid(self, center, path_func, circle_func):
        if self.regular_grid_depth <= 0:
            return

        if self.regular_grid_items:
            return

        self.regular_grid_items = []

        if not self.regular_grid:
            self.regular_grid = embedded_graph.embedded_graph.create_grid(
                self.regular_grid_depth)

        # Create the points describing the coordinates.
        items = []
        for node in self.regular_grid.embedding:
            coordinate = self.regular_grid.embedding[node]
            canvas_coordinate = self.canvas_point_from_hyperbolic_coordinate(
                coordinate)
            items.append(point(canvas_coordinate, 0))

        self.regular_grid_items += self.draw_points(items, [], center,
                                                    circle_func)

        # Create the edges.
        edges = []
        for u, v in self.regular_grid.graph.edges:
            edges.append(edge(u, v))

        self.regular_grid_items += self.draw_edges(edges, items, center,
                                                   path_func)

    def draw_grid(self, center, path_func, circle_func):
        # Drawing the grid
        if self.grid_radius <= 0:
            return

        grid_color = "gray"
        alpha = 0.75
        layer_width = math.log(2) / alpha
        number_of_layers = math.floor(self.grid_radius / layer_width)

        # Drawing the layers
        for layer in range(number_of_layers):
            outer_radius = self.grid_radius - layer * layer_width
            inner_radius = self.grid_radius - (layer + 1) * layer_width
            circle_func(center, self.scale * outer_radius, 0.0, 2.0 * math.pi,
                        True, "", grid_color, 1.0)

            # Drawing the cell borders
            number_of_cells_in_layer = math.ceil(
                math.pow(2, number_of_layers - layer))
            angular_cell_width = 2.0 * math.pi / number_of_cells_in_layer
            for cell in range(number_of_cells_in_layer):
                inner_cell_point = native_coordinates.polar_coordinate(
                    inner_radius, cell * angular_cell_width)
                outer_cell_point = native_coordinates.polar_coordinate(
                    outer_radius, cell * angular_cell_width)

                converted_inner_point = inner_cell_point.to_euclidean_coordinate_with_scale(
                    self.scale)
                converted_outer_point = outer_cell_point.to_euclidean_coordinate_with_scale(
                    self.scale)

                euclidean_inner_point = euclidean_coordinates.coordinate_relative_to_coordinate(
                    center, converted_inner_point)
                euclidean_outer_point = euclidean_coordinates.coordinate_relative_to_coordinate(
                    center, converted_outer_point)

                path_func([euclidean_inner_point, euclidean_outer_point],
                          False, grid_color, 1.0)

        # Drawing the inner radius of the inner most layer
        circle_func(
            center,
            self.scale * (self.grid_radius - number_of_layers * layer_width),
            0.0, 2.0 * math.pi, True, "", grid_color, 1.0)

    def draw_circles(self, items, selected_nodes, center, mouse_location,
                     path_func, circle_func):
        for index, item in enumerate(items):
            if not is_circle_item(item):
                continue

            # Don't draw an item if its already drawn.
            if item.drawn_items:
                continue

            # Check whether we should highlight the whole circle instead of only the point.
            should_highlight_primary_selection = False

            if index in selected_nodes:
                if selected_nodes[-1] == index:
                    item.drawn_items = circle_func(
                        item.coordinate, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.primary_selection_color,
                        self.primary_selection_color,
                        self.selection_border_size)
                    if mouse_location is not None:
                        should_highlight_primary_selection = True
                else:
                    item.drawn_items = circle_func(
                        item.coordinate, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.secondary_selection_color,
                        self.secondary_selection_color,
                        self.selection_border_size)
            else:
                item.drawn_items = circle_func(item.coordinate,
                                               self.point_size, 0.0,
                                               2.0 * math.pi, True,
                                               self.colors[item.color],
                                               self.colors[item.color],
                                               self.selection_border_size)

            converted_points = []

            if len(item.circle_points) > 0:
                converted_points = item.circle_points
            else:
                circle_size = item.radius
                native_point = self.hyperbolic_coordinate_from_canvas_point(
                    item.coordinate)

                circle_points = native_coordinates.render_points_for_circle_with_center_and_radius(
                    native_point, circle_size)
                for i in range(len(circle_points)):
                    circle_point = circle_points[i]
                    converted_point = circle_point.to_euclidean_coordinate_with_scale(
                        self.scale)
                    euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(
                        center, converted_point)
                    converted_points.append(euclidean_circle_point)
                item.circle_points = converted_points

            circle_color = self.colors[item.color]

            if should_highlight_primary_selection:
                circle_color = self.secondary_selection_color

            item.drawn_items += path_func(converted_points, True, circle_color,
                                          2.0)

    def draw_points(self, items, selected_nodes, center, circle_func):
        drawn_point_items = []
        for index, item in enumerate(items):
            if is_circle_item(item):
                continue

            # Don't draw an item if already has drawn items.
            if item.drawn_items:
                continue

            if index in selected_nodes:
                if selected_nodes[len(selected_nodes) - 1] == index:
                    item.drawn_items = circle_func(
                        item.coordinate, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.primary_selection_color,
                        self.primary_selection_color,
                        self.selection_border_size)
                else:
                    item.drawn_items = circle_func(
                        item.coordinate, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.secondary_selection_color,
                        self.secondary_selection_color,
                        self.selection_border_size)
            else:
                item.drawn_items = circle_func(item.coordinate,
                                               self.point_size, 0.0,
                                               2.0 * math.pi, True,
                                               self.colors[item.color],
                                               self.colors[item.color],
                                               self.selection_border_size)

            drawn_point_items += item.drawn_items

        return drawn_point_items

    def draw_edges(self, edges, items, center, path_func):
        drawn_edge_items = []

        # Drawing the edges
        for edge in edges:

            # Only draw edges that have not been drawn yet.
            if edge.drawn_items:
                continue

            color = "black"
            item1 = items[edge.index1]
            item2 = items[edge.index2]
            if item1.color == item2.color:
                color = self.colors[item1.color]

            relative_point1 = euclidean_coordinates.coordinate_relative_to_coordinate(
                item1.coordinate, center)
            native_point1 = relative_point1.to_native_coordinate_with_scale(
                self.scale)
            relative_point2 = euclidean_coordinates.coordinate_relative_to_coordinate(
                item2.coordinate, center)
            native_point2 = relative_point2.to_native_coordinate_with_scale(
                self.scale)

            converted_points = []
            if len(edge.edge_points) > 0:
                converted_points = edge.edge_points
            else:
                line_points = native_coordinates.render_points_for_line_from_to(
                    native_point1, native_point2)

                for i in range(len(line_points)):
                    converted_point = line_points[
                        i].to_euclidean_coordinate_with_scale(self.scale)
                    euclidean_line_point = euclidean_coordinates.coordinate_relative_to_coordinate(
                        center, converted_point)
                    converted_points.append(euclidean_line_point)

                edge.edge_points = converted_points

            edge.drawn_items = path_func(converted_points, False, color, 2.0)

            drawn_edge_items += edge.drawn_items

            # If the edge does not have a hypercycle, we continue with the next
            # edge. Otherwise, we draw the hypercycle.
            if edge.hypercycle_radius <= 0:
                continue

            # If the hypercycle of the edge is already drawn, we don't need to draw it again.
            if edge.drawn_hypercycle_items:
                continue

            hypercycle_upper_points = []
            hypercycle_lower_points = []

            if not edge.hypercycle_points is None:
                hypercycle_upper_points = edge.hypercycle_points.upper_samples
                hypercycle_lower_points = edge.hypercycle_points.lower_samples
            else:
                hypercycle_points = native_coordinates.render_points_for_hypercycle_around_points(
                    native_point1, native_point2, edge.hypercycle_radius)

                # The hypercycle_points are in native coordinates, now we
                # have to convert them to the canvas.
                for i in range(len(hypercycle_points.upper_samples)):
                    upper_sample = hypercycle_points.upper_samples[i]
                    lower_sample = hypercycle_points.lower_samples[i]

                    converted_upper_point = upper_sample.to_euclidean_coordinate_with_scale(
                        self.scale)
                    euclidean_upper_point = euclidean_coordinates.coordinate_relative_to_coordinate(
                        center, converted_upper_point)

                    converted_lower_point = lower_sample.to_euclidean_coordinate_with_scale(
                        self.scale)
                    euclidean_lower_point = euclidean_coordinates.coordinate_relative_to_coordinate(
                        center, converted_lower_point)

                    hypercycle_upper_points.append(euclidean_upper_point)
                    hypercycle_lower_points.append(euclidean_lower_point)

                edge.hypercycle_points = native_coordinates.hypercycle_points(
                    upper_samples=hypercycle_upper_points,
                    lower_samples=hypercycle_lower_points)

            drawn_upper_items = path_func(hypercycle_upper_points, False,
                                          color, 2.0)
            drawn_lower_items = path_func(hypercycle_lower_points, False,
                                          color, 2.0)
            edge.drawn_hypercycle_items = drawn_upper_items + drawn_lower_items

            drawn_edge_items += edge.drawn_hypercycle_items

        return drawn_edge_items

    def draw_with_functions(self, items, edges, selected_nodes, mouse_location,
                            path_func, circle_func):
        center = euclidean_coordinates.euclidean_coordinate(
            self.canvas.winfo_width() / 2.0,
            self.canvas.winfo_height() / 2.0)

        # Drawing the origin
        circle_func(center, self.point_size, 0.0, 2.0 * math.pi, True, "blue",
                    "blue", 1.0)

        # Draw the regular grid
        self.draw_regular_grid(center, path_func, circle_func)

        # Draw the embedded graph
        self.draw_embedded_graph(center, path_func, circle_func)

        # Draw the grid
        self.draw_grid(center, path_func, circle_func)

        # Drawing the circles
        self.draw_circles(items, selected_nodes, center, mouse_location,
                          path_func, circle_func)

        # Drawing the points.
        self.draw_points(items, selected_nodes, center, circle_func)

        # Drawing the edges.
        self.draw_edges(edges, items, center, path_func)

    def draw_circle(self, center, radius, start_angle, end_angle, is_clockwise,
                    fill_color, border_color, width):

        upper_left = euclidean_coordinates.euclidean_coordinate(
            center.x - radius, center.y - radius)
        lower_right = euclidean_coordinates.euclidean_coordinate(
            center.x + radius, center.y + radius)

        arcs = []

        if len(fill_color) > 0:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                arc1 = self.canvas.create_arc(upper_left.x,
                                              upper_left.y,
                                              lower_right.x,
                                              lower_right.y,
                                              style=PIESLICE,
                                              start=math.degrees(0.0),
                                              extent=math.degrees(math.pi),
                                              fill=fill_color,
                                              outline=border_color,
                                              width=width)
                arc2 = self.canvas.create_arc(upper_left.x,
                                              upper_left.y,
                                              lower_right.x,
                                              lower_right.y,
                                              style=PIESLICE,
                                              start=math.degrees(math.pi),
                                              extent=math.degrees(1.99 *
                                                                  math.pi),
                                              fill=fill_color,
                                              outline=border_color,
                                              width=width)
                arcs.append(arc1)
                arcs.append(arc2)
            else:
                arc = self.canvas.create_arc(upper_left.x,
                                             upper_left.y,
                                             lower_right.x,
                                             lower_right.y,
                                             style=PIESLICE,
                                             start=math.degrees(start_angle),
                                             extent=math.degrees(end_angle -
                                                                 start_angle),
                                             fill=fill_color,
                                             outline=border_color,
                                             width=width)
                arcs.append(arc)
        else:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                arc1 = self.canvas.create_arc(upper_left.x,
                                              upper_left.y,
                                              lower_right.x,
                                              lower_right.y,
                                              style=ARC,
                                              start=math.degrees(0.0),
                                              extent=math.degrees(math.pi),
                                              outline=border_color,
                                              width=width)
                arc2 = self.canvas.create_arc(upper_left.x,
                                              upper_left.y,
                                              lower_right.x,
                                              lower_right.y,
                                              style=ARC,
                                              start=math.degrees(math.pi),
                                              extent=math.degrees(1.99 *
                                                                  math.pi),
                                              outline=border_color,
                                              width=width)
                arcs.append(arc1)
                arcs.append(arc2)
            else:
                if start_angle > end_angle:
                    arc1 = self.canvas.create_arc(
                        upper_left.x,
                        upper_left.y,
                        lower_right.x,
                        lower_right.y,
                        style=ARC,
                        start=math.degrees(start_angle),
                        extent=math.degrees(2.0 * math.pi - start_angle),
                        outline=border_color,
                        width=width)
                    arc2 = self.canvas.create_arc(
                        upper_left.x,
                        upper_left.y,
                        lower_right.x,
                        lower_right.y,
                        style=ARC,
                        start=0.0,
                        extent=math.degrees(end_angle),
                        outline=border_color,
                        width=width)
                    arcs.append(arc1)
                    arcs.append(arc2)
                else:
                    arc = self.canvas.create_arc(
                        upper_left.x,
                        upper_left.y,
                        lower_right.x,
                        lower_right.y,
                        style=ARC,
                        start=math.degrees(start_angle),
                        extent=math.degrees(end_angle - start_angle),
                        outline=border_color,
                        width=width)
                    arcs.append(arc)

        return arcs

    def draw_path(self, points, is_closed, color, width):
        path_points = []
        for i in range(1, len(points)):
            path_point = self.draw_line_from_coordinate_to_coordinate(
                points[i - 1], points[i], color, width)
            path_points.append(path_point)

        if is_closed:
            path_point = self.draw_line_from_coordinate_to_coordinate(
                points[-1], points[0], color, width)
            path_points.append(path_point)

        return path_points

    def draw_line_from_coordinate_to_coordinate(self,
                                                coord1,
                                                coord2,
                                                color,
                                                width=1):
        return self.canvas.create_line(coord1.x,
                                       coord1.y,
                                       coord2.x,
                                       coord2.y,
                                       fill=color,
                                       width=width)

    def clear(self):
        self.canvas.delete("all")
