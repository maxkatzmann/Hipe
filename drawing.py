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

def is_circle_item(item):
    return isinstance(item, circle)

class drawer:

    colors = ["black", "red", "green", "blue", "orange", "magenta"];
    selection_border_size = 1
    point_size = 3

    def __init__(self, canvas, scale):
        self.canvas = canvas
        self.scale = scale

    def hyperbolic_coordinate_from_canvas_point(self, point):
        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)
        relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
        native_point = relative_point.to_native_coordinate_with_scale(self.scale)
        return native_point

    def draw(self, items, edges, selected_nodes):
        self.draw_with_functions(items,
                                 edges,
                                 selected_nodes,
                                 self.draw_line_from_coordinate_to_coordinate,
                                 self.draw_circle)

    def draw_with_functions(self, items, edges, selected_nodes, line_func, circle_func):
        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)

        circle_func(center, self.point_size, 0.0, 2.0 * math.pi, True, "blue", "blue", 1.0)

        for index, item in enumerate(items):
            if is_circle_item(item):
                if index in selected_nodes:
                    circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.colors[item.color], "red", self.selection_border_size)
                else:
                    circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.colors[item.color], self.colors[item.color], self.selection_border_size)

                circle_size = item.radius
                native_point = self.hyperbolic_coordinate_from_canvas_point(item.coordinate)

                circle_points = native_coordinates.render_points_for_circle_with_center_and_radius(native_point,
                                                                                                   circle_size,
                                                                                                   self.scale)
                converted_points = []
                for i in range(len(circle_points)):
                    circle_point = circle_points[i]
                    converted_point = circle_point.to_euclidean_coordinate_with_scale(self.scale)
                    euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
                    converted_points.append(euclidean_circle_point)
                    if i > 0:
                        line_func(converted_points[i - 1],
                                  converted_points[i],
                                  self.colors[item.color])

                line_func(converted_points[len(circle_points) - 1],
                          converted_points[0],
                          self.colors[item.color])
            else:
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(item.coordinate, center)
                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

                if index in selected_nodes:
                    circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.colors[item.color], "red", self.selection_border_size)
                else:
                    circle_func(item.coordinate, self.point_size, 0.0, 2.0 * math.pi, True, self.colors[item.color], self.colors[item.color], self.selection_border_size)

        for edge in edges:
            (node1, node2) = edge
            color = "black"
            item1 = items[node1]
            item2 = items[node2]
            if item1.color == item2.color:
                color = self.colors[item1.color]
            self.draw_edge_from_coordinate_to_coordinate(item1.coordinate,
                                                         item2.coordinate,
                                                         color,
                                                         line_func)

    def draw_circle(self, center, radius, start_angle, end_angle, is_clockwise, fill_color, border_color, width):

        upper_left = euclidean_coordinates.euclidean_coordinate(center.x - radius, center.y - radius)
        lower_right = euclidean_coordinates.euclidean_coordinate(center.x + radius, center.y + radius)

        if len(fill_color) > 0:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = PIESLICE, \
                                       start = math.degrees(0.0), \
                                       extent = math.degrees(math.pi), \
                                       fill = fill_color, \
                                       outline = border_color, \
                                       width = width)
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = PIESLICE, \
                                       start = math.degrees(math.pi), \
                                       extent = math.degrees(1.99 * math.pi), \
                                       fill = fill_color, \
                                       outline = border_color, \
                                       width = width)
            else:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = PIESLICE, \
                                       start = math.degrees(start_angle), \
                                       extent = math.degrees(end_angle - start_angle), \
                                       fill = fill_color, \
                                       outline = border_color, \
                                       width = width)
        else:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = ARC, \
                                       start = math.degrees(0.0), \
                                       extent = math.degrees(math.pi), \
                                       outline = border_color, \
                                       width = width)
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = ARC, \
                                       start = math.degrees(math.pi), \
                                       extent = math.degrees(1.99 * math.pi), \
                                       outline = border_color, \
                                       width = width)
            else:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = ARC, \
                                       start = math.degrees(start_angle), \
                                       extent = math.degrees(end_angle - start_angle),
                                       width = width)

    def draw_edge_from_coordinate_to_coordinate(self, coord1, coord2, color, line_func):
        render_detail = 100
        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)

        relative_point1 = euclidean_coordinates.coordinate_relative_to_coordinate(coord1, center)
        native_point1 = relative_point1.to_native_coordinate_with_scale(self.scale)

        relative_point2 = euclidean_coordinates.coordinate_relative_to_coordinate(coord2, center)
        native_point2 = relative_point2.to_native_coordinate_with_scale(self.scale)

        angular_distance = native_point2.phi - native_point1.phi

        line_points = native_coordinates.render_points_for_line_from_to(native_point1, native_point2)
        converted_points = []

        for i in range(len(line_points)):
            converted_point = line_points[i].to_euclidean_coordinate_with_scale(self.scale)
            euclidean_line_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
            converted_points.append(euclidean_line_point)

            if i > 0:
                line_func(converted_points[i - 1],
                          converted_points[i],
                          color)
        if len(converted_points) > 2:
            if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
                line_func(converted_points[render_detail - 1],
                          coord2,
                          color)
            else:
                line_func(converted_points[render_detail - 1],
                          coord1,
                          color)

    def draw_line_from_coordinate_to_coordinate(self, coord1, coord2, color):
        self.canvas.create_line(coord1.x, \
                                coord1.y, \
                                coord2.x, \
                                coord2.y, \
                                fill = color)

    def clear(self):
        self.canvas.delete("all")
