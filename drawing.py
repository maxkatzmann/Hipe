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
import math

import drawing
import euclidean_coordinates
import embedded_graph
import native_coordinates


class point:
    def __init__(self, coordinate_H, color):
        self.coordinate_H = coordinate_H
        self.color = color
        self.drawn_items = None


class circle:
    def __init__(self, coordinate_H, radius, color):
        self.coordinate_H = coordinate_H
        self.radius = radius
        self.color = color
        self.circle_points_E = []
        self.drawn_items = None


class edge:
    def __init__(self, index1, index2):
        self.index1 = index1
        self.index2 = index2
        self.edge_points_E = []
        self.drawn_items = None

        self.hypercycle_radius = 0
        self.hypercycle_upper_points_E = None
        self.hypercycle_lower_points_E = None
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

        # The items and edges that are drawn.
        self.items = []
        self.edges = []

        self.canvas = canvas
        self.scale = scale

        # The embedded graph
        self.embedded_graph = None

        # The drawn items associated with the embedded graph.
        self.embedded_graph_items = None

        # The grid
        self.grid_radius = 0
        self.grid_items = None

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

        # The items representing the origin.
        self.drawn_origin_items = None

    def canvas_point_from_hyperbolic_coordinate(self, coordinate_H):

        center_E = euclidean_coordinates.euclidean_coordinate(
            self.canvas.winfo_width() / 2.0,
            self.canvas.winfo_height() / 2.0)

        coordinate_E = coordinate_H.to_euclidean_coordinate_with_scale(
            self.scale)

        coordinate_E.x = center_E.x - coordinate_E.x
        coordinate_E.y = center_E.y - coordinate_E.y

        return coordinate_E

    def hyperbolic_coordinate_from_canvas_point(self, coordinate_E):
        center_E = euclidean_coordinates.euclidean_coordinate(
            self.canvas.winfo_width() / 2.0,
            self.canvas.winfo_height() / 2.0)
        relative_E = euclidean_coordinates.coordinate_relative_to_coordinate(
            coordinate_E, center_E)
        coordinate_H = relative_E.to_native_coordinate_with_scale(self.scale)
        return coordinate_H

    def draw(self, items, edges, selected_nodes, mouse_location_E,
             snapped_item_radial, snapped_item_angular):
        self.draw_with_functions(items, edges, selected_nodes,
                                 mouse_location_E, self.draw_path,
                                 self.draw_circle)

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
        if mouse_location_E is not None:
            self.mouse_location_cirlce_items = self.draw_circle(
                mouse_location_E, self.selection_radius, 0.0, 2.0 * math.pi,
                False, "", self.secondary_selection_color, 1.0)

        # Drawing the snapping guides if there are any.
        if len(selected_nodes) > 0:
            center_E = euclidean_coordinates.euclidean_coordinate(
                self.canvas.winfo_width() / 2.0,
                self.canvas.winfo_height() / 2.0)
            selected_index = selected_nodes[-1]
            selected_coordinate_H = items[selected_index].coordinate_H
            selected_coordinate_E = self.canvas_point_from_hyperbolic_coordinate(
                selected_coordinate_H)
            radius = selected_coordinate_H.r * self.scale

            self.snap_items = []

            if snapped_item_radial is not None:
                snapped_coordinate_H = items[snapped_item_radial].coordinate_H

                # The radii of the two coordinate should match since we snapped to it.
                # We now draw the circle connecting the two
                circle_from_select_to_snapped = True

                signed_angular_distance = snapped_coordinate_H.phi - \
                    selected_coordinate_H.phi
                if signed_angular_distance > 0:
                    if signed_angular_distance < math.pi:
                        circle_from_select_to_snapped = False
                else:
                    if signed_angular_distance < -math.pi:
                        circle_from_select_to_snapped = False

                start_angle = selected_coordinate_H.phi
                end_angle = snapped_coordinate_H.phi

                if not circle_from_select_to_snapped:
                    start_angle = snapped_coordinate_H.phi
                    end_angle = selected_coordinate_H.phi

                drawing_start_angle = ((math.pi - start_angle) +
                                       (2.0 * math.pi)) % (2.0 * math.pi)
                drawing_end_angle = ((math.pi - end_angle) +
                                     (2.0 * math.pi)) % (2.0 * math.pi)

                radial_snap_items = self.draw_circle(
                    center_E, radius, drawing_start_angle, drawing_end_angle,
                    circle_from_select_to_snapped, "",
                    self.secondary_selection_color, 1.0)
                self.snap_items += radial_snap_items

            if snapped_item_angular is not None:
                selected_coordinate_E = self.canvas_point_from_hyperbolic_coordinate(
                    selected_coordinate_H)
                snapped_coordinate_H = items[snapped_item_angular].coordinate_H
                snapped_coordinate_E = self.canvas_point_from_hyperbolic_coordinate(
                    snapped_coordinate_H)
                angular_snap_items = self.draw_line_from_coordinate_to_coordinate(
                    selected_coordinate_E, snapped_coordinate_E,
                    self.secondary_selection_color, 1.0)
                self.snap_items.append(angular_snap_items)

    def draw_embedded_graph(self, center_E, path_func, circle_func):
        if not self.embedded_graph:
            return

        if self.embedded_graph_items:
            return

        self.embedded_graph_items = []

        items = []
        for node in self.embedded_graph.embedding:
            coordinate_H = self.embedded_graph.embedding[node]
            items.append(point(coordinate_H, 0))

        self.embedded_graph_items += self.draw_points(items, [], center_E,
                                                      circle_func)

        # Create the edges.
        edges = []
        for u, v in self.embedded_graph.graph.edges:
            edges.append(edge(u, v))

        self.embedded_graph_items += self.draw_edges(edges, items, center_E,
                                                     path_func)

    def draw_regular_grid(self, center_E, path_func, circle_func):
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
            coordinate_H = self.regular_grid.embedding[node]
            items.append(point(coordinate_H, 0))

        self.regular_grid_items += self.draw_points(items, [], center_E,
                                                    circle_func)

        # Create the edges.
        edges = []
        for u, v in self.regular_grid.graph.edges:
            edges.append(edge(u, v))

        self.regular_grid_items += self.draw_edges(edges, items, center_E,
                                                   path_func)

    def draw_grid(self, center_E, path_func, circle_func):
        # Drawing the grid
        if self.grid_radius <= 0:
            return

        # Don't redraw if we already drew it.
        if self.grid_items is not None:
            return

        grid_color = "gray"
        alpha = 0.75
        layer_width = math.log(2) / alpha
        number_of_layers = math.floor(self.grid_radius / layer_width)

        grid_items = []

        # Drawing the layers
        for layer in range(number_of_layers):
            outer_radius = self.grid_radius - layer * layer_width
            inner_radius = self.grid_radius - (layer + 1) * layer_width
            grid_items += circle_func(center_E, self.scale * outer_radius, 0.0,
                                      2.0 * math.pi, True, "", grid_color, 1.0)

            # Drawing the cell borders
            number_of_cells_in_layer = math.ceil(
                math.pow(2, number_of_layers - layer))
            angular_cell_width = 2.0 * math.pi / number_of_cells_in_layer
            for cell in range(number_of_cells_in_layer):
                inner_cell_point_H = native_coordinates.polar_coordinate(
                    inner_radius, cell * angular_cell_width)
                outer_cell_point_H = native_coordinates.polar_coordinate(
                    outer_radius, cell * angular_cell_width)

                inner_cell_point_E = self.canvas_point_from_hyperbolic_coordinate(
                    inner_cell_point_H)
                outer_cell_point_E = self.canvas_point_from_hyperbolic_coordinate(
                    outer_cell_point_H)

                grid_items += path_func(
                    [inner_cell_point_E, outer_cell_point_E], False,
                    grid_color, 1.0)

        # Drawing the inner radius of the inner most layer
        grid_items += circle_func(
            center_E,
            self.scale * (self.grid_radius - number_of_layers * layer_width),
            0.0, 2.0 * math.pi, True, "", grid_color, 1.0)

        self.grid_items = grid_items

    def draw_circles(self, items, selected_nodes, center_E, mouse_location_E,
                     path_func, circle_func):
        for index, item in enumerate(items):
            if not is_circle_item(item):
                continue

            # Don't draw an item if its already drawn.
            if item.drawn_items:
                continue

            # Check whether we should highlight the whole circle instead of only the point.
            should_highlight_primary_selection = False

            coordinate_E = self.canvas_point_from_hyperbolic_coordinate(
                item.coordinate_H)

            if index in selected_nodes:
                if selected_nodes[-1] == index:
                    item.drawn_items = circle_func(
                        coordinate_E, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.primary_selection_color,
                        self.primary_selection_color,
                        self.selection_border_size)
                    if mouse_location_E is not None:
                        should_highlight_primary_selection = True
                else:
                    item.drawn_items = circle_func(
                        coordinate_E, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.secondary_selection_color,
                        self.secondary_selection_color,
                        self.selection_border_size)
            else:
                item.drawn_items = circle_func(coordinate_E, self.point_size,
                                               0.0, 2.0 * math.pi, True,
                                               self.colors[item.color],
                                               self.colors[item.color],
                                               self.selection_border_size)

            converted_points_E = []

            if len(item.circle_points_E) > 0:
                converted_points_E = item.circle_points_E
            else:
                circle_size = item.radius
                circle_points_H = native_coordinates.render_points_for_circle_with_center_and_radius(
                    item.coordinate_H, circle_size)
                for i in range(len(circle_points_H)):
                    circle_point_H = circle_points_H[i]
                    circle_point_E = self.canvas_point_from_hyperbolic_coordinate(
                        circle_point_H)
                    converted_points_E.append(circle_point_E)
                item.circle_points_E = converted_points_E

            circle_color = self.colors[item.color]

            if should_highlight_primary_selection:
                circle_color = self.secondary_selection_color

            item.drawn_items += path_func(converted_points_E, True,
                                          circle_color, 2.0)

    def draw_points(self, items, selected_nodes, center_E, circle_func):
        drawn_point_items = []
        for index, item in enumerate(items):
            if is_circle_item(item):
                continue

            # Don't draw an item if already has drawn items.
            if item.drawn_items:
                continue

            coordinate_E = self.canvas_point_from_hyperbolic_coordinate(
                item.coordinate_H)

            if index in selected_nodes:
                if selected_nodes[len(selected_nodes) - 1] == index:
                    item.drawn_items = circle_func(
                        coordinate_E, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.primary_selection_color,
                        self.primary_selection_color,
                        self.selection_border_size)
                else:
                    item.drawn_items = circle_func(
                        coordinate_E, self.point_size, 0.0, 2.0 * math.pi,
                        True, self.secondary_selection_color,
                        self.secondary_selection_color,
                        self.selection_border_size)
            else:
                item.drawn_items = circle_func(coordinate_E, self.point_size,
                                               0.0, 2.0 * math.pi, True,
                                               self.colors[item.color],
                                               self.colors[item.color],
                                               self.selection_border_size)

            drawn_point_items += item.drawn_items

        return drawn_point_items

    def draw_edges(self, edges, items, center_E, path_func):
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

            point1_H = item1.coordinate_H
            point2_H = item2.coordinate_H

            converted_points_E = []
            if len(edge.edge_points_E) > 0:
                converted_points_E = edge.edge_points_E
            else:
                line_points = native_coordinates.render_points_for_line_from_to(
                    point1_H, point2_H)

                for i in range(len(line_points)):
                    line_point_H = line_points[i]
                    line_point_E = self.canvas_point_from_hyperbolic_coordinate(
                        line_point_H)
                    converted_points_E.append(line_point_E)

                edge.edge_points_E = converted_points_E

            edge.drawn_items = path_func(converted_points_E, False, color, 2.0)

            drawn_edge_items += edge.drawn_items

            # If the edge does not have a hypercycle, we continue with the next
            # edge. Otherwise, we draw the hypercycle.
            if edge.hypercycle_radius <= 0:
                continue

            # If the hypercycle of the edge is already drawn, we don't need to draw it again.
            if edge.drawn_hypercycle_items:
                continue

            hypercycle_upper_points_E = []
            hypercycle_lower_points_E = []

            if edge.hypercycle_upper_points_E is not None and edge.hypercycle_lower_points_E is not None:
                hypercycle_upper_points_E = edge.hypercycle_upper_points_E
                hypercycle_lower_points_E = edge.hypercycle_lower_points_E
            else:
                hypercycle_upper_points_H, hypercycle_lower_points_H = native_coordinates.render_points_for_hypercycle_around_points(
                    point1_H, point2_H, edge.hypercycle_radius)

                # The hypercycle_points are in native coordinates, now we
                # have to convert them to the canvas.
                for i in range(len(hypercycle_upper_points_H)):
                    upper_sample_H = hypercycle_upper_points_H[i]
                    lower_sample_H = hypercycle_lower_points_H[i]

                    upper_sample_E = self.canvas_point_from_hyperbolic_coordinate(
                        upper_sample_H)
                    lower_sample_E = self.canvas_point_from_hyperbolic_coordinate(
                        lower_sample_H)

                    hypercycle_upper_points_E.append(upper_sample_E)
                    hypercycle_lower_points_E.append(lower_sample_E)

                edge.hypercycle_upper_points_E = hypercycle_upper_points_E
                edge.hypercycle_lower_points_E = hypercycle_lower_points_E

            drawn_upper_items = path_func(hypercycle_upper_points_E, False,
                                          color, 2.0)
            drawn_lower_items = path_func(hypercycle_lower_points_E, False,
                                          color, 2.0)
            edge.drawn_hypercycle_items = drawn_upper_items + drawn_lower_items

            drawn_edge_items += edge.drawn_hypercycle_items

        return drawn_edge_items

    def draw_with_functions(self, items, edges, selected_nodes,
                            mouse_location_E, path_func, circle_func):
        center_E = euclidean_coordinates.euclidean_coordinate(
            self.canvas.winfo_width() / 2.0,
            self.canvas.winfo_height() / 2.0)

        # Drawing the origin
        if self.drawn_origin_items is None:
            self.drawn_origin_items = circle_func(center_E, self.point_size,
                                                  0.0, 2.0 * math.pi, True,
                                                  "blue", "blue", 1.0)

        # Draw the regular grid
        self.draw_regular_grid(center_E, path_func, circle_func)

        # Draw the embedded graph
        self.draw_embedded_graph(center_E, path_func, circle_func)

        # Draw the grid
        self.draw_grid(center_E, path_func, circle_func)

        # Drawing the circles
        self.draw_circles(items, selected_nodes, center_E, mouse_location_E,
                          path_func, circle_func)

        # Drawing the points.
        self.draw_points(items, selected_nodes, center_E, circle_func)

        # Drawing the edges.
        self.draw_edges(edges, items, center_E, path_func)

    # Takes a center coordinate (Euclidean) and a radius and draws a circle
    # with the passed radius around the passed center.
    def draw_circle(self, center_E, radius, start_angle, end_angle,
                    is_clockwise, fill_color, border_color, width):

        upper_left = euclidean_coordinates.euclidean_coordinate(
            center_E.x - radius, center_E.y - radius)
        lower_right = euclidean_coordinates.euclidean_coordinate(
            center_E.x + radius, center_E.y + radius)

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

    # Takes a set of points (Euclidean) and draws lines from point i to i+1.
    def draw_path(self, points_E, is_closed, color, width):
        path_points_E = []
        for i in range(1, len(points_E)):
            path_point_E = self.draw_line_from_coordinate_to_coordinate(
                points_E[i - 1], points_E[i], color, width)
            path_points_E.append(path_point_E)

        if is_closed:
            path_point_E = self.draw_line_from_coordinate_to_coordinate(
                points_E[-1], points_E[0], color, width)
            path_points_E.append(path_point_E)

        return path_points_E

    # Draws a line from coord1 to coord2 (Both Euclidean).
    def draw_line_from_coordinate_to_coordinate(self,
                                                coord1_E,
                                                coord2_E,
                                                color,
                                                width=1):
        return self.canvas.create_line(coord1_E.x,
                                       coord1_E.y,
                                       coord2_E.x,
                                       coord2_E.y,
                                       fill=color,
                                       width=width)

    def clear(self):
        self.canvas.delete("all")

    def mark_item_for_redraw(self, item):
        if not item.drawn_items:
            return

        # If the item is a circle, its circle points need to move now.
        if drawing.is_circle_item(item):
            self.mark_circle_for_redraw(item)
        else:
            self.mark_point_for_redraw(item)

    def mark_edge_for_redraw(self, edge):
        edge.edge_points_E = []

        if edge.drawn_items:
            for drawn_item in edge.drawn_items:
                self.canvas.delete(drawn_item)
            edge.drawn_items = None

        if edge.drawn_hypercycle_items:
            for drawn_item in edge.drawn_hypercycle_items:
                self.canvas.delete(drawn_item)
                edge.drawn_hypercycle_items = None
        edge.hypercycle_upper_points_E = None
        edge.hypercycle_lower_points_E = None

    def mark_point_for_redraw(self, point):
        for drawn_item in point.drawn_items:
            self.canvas.delete(drawn_item)
        point.drawn_items = None

    def mark_circle_for_redraw(self, circle):
        for drawn_item in circle.drawn_items:
            self.canvas.delete(drawn_item)
        circle.drawn_items = None
        circle.circle_points_E = []

    def mark_all_items_for_redraw(self):
        for item in self.items:
            self.mark_item_for_redraw(item)

        for edge in self.edges:
            self.mark_edge_for_redraw(edge)

        self.mark_origin_for_redraw()

        self.mark_grid_for_redraw()
        self.mark_regular_grid_for_redraw()
        self.mark_embedded_graph_for_redraw()

    def mark_origin_for_redraw(self):
        if not self.drawn_origin_items:
            return

        for drawn_item in self.drawn_origin_items:
            self.canvas.delete(drawn_item)

        self.drawn_origin_items = None

    def mark_regular_grid_for_redraw(self):
        if not self.regular_grid_items:
            return

        for drawn_item in self.regular_grid_items:
            self.canvas.delete(drawn_item)

        self.regular_grid_items = None

    def mark_grid_for_redraw(self):
        if not self.grid_items:
            return

        for drawn_item in self.grid_items:
            self.canvas.delete(drawn_item)

        self.grid_items = None

    def mark_embedded_graph_for_redraw(self):
        if not self.embedded_graph_items:
            return

        for drawn_item in self.embedded_graph_items:
            self.canvas.delete(drawn_item)

        self.embedded_graph_items = None
