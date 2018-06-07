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

class drawer:

    colors = ["black", "red", "green", "blue", "orange", "magenta"];

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

    def draw(self, points, edges, circle_sizes, circle_colors, selected_nodes, is_circle_node):
        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)

        self.draw_circle(center, 2.0, 0.0, 2.0 * math.pi, True, "blue")

        for index, point in enumerate(points):
            if is_circle_node[index]:
                if index in selected_nodes:
                    self.draw_circle(point, 2.0, 0.0, 2.0 * math.pi, True, "red")
                else:
                    self.draw_circle(point, 2.0, 0.0, 2.0 * math.pi, True, "black")

                circle_size = circle_sizes[index]
                native_point = self.hyperbolic_coordinate_from_canvas_point(point)

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
                        self.draw_line_from_coordinate_to_coordinate(converted_points[i - 1],
                                                                     converted_points[i],
                                                                     self.colors[circle_colors[index]])

                self.draw_line_from_coordinate_to_coordinate(converted_points[len(circle_points) - 1],
                                                             converted_points[0],
                                                             self.colors[circle_colors[index]])
            else:
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

                if index in selected_nodes:
                    self.draw_circle(point, 2.0, 0.0, 2.0 * math.pi, True, "red")
                else:
                    self.draw_circle(point, 2.0, 0.0, 2.0 * math.pi, True, "black")

        for edge in edges:
            (node1, node2) = edge
            self.draw_edge_from_coordinate_to_coordinate(points[node1],
                                                         points[node2],
                                                         "black")

    def draw_circle(self, center, radius, start_angle, end_angle, is_clockwise, fill_color):
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
                                       outline = fill_color)
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = PIESLICE, \
                                       start = math.degrees(math.pi), \
                                       extent = math.degrees(1.99 * math.pi), \
                                       fill = fill_color, \
                                       outline = fill_color)
            else:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = PIESLICE, \
                                       start = math.degrees(start_angle), \
                                       extent = math.degrees(end_angle - start_angle), \
                                       fill = fill_color, \
                                       outline = fill_color)
        else:
            if start_angle == 0.0 and end_angle == 2.0 * math.pi:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = ARC, \
                                       start = math.degrees(0.0), \
                                       extent = math.degrees(math.pi))
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = ARC, \
                                       start = math.degrees(math.pi), \
                                       extent = math.degrees(1.99 * math.pi))
            else:
                self.canvas.create_arc(upper_left.x, \
                                       upper_left.y, \
                                       lower_right.x, \
                                       lower_right.y, \
                                       style = ARC, \
                                       start = math.degrees(start_angle), \
                                       extent = math.degrees(end_angle - start_angle))

    def draw_edge_from_coordinate_to_coordinate(self, coord1, coord2, color):
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
                self.draw_line_from_coordinate_to_coordinate(converted_points[i - 1],
                                                             converted_points[i],
                                                             color)
        if len(converted_points) > 2:
            if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
                self.draw_line_from_coordinate_to_coordinate(converted_points[render_detail - 1],
                                                             coord2,
                                                             color)
            else:
                self.draw_line_from_coordinate_to_coordinate(converted_points[render_detail - 1],
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
