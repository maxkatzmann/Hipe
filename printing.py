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

import euclidean_coordinates
import native_coordinates
import math

colors = ["black", "red", "green", "blue", "orange", "magenta"];

class printer:
    def __init__(self, canvas, scale):
        self.canvas = canvas
        self.scale = scale

    ### SVG ###

    def print_ipe(self, points, edges, circle_sizes, circle_colors, selected_nodes, is_circle_node):

        print("<?xml version=\"1.0\"?>\n" +\
              "<!DOCTYPE ipe SYSTEM \"ipe.dtd\">\n" +\
              "<ipe version=\"70206\" creator=\"Ipe 7.2.7\">\n" +\
              "<info created=\"D:20170719160807\" modified=\"D:20170719160807\"/>\n" +\
              "<ipestyle name=\"basic\">\n" +\
              "</ipestyle>\n" +\
              "<page>\n" +\
              "<layer name=\"alpha\"/>\n" +\
              "<view layers=\"alpha\" active=\"alpha\"/>\n")

        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)

        self.print_ipe_circle(center, 2.0, True, "black")

        render_detail = 360
        render_detail_half = render_detail / 2

        for index, point in enumerate(points):
            if is_circle_node[index]:
                if index in selected_nodes:
                    self.print_ipe_circle(point, 2.0, True, "black")
                else:
                    self.print_ipe_circle(point, 2.0, True, "black")

                circle_size = circle_sizes[index]
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)

                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

                additional_render_detail = 8 * math.floor(native_point.r)
                angular_point_distance = 2.0 * math.pi / render_detail

                circle_points = []
                for i in range(render_detail):
                    native_circle_point = native_coordinates.polar_coordinate(circle_size, i * angular_point_distance)
                    circle_points.append(native_circle_point)

                    if abs(i - render_detail_half) < (additional_render_detail / 2):
                        for j in range(additional_render_detail):
                            native_circle_point = native_coordinates.polar_coordinate(circle_size, \
                            i * angular_point_distance + j * (angular_point_distance / additional_render_detail))
                            circle_points.append(native_circle_point)

                for i in range(len(circle_points)):
                    native_circle_point = circle_points[i]
                    translated_point = native_coordinates.coordinate_translated_along_x_axis_by_hyperbolic_distance(native_circle_point, native_point.r)
                    rotated_point = native_coordinates.coordinate_rotated_around_origin_by_angle(translated_point, native_point.phi)
                    converted_point = rotated_point.to_euclidean_coordinate_with_scale(self.scale)
                    euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)

                    circle_points[i] = euclidean_circle_point

                    if i > 0:
                        self.print_ipe_line(circle_points[i - 1], circle_points[i], colors[circle_colors[index]])

                self.print_ipe_line(circle_points[len(circle_points) - 1], circle_points[0], colors[circle_colors[index]])
            else:
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

                if index in selected_nodes:
                    self.print_ipe_circle(point, 2.0, True, "black")
                else:
                    self.print_ipe_circle(point, 2.0, True, "black")

        for edge in edges:
            (node1, node2) = edge
            self.print_ipe_edge(points[node1], points[node2], "black")

        print("</page>\n" +\
              "</ipe>")

    def print_ipe_line(self, coord1, coord2, color):
        print("<path stroke=\"" + str(color) + "\">\n" +\
              str(coord1.x) + " " + str(coord1.y) + " m\n" +\
              str(coord2.x) + " " + str(coord2.y) + " l\n" +\
              "</path>")

    def print_ipe_edge(self, coord1, coord2, color):
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
                self.print_ipe_line(converted_points[i - 1],
                                    converted_points[i],
                                    color)
        if len(converted_points) > 2:
            if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
                self.print_ipe_line(converted_points[render_detail - 1],
                                    coord2,
                                    color)
            else:
                self.print_ipe_line(converted_points[render_detail - 1],
                                    coord1,
                                    color)

    def print_ipe_circle(self, center, radius, filled, color):
        if filled:
            print("<path stroke=\"" + str(color) + "\" fill=\"" + str(color) + "\"> " + str(radius) + " 0 0 " + str(radius) + " " + str(center.x) + " " + str(center.y) + " e </path>")
        else:
            print("<path stroke=\"" + str(color) + "\"> " + str(radius) + " 0 0 " + str(radius) + " " + str(center.x) + " " + str(center.y) + " e </path>")

    ### SVG ###

    def print_svg(self, points, edges, circle_sizes, circle_colors, selected_nodes, is_circle_node):
        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE svg PUBLIC " +\
              "\"-//W3C//DTD SVG 1.1//EN\" " +\
              "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n\n<svg " +\
              "xmlns=\"http://www.w3.org/2000/svg\"\nxmlns:xlink=\"http://" +\
              "www.w3.org/1999/xlink\" " +\
              "xmlns:ev=\"http://www.w3.org/2001/xml-events\"\nversion=\"1.1\" " +\
              "baseProfile=\"full\"\nwidth=\"" + str(self.canvas.winfo_width()) + "\" height=\"" + str(self.canvas.winfo_height()) + "\">\n\n")

        center = euclidean_coordinates.euclidean_coordinate(\
            self.canvas.winfo_width() / 2.0, \
            self.canvas.winfo_height() / 2.0)

        self.print_svg_circle(center, 2.0, True, "blue")

        render_detail = 360
        render_detail_half = render_detail / 2

        for index, point in enumerate(points):
            if is_circle_node[index]:
                if index in selected_nodes:
                    self.print_svg_circle(point, 2.0, True, "red")
                else:
                    self.print_svg_circle(point, 2.0, True, "black")

                circle_size = circle_sizes[index]
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

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
                        self.print_svg_line(converted_points[i - 1],
                                            converted_points[i],
                                            colors[circle_colors[index]])

                self.print_svg_line(converted_points[len(circle_points) - 1],
                                    converted_points[0],
                                    colors[circle_colors[index]])
            else:
                relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
                native_point = relative_point.to_native_coordinate_with_scale(self.scale)

                if index in selected_nodes:
                    self.print_svg_circle(point, 2.0, True, "red")
                else:
                    self.print_svg_circle(point, 2.0, True, "black")

        for edge in edges:
            (node1, node2) = edge
            self.print_svg_edge(points[node1], points[node2], "black")

        print("\n</svg>\n")

    def print_svg_circle(self, center, radius, filled, color):
        if filled:
            print("<circle cx=\"" + str(center.x) + "\" cy=\"" + str(center.y) + "\" r=\"" + str(radius) + "\" fill=\"" + str(color) + "\" stroke=\"" + str(color) + "\" stroke-width=\"1\"/>\n")
        else:
            print("<circle cx=\"" + str(center.x) + "\" cy=\"" + str(center.y) + "\" r=\"" + str(radius) + "\" fill=\"clear\" stroke=\"" + str(color) + "\" stroke-width=\"1\"/>\n")

    def print_svg_line(self, coord1, coord2, color):
        print("<line x1=\"" + str(coord1.x) + "\" y1=\"" + str(coord1.y) + "\" x2=\"" + str(coord2.x) + "\" y2=\"" + str(coord2.y) + "\" stroke=\"" + str(color) + "\" stroke-width=\"1.0\" opacity=\"1.0\"/>\n")

    def print_svg_edge(self, coord1, coord2, color):
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
                self.print_svg_line(converted_points[i - 1],
                                    converted_points[i],
                                    color)

        if len(converted_points) > 2:
            if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
                self.print_svg_line(converted_points[render_detail - 1],
                                    coord2,
                                    color)
            else:
                self.print_svg_line(converted_points[render_detail - 1],
                                    coord1,
                                    color)
