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
import native_coordinates
import math
import collections

class point:
    def __init__(self, coordinate, color):
        self.coordinate = coordinate
        self.color = color

class circle:
    def __init__(self, coordinate, radius, color):
        self.coordinate = coordinate
        self.radius = radius
        self.color = color
        self.circle_points = []

class edge:
    def __init__(self, index1, index2):
        self.index1 = index1
        self.index2 = index2
        self.edge_points = []
        self.hypercycle_radius = 0
        self.hypercycle_points = None

    def __str__(self):
        return "("  + str(self.index1) + ", " + str(self.index2) + ")"

def is_circle_item(item):
    return isinstance(item, circle)

class drawer:

    colors = ["black", "green", "blue", "purple", "deep pink", "red4", "orange", "gold"];
    selection_border_size = 1
    selection_radius = 30
    primary_selection_color = "red"
    secondary_selection_color = "magenta"
    point_size = 3

    def __init__(self, canvas, scale):
        self.canvas = canvas
        self.scale = scale
        self.grid_radius = 0

    def hyperbolic_coordinate_from_canvas_point(self, point):
        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)
        relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
        native_point = relative_point.to_native_coordinate_with_scale(self.scale)
        return native_point

    def draw(self, items, edges, selected_nodes, mouse_location):
        self.draw_with_functions(items,
                                 edges,
                                 selected_nodes,
                                 mouse_location,
                                 self.draw_path,
                                 self.draw_circle)
        if mouse_location is not None:
            self.draw_circle(mouse_location, self.selection_radius, 0.0, 2.0 * math.pi, False, "", "magenta", 1.0)

    def draw_with_functions(self, items, edges, selected_nodes, mouse_location, path_func, circle_func):
        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)

        # Drawing the origin
        circle_func(center, self.point_size, 0.0, 2.0 * math.pi, True, "blue", "blue", 1.0)

        # Drawing the grid
        if self.grid_radius > 0:
            grid_color = "gray"
            alpha = 0.75
            layer_width = math.log(2) / alpha
            number_of_layers = math.floor(self.grid_radius / layer_width)

            # Drawing the layers
            for layer in range(number_of_layers):
                outer_radius = self.grid_radius - layer * layer_width
                inner_radius = self.grid_radius - (layer + 1) * layer_width
                circle_func(center, self.scale * outer_radius, 0.0, 2.0 * math.pi, True, "", grid_color, 1.0)

                # Drawing the cell borders
                number_of_cells_in_layer = math.ceil(math.pow(2, number_of_layers - layer))
                angular_cell_width = 2.0 * math.pi / number_of_cells_in_layer
                for cell in range(number_of_cells_in_layer):
                    inner_cell_point = native_coordinates.polar_coordinate(inner_radius, cell * angular_cell_width)
                    outer_cell_point = native_coordinates.polar_coordinate(outer_radius, cell * angular_cell_width)

                    converted_inner_point = inner_cell_point.to_euclidean_coordinate_with_scale(self.scale)
                    converted_outer_point = outer_cell_point.to_euclidean_coordinate_with_scale(self.scale)

                    euclidean_inner_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_inner_point)
                    euclidean_outer_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_outer_point)

                    path_func([euclidean_inner_point, euclidean_outer_point],
                              False,
                              grid_color,
                              1.0)

            # Drawing the inner radius of the inner most layer
            circle_func(center, self.scale * (self.grid_radius - number_of_layers * layer_width), 0.0, 2.0 * math.pi, True, "", grid_color, 1.0)

        # Drawing the circles
        for index, item in enumerate(items):
            if is_circle_item(item):

                # Check whether we should highlight the whole circle instead of only the point.
                should_highlight_primary_selection = False

                if index in selected_nodes:
                    if selected_nodes[-1] == index:
                        circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.primary_selection_color, self.primary_selection_color, self.selection_border_size)
                        if mouse_location is not None:
                            should_highlight_primary_selection = True
                    else:
                        circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.secondary_selection_color, self.secondary_selection_color, self.selection_border_size)
                else:
                    circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.colors[item.color], self.colors[item.color], self.selection_border_size)

                converted_points = []

                if len(item.circle_points) > 0:
                    converted_points = item.circle_points
                else:
                    circle_size = item.radius
                    native_point = self.hyperbolic_coordinate_from_canvas_point(item.coordinate)

                    circle_points = native_coordinates.render_points_for_circle_with_center_and_radius(native_point,
                                                                                                   circle_size,
                                                                                                   self.scale)
                    for i in range(len(circle_points)):
                        circle_point = circle_points[i]
                        converted_point = circle_point.to_euclidean_coordinate_with_scale(self.scale)
                        euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
                        converted_points.append(euclidean_circle_point)
                    item.circle_points = converted_points

                circle_color = self.colors[item.color]

                if should_highlight_primary_selection:
                    circle_color = self.secondary_selection_color

                path_func(converted_points, True, circle_color, 2.0)
            else:
                # Drawing the points.
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(item.coordinate, center)
                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

                if index in selected_nodes:
                    if selected_nodes[len(selected_nodes) - 1] == index:
                        circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.primary_selection_color, self.primary_selection_color, self.selection_border_size)
                    else:
                        circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.secondary_selection_color, self.secondary_selection_color, self.selection_border_size)
                else:
                    circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.colors[item.color], self.colors[item.color], self.selection_border_size)

        # Drawing the edges
        for edge in edges:
            color = "black"
            item1 = items[edge.index1]
            item2 = items[edge.index2]
            if item1.color == item2.color:
                color = self.colors[item1.color]

            relative_point1 = euclidean_coordinates.coordinate_relative_to_coordinate(item1.coordinate, center)
            native_point1 = relative_point1.to_native_coordinate_with_scale(self.scale)
            relative_point2 = euclidean_coordinates.coordinate_relative_to_coordinate(item2.coordinate, center)
            native_point2 = relative_point2.to_native_coordinate_with_scale(self.scale)

            angular_distance = native_point2.phi - native_point1.phi

            converted_points = []
            if len(edge.edge_points) > 0:
                converted_points = edge.edge_points
            else:
                render_detail = 100

                line_points = native_coordinates.render_points_for_line_from_to(native_point1, native_point2)

                for i in range(len(line_points)):
                    converted_point = line_points[i].to_euclidean_coordinate_with_scale(self.scale)
                    euclidean_line_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
                    converted_points.append(euclidean_line_point)

                edge.edge_points = converted_points

            if len(converted_points) > 2:
                if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
                    converted_points.append(item2.coordinate)
                else:
                    converted_points.append(item1.coordinate)

            path_func(converted_points, False, color, 2.0)

            # Drawing the hypercycle if there is one
            if edge.hypercycle_radius > 0:

                hypercycle_upper_points = []
                hypercycle_lower_points = []

                if not edge.hypercycle_points is None:
                    hypercycle_upper_points = edge.hypercycle_points.upper_samples
                    hypercycle_lower_points = edge.hypercycle_points.lower_samples
                else:
                    hypercycle_points = native_coordinates.render_points_for_hypercycle_around_points(native_point1,
                                                                                                      native_point2,
                                                                                                      edge.hypercycle_radius)

                    # The hypercycle_points are in native coordinates, now we
                    # have to convert them to the canvas.
                    for i in range(len(hypercycle_points.upper_samples)):
                        upper_sample = hypercycle_points.upper_samples[i]
                        lower_sample = hypercycle_points.lower_samples[i]

                        converted_upper_point = upper_sample.to_euclidean_coordinate_with_scale(self.scale)
                        euclidean_upper_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_upper_point)

                        converted_lower_point = lower_sample.to_euclidean_coordinate_with_scale(self.scale)
                        euclidean_lower_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_lower_point)

                        hypercycle_upper_points.append(euclidean_upper_point)
                        hypercycle_lower_points.append(euclidean_lower_point)

                    edge.hypercycle_points = native_coordinates.hypercycle_points(upper_samples = hypercycle_upper_points,
                                                                                  lower_samples = hypercycle_lower_points)

                path_func(hypercycle_upper_points, False, color, 2.0)
                path_func(hypercycle_lower_points, False, color, 2.0)

    def draw_circle(self, center, radius, start_angle, end_angle, is_clockwise, fill_color, border_color, width):

        upper_left = euclidean_coordinates.euclidean_coordinate(center.x - radius, center.y - radius)
        lower_right = euclidean_coordinates.euclidean_coordinate(center.x + radius, center.y + radius)

        if len(fill_color) > 0:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                self.canvas.create_arc(upper_left.x,
                                       upper_left.y,
                                       lower_right.x,
                                       lower_right.y,
                                       style = PIESLICE,
                                       start = math.degrees(0.0),
                                       extent = math.degrees(math.pi),
                                       fill = fill_color,
                                       outline = border_color,
                                       width = width)
                self.canvas.create_arc(upper_left.x,
                                       upper_left.y,
                                       lower_right.x,
                                       lower_right.y,
                                       style = PIESLICE,
                                       start = math.degrees(math.pi),
                                       extent = math.degrees(1.99 * math.pi),
                                       fill = fill_color,
                                       outline = border_color,
                                       width = width)
            else:
                self.canvas.create_arc(upper_left.x,
                                       upper_left.y,
                                       lower_right.x,
                                       lower_right.y,
                                       style = PIESLICE,
                                       start = math.degrees(start_angle),
                                       extent = math.degrees(end_angle - start_angle),
                                       fill = fill_color,
                                       outline = border_color,
                                       width = width)
        else:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                self.canvas.create_arc(upper_left.x,
                                       upper_left.y,
                                       lower_right.x,
                                       lower_right.y,
                                       style = ARC,
                                       start = math.degrees(0.0),
                                       extent = math.degrees(math.pi),
                                       outline = border_color,
                                       width = width)
                self.canvas.create_arc(upper_left.x,
                                       upper_left.y,
                                       lower_right.x,
                                       lower_right.y,
                                       style = ARC,
                                       start = math.degrees(math.pi),
                                       extent = math.degrees(1.99 * math.pi),
                                       outline = border_color,
                                       width = width)
            else:
                self.canvas.create_arc(upper_left.x,
                                       upper_left.y,
                                       lower_right.x,
                                       lower_right.y,
                                       style = ARC,
                                       start = math.degrees(start_angle),
                                       extent = math.degrees(end_angle - start_angle),
                                       width = width)

    def draw_path(self, points, is_closed, color, width):
        for i in range(1, len(points)):
            self.draw_line_from_coordinate_to_coordinate(points[i - 1],
                                                         points[i],
                                                         color,
                                                         width)

        if is_closed:
            self.draw_line_from_coordinate_to_coordinate(points[-1],
                                                         points[0],
                                                         color,
                                                         width)


    def draw_line_from_coordinate_to_coordinate(self, coord1, coord2, color, width = 1):
        self.canvas.create_line(coord1.x,
                                coord1.y,
                                coord2.x,
                                coord2.y,
                                fill = color,
                                width = width)

    def clear(self):
        self.canvas.delete("all")
