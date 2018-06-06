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
# Reference: https://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
import math
import sys
import native_coordinates
import euclidean_coordinates
from subprocess import call

# Creating the widget
root = Tk()
root.title("HyperVis")

# Creating the canvas
canvas = Canvas(root, width = 800, height = 600)
canvas.pack(fill=BOTH, expand=YES)

def draw_circle(canvas, center, radius, start_angle, end_angle, is_clockwise, fill_color):
    upper_left = euclidean_coordinates.EuclideanCoordinate(center.x - radius, center.y - radius)
    lower_right = euclidean_coordinates.EuclideanCoordinate(center.x + radius, center.y + radius)

    if len(fill_color) > 0:
        if start_angle == 0.0 and end_angle == 2.0 * math.pi:
            canvas.create_arc(upper_left.x, \
                upper_left.y, \
                lower_right.x, \
                lower_right.y, \
                style = PIESLICE, \
                start = math.degrees(0.0), \
                extent = math.degrees(math.pi), \
                fill = fill_color, \
                outline = fill_color)
            canvas.create_arc(upper_left.x, \
                upper_left.y, \
                lower_right.x, \
                lower_right.y, \
                style = PIESLICE, \
                start = math.degrees(math.pi), \
                extent = math.degrees(1.99 * math.pi), \
                fill = fill_color, \
                outline = fill_color)
        else:
            canvas.create_arc(upper_left.x, \
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
            canvas.create_arc(upper_left.x, \
                upper_left.y, \
                lower_right.x, \
                lower_right.y, \
                style = ARC, \
                start = math.degrees(0.0), \
                extent = math.degrees(math.pi))
            canvas.create_arc(upper_left.x, \
                upper_left.y, \
                lower_right.x, \
                lower_right.y, \
                style = ARC, \
                start = math.degrees(math.pi), \
                extent = math.degrees(1.99 * math.pi))
        else:
            canvas.create_arc(upper_left.x, \
                upper_left.y, \
                lower_right.x, \
                lower_right.y, \
                style = ARC, \
                start = math.degrees(start_angle), \
                extent = math.degrees(end_angle - start_angle))

def draw_edge_from_coordinate_to_coordinate(canvas, coord1, coord2, color):
    global scale
    render_detail = 100
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    if (coord1.x == center.x and coord1.y == center.y) or (coord2.x == center.x and coord2.y == center.y):
        draw_line_from_coordinate_to_coordinate(canvas, coord1, coord2, color)
    else:
        relative_point1 = euclidean_coordinates.coordinate_relative_to_coordinate(coord1, center)
        native_point1 = relative_point1.to_native_coordinate_with_scale(scale)

        relative_point2 = euclidean_coordinates.coordinate_relative_to_coordinate(coord2, center)
        native_point2 = relative_point2.to_native_coordinate_with_scale(scale)

        angular_distance = native_point2.phi - native_point1.phi
        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            native_temp = native_point1
            native_point1 = native_point2
            native_point2 = native_temp

        distance = native_coordinates.distance_between(native_point1, native_point2)

        cos_gamma_2 = 0.0
        try:
            cos_gamma_2 = (((math.cosh(native_point2.r) * math.cosh(distance)) - math.cosh(native_point1.r)) / (math.sinh(native_point2.r) * math.sinh(distance)))
        except (ZeroDivisionError, ValueError):
            pass

        line_points = []
        for i in range(0, render_detail):
            partial_distance = distance * (i / float(render_detail))
            r = 0.0
            try:
                r = math.acosh((math.cosh(native_point2.r) * math.cosh(partial_distance) - (math.sinh(native_point2.r) * math.sinh(partial_distance) * cos_gamma_2)))
            except (ZeroDivisionError, ValueError):
                pass
            gamma_prime = 0.0
            try:
                gamma_prime = math.acos(((math.cosh(r) * math.cosh(native_point2.r)) - math.cosh(partial_distance)) / (math.sinh(r) * math.sinh(native_point2.r)))
            except (ZeroDivisionError, ValueError):
                pass

            phi = native_point2.phi + gamma_prime
            native_line_point = native_coordinates.PolarCoordinate(r, phi)

            converted_point = native_line_point.to_euclidean_coordinate_with_scale(scale)
            euclidean_line_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
            line_points.append(euclidean_line_point)

            if i > 0:
                draw_line_from_coordinate_to_coordinate(canvas, line_points[i - 1], line_points[i], color)

        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            draw_line_from_coordinate_to_coordinate(canvas, line_points[render_detail - 1], coord2, color)
        else:
            draw_line_from_coordinate_to_coordinate(canvas, line_points[render_detail - 1], coord1, color)


def draw_line_from_coordinate_to_coordinate(canvas, coord1, coord2, color):
    canvas.create_line(coord1.x, \
        coord1.y, \
        coord2.x, \
        coord2.y, \
        fill = color)

def resize(event):
    canvas.delete("all")
    redraw(canvas)

### Main ###

points = []
edges = []
circle_sizes = []
circle_colors = []
selected_nodes = []
is_circle_node = []
current_circle_size = 10.0
colors = ["black", "red", "green", "blue", "orange", "magenta"];

scale = 35.0

def print_circle(center, radius, filled, color):
    if filled:
        print("<circle cx=\"" + str(center.x) + "\" cy=\"" + str(center.y) + "\" r=\"" + str(radius) + "\" fill=\"" + str(color) + "\" stroke=\"" + str(color) + "\" stroke-width=\"1\"/>\n")
    else:
        print("<circle cx=\"" + str(center.x) + "\" cy=\"" + str(center.y) + "\" r=\"" + str(radius) + "\" fill=\"clear\" stroke=\"" + str(color) + "\" stroke-width=\"1\"/>\n")

def print_ipe_circle(center, radius, filled, color):
    if filled:
        print("<path stroke=\"" + str(color) + "\" fill=\"" + str(color) + "\"> " + str(radius) + " 0 0 " + str(radius) + " " + str(center.x) + " " + str(center.y) + " e </path>")
    else:
        print("<path stroke=\"" + str(color) + "\"> " + str(radius) + " 0 0 " + str(radius) + " " + str(center.x) + " " + str(center.y) + " e </path>")

def print_line(coord1, coord2, color):
    print("<line x1=\"" + str(coord1.x) + "\" y1=\"" + str(coord1.y) + "\" x2=\"" + str(coord2.x) + "\" y2=\"" + str(coord2.y) + "\" stroke=\"" + str(color) + "\" stroke-width=\"1.0\" opacity=\"1.0\"/>\n")

def print_ipe_line(coord1, coord2, color):
    print("<path stroke=\"" + str(color) + "\">\n" +\
          str(coord1.x) + " " + str(coord1.y) + " m\n" +\
          str(coord2.x) + " " + str(coord2.y) + " l\n" +\
          "</path>")

def print_edge(coord1, coord2, color):
    global scale
    render_detail = 100
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    if (coord1.x == center.x and coord1.y == center.y) or (coord2.x == center.x and coord2.y == center.y):
        print_line(coord1, coord2, color)
    else:
        relative_point1 = euclidean_coordinates.coordinate_relative_to_coordinate(coord1, center)
        native_point1 = relative_point1.to_native_coordinate_with_scale(scale)

        relative_point2 = euclidean_coordinates.coordinate_relative_to_coordinate(coord2, center)
        native_point2 = relative_point2.to_native_coordinate_with_scale(scale)

        angular_distance = native_point2.phi - native_point1.phi
        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            native_temp = native_point1
            native_point1 = native_point2
            native_point2 = native_temp

        distance = native_coordinates.distance_between(native_point1, native_point2)

        cos_gamma_2 = 0.0
        try: 
            cos_gamma_2 = (((math.cosh(native_point2.r) * math.cosh(distance)) - math.cosh(native_point1.r)) / (math.sinh(native_point2.r) * math.sinh(distance)))
        except (ZeroDivisionError, ValueError):
            pass

        line_points = []
        for i in range(0, render_detail):
            partial_distance = distance * (i / float(render_detail))
            r = 0.0
            try:
                r = math.acosh((math.cosh(native_point2.r) * math.cosh(partial_distance) - (math.sinh(native_point2.r) * math.sinh(partial_distance) * cos_gamma_2)))
            except (ZeroDivisionError, ValueError):
                pass
            gamma_prime = 0.0
            try:
                gamma_prime = math.acos(((math.cosh(r) * math.cosh(native_point2.r)) - math.cosh(partial_distance)) / (math.sinh(r) * math.sinh(native_point2.r)))
            except (ZeroDivisionError, ValueError):
                pass

            phi = native_point2.phi + gamma_prime
            native_line_point = native_coordinates.PolarCoordinate(r, phi)

            converted_point = native_line_point.to_euclidean_coordinate_with_scale(scale)
            euclidean_line_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
            line_points.append(euclidean_line_point)

            if i > 0:
                print_line(line_points[i - 1], line_points[i], color)

        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            print_line(line_points[render_detail - 1], coord2, color)
        else:
            print_line(line_points[render_detail - 1], coord1, color)

def print_ipe_edge(coord1, coord2, color):
    global scale
    render_detail = 100
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    if (coord1.x == center.x and coord1.y == center.y) or (coord2.x == center.x and coord2.y == center.y):
        print_ipe_line(coord1, coord2, color)
    else:
        relative_point1 = euclidean_coordinates.coordinate_relative_to_coordinate(coord1, center)
        native_point1 = relative_point1.to_native_coordinate_with_scale(scale)

        relative_point2 = euclidean_coordinates.coordinate_relative_to_coordinate(coord2, center)
        native_point2 = relative_point2.to_native_coordinate_with_scale(scale)

        angular_distance = native_point2.phi - native_point1.phi
        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            native_temp = native_point1
            native_point1 = native_point2
            native_point2 = native_temp

        distance = native_coordinates.distance_between(native_point1, native_point2)

        cos_gamma_2 = 0.0
        try: 
            cos_gamma_2 = (((math.cosh(native_point2.r) * math.cosh(distance)) - math.cosh(native_point1.r)) / (math.sinh(native_point2.r) * math.sinh(distance)))
        except (ZeroDivisionError, ValueError):
            pass

        line_points = []
        for i in range(0, render_detail):
            partial_distance = distance * (i / float(render_detail))
            r = 0.0
            try:
                r = math.acosh((math.cosh(native_point2.r) * math.cosh(partial_distance) - (math.sinh(native_point2.r) * math.sinh(partial_distance) * cos_gamma_2)))
            except (ZeroDivisionError, ValueError):
                pass
            gamma_prime = 0.0
            try:
                gamma_prime = math.acos(((math.cosh(r) * math.cosh(native_point2.r)) - math.cosh(partial_distance)) / (math.sinh(r) * math.sinh(native_point2.r)))
            except (ZeroDivisionError, ValueError):
                pass

            phi = native_point2.phi + gamma_prime
            native_line_point = native_coordinates.PolarCoordinate(r, phi)

            converted_point = native_line_point.to_euclidean_coordinate_with_scale(scale)
            euclidean_line_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)
            line_points.append(euclidean_line_point)

            if i > 0:
                print_ipe_line(line_points[i - 1], line_points[i], color)

        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            print_ipe_line(line_points[render_detail - 1], coord2, color)
        else:
            print_ipe_line(line_points[render_detail - 1], coord1, color)

def print_ipe():
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    global scale

    print("<?xml version=\"1.0\"?>\n" +\
          "<!DOCTYPE ipe SYSTEM \"ipe.dtd\">\n" +\
          "<ipe version=\"70206\" creator=\"Ipe 7.2.7\">\n" +\
          "<info created=\"D:20170719160807\" modified=\"D:20170719160807\"/>\n" +\
          "<ipestyle name=\"basic\">\n" +\
          "</ipestyle>\n" +\
          "<page>\n" +\
          "<layer name=\"alpha\"/>\n" +\
          "<view layers=\"alpha\" active=\"alpha\"/>\n")

    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    print_ipe_circle(center, 2.0, True, "black")

    render_detail = 360
    render_detail_half = render_detail / 2

    for index, point in enumerate(points):
        if is_circle_node[index]:
            if index in selected_nodes:
                print_ipe_circle(point, 2.0, True, "black")
            else:
                print_ipe_circle(point, 2.0, True, "black")

            circle_size = circle_sizes[index]
            relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
            native_point = relative_point.to_native_coordinate_with_scale(scale)

            additional_render_detail = 8 * math.floor(native_point.r)
            angular_point_distance = 2.0 * math.pi / render_detail

            circle_points = []
            for i in range(render_detail):
                native_circle_point = native_coordinates.PolarCoordinate(circle_size, i * angular_point_distance)
                circle_points.append(native_circle_point)

                if abs(i - render_detail_half) < (additional_render_detail / 2):
                    for j in range(additional_render_detail):
                        native_circle_point = native_coordinates.PolarCoordinate(circle_size, \
                        i * angular_point_distance + j * (angular_point_distance / additional_render_detail))
                        circle_points.append(native_circle_point)

            for i in range(len(circle_points)):
                native_circle_point = circle_points[i]
                translated_point = native_coordinates.coordinate_translated_along_x_axis_by_hyperbolic_distance(native_circle_point, native_point.r)
                rotated_point = native_coordinates.coordinate_rotated_around_origin_by_angle(translated_point, native_point.phi)
                converted_point = rotated_point.to_euclidean_coordinate_with_scale(scale)
                euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)

                circle_points[i] = euclidean_circle_point

                if i > 0:
                    print_ipe_line(circle_points[i - 1], circle_points[i], colors[circle_colors[index]])

            print_ipe_line(circle_points[len(circle_points) - 1], circle_points[0], colors[circle_colors[index]])
        else:
            relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
            native_point = relative_point.to_native_coordinate_with_scale(scale)

            if index in selected_nodes:
                print_ipe_circle(point, 2.0, True, "black")
            else:
                print_ipe_circle(point, 2.0, True, "black")

    for edge in edges:
        (node1, node2) = edge
        print_ipe_edge(points[node1], points[node2], "black")

    print("</page>\n" +\
          "</ipe>")

def print_svg():
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    global scale

    print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE svg PUBLIC " +\
          "\"-//W3C//DTD SVG 1.1//EN\" " +\
          "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n\n<svg " +\
          "xmlns=\"http://www.w3.org/2000/svg\"\nxmlns:xlink=\"http://" +\
          "www.w3.org/1999/xlink\" " +\
          "xmlns:ev=\"http://www.w3.org/2001/xml-events\"\nversion=\"1.1\" " +\
          "baseProfile=\"full\"\nwidth=\"" + str(canvas.winfo_width()) + "\" height=\"" + str(canvas.winfo_height()) + "\">\n\n")

    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    print_circle(center, 2.0, True, "blue")

    render_detail = 360
    render_detail_half = render_detail / 2

    for index, point in enumerate(points):
        if is_circle_node[index]:
            if index in selected_nodes:
                print_circle(point, 2.0, True, "red")
            else:
                print_circle(point, 2.0, True, "black")

            circle_size = circle_sizes[index]
            relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
            native_point = relative_point.to_native_coordinate_with_scale(scale)

            additional_render_detail = 8 * math.floor(native_point.r)
            angular_point_distance = 2.0 * math.pi / render_detail

            circle_points = []
            for i in range(render_detail):
                native_circle_point = native_coordinates.PolarCoordinate(circle_size, i * angular_point_distance)
                circle_points.append(native_circle_point)

                if abs(i - render_detail_half) < (additional_render_detail / 2):
                    for j in range(additional_render_detail):
                        native_circle_point = native_coordinates.PolarCoordinate(circle_size, \
                        i * angular_point_distance + j * (angular_point_distance / additional_render_detail))
                        circle_points.append(native_circle_point)

            for i in range(len(circle_points)):
                native_circle_point = circle_points[i]
                translated_point = native_coordinates.coordinate_translated_along_x_axis_by_hyperbolic_distance(native_circle_point, native_point.r)
                rotated_point = native_coordinates.coordinate_rotated_around_origin_by_angle(translated_point, native_point.phi)
                converted_point = rotated_point.to_euclidean_coordinate_with_scale(scale)
                euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)

                circle_points[i] = euclidean_circle_point

                if i > 0:
                    print_line(circle_points[i - 1], circle_points[i], colors[circle_colors[index]])

            print_line(circle_points[len(circle_points) - 1], circle_points[0], colors[circle_colors[index]])
        else:
            relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
            native_point = relative_point.to_native_coordinate_with_scale(scale)

            if index in selected_nodes:
                print_circle(point, 2.0, True, "red")
            else:
                print_circle(point, 2.0, True, "black")

    for edge in edges:
        (node1, node2) = edge
        print_edge(points[node1], points[node2], "black")

    print("\n</svg>\n")

def hyperbolic_coordinate_from_canvas_point(canvas, point):
    global scale
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)
    relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
    native_point = relative_point.to_native_coordinate_with_scale(scale)
    return native_point

def redraw(canvas):
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    global scale
    canvas.delete("all")
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    draw_circle(canvas, center, 2.0, 0.0, 2.0 * math.pi, True, "blue")

    render_detail = 360
    render_detail_half = render_detail / 2

    for index, point in enumerate(points):
        if is_circle_node[index]:
            if index in selected_nodes:
                draw_circle(canvas, point, 2.0, 0.0, 2.0 * math.pi, True, "red")
            else:
                draw_circle(canvas, point, 2.0, 0.0, 2.0 * math.pi, True, "black")

            circle_size = circle_sizes[index]
            native_point = hyperbolic_coordinate_from_canvas_point(canvas, point)

            additional_render_detail = math.floor(native_point.r * native_point.r)
            render_detail_factor = 0
            if native_point.r > 0:
                render_detail_factor = min(1.0, 0.75 * scale / (native_point.r * native_point.r))
            angular_point_distance = 2.0 * math.pi / render_detail

            # is_additional = []

            circle_points = []
            for i in range(render_detail):
                native_circle_point = native_coordinates.PolarCoordinate(circle_size, i * angular_point_distance)
                circle_points.append(native_circle_point)
                # is_additional.append("red")

                if i == render_detail_half:
                    for j in range(additional_render_detail):
                        native_circle_point = native_coordinates.PolarCoordinate(circle_size, \
                        i * angular_point_distance + j * (render_detail_factor * angular_point_distance / additional_render_detail))
                        circle_points.append(native_circle_point)
                        # is_additional.append("blue")
                elif i == render_detail_half - 1:
                    for j in range(additional_render_detail):
                        native_circle_point = native_coordinates.PolarCoordinate(circle_size, \
                        (i + (1.0 - render_detail_factor)) * angular_point_distance + j * (render_detail_factor * angular_point_distance / additional_render_detail))
                        circle_points.append(native_circle_point)
                        # is_additional.append("blue")
                elif abs(i - render_detail_half) <= 7 * render_detail_factor - 4:
                    for j in range(math.floor(additional_render_detail * render_detail_factor * render_detail_factor)):
                        native_circle_point = native_coordinates.PolarCoordinate(circle_size, \
                        i * angular_point_distance + j * (angular_point_distance / (additional_render_detail * render_detail_factor * render_detail_factor)))
                        circle_points.append(native_circle_point)
                        # is_additional.append("green")

            for i in range(len(circle_points)):
                native_circle_point = circle_points[i]
                translated_point = native_coordinates.coordinate_translated_along_x_axis_by_hyperbolic_distance(native_circle_point, native_point.r)
                rotated_point = native_coordinates.coordinate_rotated_around_origin_by_angle(translated_point, native_point.phi)
                converted_point = rotated_point.to_euclidean_coordinate_with_scale(scale)
                euclidean_circle_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, converted_point)

                circle_points[i] = euclidean_circle_point
                # draw_circle(canvas, circle_points[i], 2.0, 0.0, 2.0 * math.pi, True, is_additional[i])

                if i > 0:
                    draw_line_from_coordinate_to_coordinate(canvas, circle_points[i - 1], circle_points[i], colors[circle_colors[index]])

            draw_line_from_coordinate_to_coordinate(canvas, circle_points[len(circle_points) - 1], circle_points[0], colors[circle_colors[index]])
        else:
            relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
            native_point = relative_point.to_native_coordinate_with_scale(scale)

            if index in selected_nodes:
                draw_circle(canvas, point, 2.0, 0.0, 2.0 * math.pi, True, "red")
            else:
                draw_circle(canvas, point, 2.0, 0.0, 2.0 * math.pi, True, "black")

    for edge in edges:
        (node1, node2) = edge
        draw_edge_from_coordinate_to_coordinate(canvas, points[node1], points[node2], "black")

# Internally, the angle 0 is on the left. We want it on the right.
def converted_angle_from_native_angle(angle):
    return (3.0 * math.pi - angle) % (2.0 * math.pi)

def update_status_label():
    global status_label
    global is_circle_node
    global circle_sizes
    global points
    status_label_text = ""
    if len(selected_nodes) > 0:
        for selected_node in selected_nodes:
            if is_circle_node[selected_node]:
                circle_center = hyperbolic_coordinate_from_canvas_point(canvas, points[selected_node])
                status_label_text += "Circle Center: (" + "{:1.4f}".format(circle_center.r) + ", " + "{:1.4f}".format(converted_angle_from_native_angle(circle_center.phi)) + "), Radius: " + "{:1.4}".format(circle_sizes[selected_node]) + "\n"
            else:
                coordinate = hyperbolic_coordinate_from_canvas_point(canvas, points[selected_node])
                status_label_text += "Point: (" + "{:1.4f}".format(coordinate.r) + ", " + "{:1.4f}".format(converted_angle_from_native_angle(coordinate.phi)) + ")" + "\n"

    status_label['text'] = status_label_text

# Mouse Interaction
def mouse_pressed(event):
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)

    shortest_distance = sys.float_info.max
    global selected_nodes

    for index, point in enumerate(points):
        distance = euclidean_coordinates.distance_between(mouse_location, point)
        if distance < shortest_distance:
            del selected_nodes[:]
            selected_nodes.append(index)
            shortest_distance = distance

    update_status_label()
    redraw(canvas)


def shift_mouse_pressed(event):
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)

    shortest_distance = sys.float_info.max
    global selected_nodes

    selected_index = -1
    for index, point in enumerate(points):
        distance = euclidean_coordinates.distance_between(mouse_location, point)
        if distance < shortest_distance:
            selected_index = index
            shortest_distance = distance

    if selected_index >= 0:
        if not selected_index in selected_nodes:
            selected_nodes.append(selected_index)

    update_status_label()
    redraw(canvas)


def mouse_dragged(event):
    global selected_nodes
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)
    if len(selected_nodes) > 0:
        points[selected_nodes[0]] = mouse_location
    update_status_label()
    redraw(canvas)

def right_mouse_pressed(event):
    global current_circle_size
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)
    points.append(mouse_location)
    is_circle_node.append(True)
    circle_sizes.append(current_circle_size)
    circle_colors.append(0)
    redraw(canvas)

def shift_right_mouse_pressed(event):
    global current_circle_size
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)
    points.append(mouse_location)
    is_circle_node.append(False)
    circle_sizes.append(current_circle_size)
    circle_colors.append(0)
    redraw(canvas)

def mouse_scrolled_with_delta(delta):
    global selected_nodes
    global current_circle_size
    for selected_node in selected_nodes:
        if is_circle_node[selected_node]:
            current_circle_size = circle_sizes[selected_node]
            current_circle_size += 0.1 * delta

            if current_circle_size < 0.1:
                current_circle_size = 0.1

            circle_sizes[selected_node] = current_circle_size

    update_status_label()
    redraw(canvas)

def mouse_scrolled(event):
    mouse_scrolled_with_delta(event.delta)

def mouse_scroll_up(event):
    mouse_scrolled_with_delta(1)

def mouse_scroll_down(event):
    mouse_scrolled_with_delta(-1)

# Keyboard Interaction
def delete_pressed(event):
    global selected_nodes
    global edges
    for selected_node in selected_nodes:
        for edge in edges:
            if selected_node in edge:
                edges.remove(edge)
        points.pop(selected_node)
        is_circle_node.pop(selected_node)
        circle_sizes.pop(selected_node)
        circle_colors.pop(selected_node)
    del selected_nodes[:]

    update_status_label()
    redraw(canvas)

def c_pressed(event):
    global selected_nodes
    for selected_node in selected_nodes:
        if is_circle_node[selected_node]:
            selected_node_color_index = circle_colors[selected_node]
            selected_node_color_index += 1
            selected_node_color_index %= len(colors)
            circle_colors[selected_node] = selected_node_color_index
            redraw(canvas)

def o_pressed(event):
    global current_circle_size
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)
    points.append(center)
    is_circle_node.append(True)
    circle_sizes.append(current_circle_size)
    circle_colors.append(0)
    redraw(canvas)

def d_pressed(event):
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    points = []
    edges = []
    circle_sizes = []
    circle_colors = []
    selected_nodes = []
    is_circle_node = []
    current_circle_size = 5.0

    global status_label
    status_label["text"] = "Deleted everything."
    redraw(canvas)

def e_pressed(event):
    global selected_nodes
    global edges
    for i in range(0, len(selected_nodes)):
        for j in range(i + 1, len(selected_nodes)):
            selected_node1 = selected_nodes[i]
            selected_node2 = selected_nodes[j]
            edge = (selected_node1, selected_node2)
            inverse_edge = (selected_node2, selected_node1) 
            if edge in edges:
                edges.remove(edge)
            elif inverse_edge in edges:
                edges.remove(inverse_edge)
            else:
                edges.append(edge)
    redraw(canvas)

def g_pressed(event):
    global selected_nodes
    global edges
    for i in range(0, len(selected_nodes)):
        for j in range(i + 1, len(selected_nodes)):
            selected_node1 = selected_nodes[i]
            selected_node2 = selected_nodes[j]
            edge = (selected_node1, selected_node2)
            inverse_edge = (selected_node2, selected_node1) 
            if edge in edges:
                edges.remove(edge)
            elif inverse_edge in edges:
                edges.remove(inverse_edge)
            else:
                edges.append(edge)
    redraw(canvas)

def r_pressed(event):
    global selected_nodes
    if len(selected_nodes) > 1:
        center = euclidean_coordinates.EuclideanCoordinate(\
                                                           canvas.winfo_width() / 2.0, \
                                                           canvas.winfo_height() / 2.0)
        reference_point = points[selected_nodes[0]]
        relative_reference_point = euclidean_coordinates.coordinate_relative_to_coordinate(reference_point, center)
        native_reference_point = relative_reference_point.to_native_coordinate_with_scale(1.0)
        reference_radius = native_reference_point.r
        for i in range(1, len(selected_nodes)):
            original_point = points[selected_nodes[i]]
            relative_original_point = euclidean_coordinates.coordinate_relative_to_coordinate(original_point, center)
            native_original_point = relative_original_point.to_native_coordinate_with_scale(1.0)
            native_original_point.r = reference_radius
            relative_modified_point = native_original_point.to_euclidean_coordinate_with_scale(1.0)
            modified_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, relative_modified_point)
            points[selected_nodes[i]] = modified_point

        redraw(canvas)

def s_pressed(event):
    call(["mkdir", "-p", "output"])
    old_stdout = sys.stdout
    import datetime
    filename = './output/' + str(datetime.datetime.now()) + '.svg'
    sys.stdout = open(filename, "w")
    print_svg()
    sys.stdout = old_stdout
    global status_label
    status_label["text"] = "Drawing saved as " + filename

def i_pressed(event):
    call(["mkdir", "-p", "output"])
    old_stdout = sys.stdout
    import datetime
    filename = './output/' + str(datetime.datetime.now()) + '.ipe'
    sys.stdout = open(filename, "w")
    print_ipe()
    sys.stdout = old_stdout
    global status_label
    status_label["text"] = "Drawing saved as " + filename

canvas.bind("<Configure>", resize)
canvas.bind("<Button-1>", mouse_pressed)
canvas.bind("<Shift-Button-1>", shift_mouse_pressed)
canvas.bind("<B1-Motion>", mouse_dragged)
canvas.bind("<Button-2>", right_mouse_pressed)
canvas.bind("<Shift-Button-2>", shift_right_mouse_pressed)
canvas.bind("<Button-3>", right_mouse_pressed)
canvas.bind("<Shift-Button-3>", shift_right_mouse_pressed)
canvas.bind("<Button-4>", mouse_scroll_up)
canvas.bind("<Button-5>", mouse_scroll_down)
root.bind("<BackSpace>", delete_pressed)
root.bind("<MouseWheel>", mouse_scrolled)
root.bind("c", c_pressed)
root.bind("d", d_pressed)
root.bind("e", e_pressed)
root.bind("g", g_pressed)
root.bind("i", i_pressed)
root.bind("o", o_pressed)
root.bind("r", r_pressed)
root.bind("s", s_pressed)
root.bind("+", mouse_scroll_up)
root.bind("-", mouse_scroll_down)

usage_label = Label(canvas, text = \
                "Right Click: Add point and circle \n" +\
                "Shift Right Click: Adds a point without a circle \n" +\
                "Left Click: Select a point \n" +\
                "Shift Left Click: Add to selection \n" +\
                "O: Add circle around the oririn \n" +\
                "E: Add an edge between all selected nodes \n" +\
                "R: Set radii of selected points to the one of the first seleced \n" +\
                "Back Space: Delete selected point \n" +\
                "MouseWheel / '+' / '-': Change Circle Radius \n" +\
                "C: Cycle through the colors [Black, Green, Red, Blue, Orange and Magenta]\n" +\
                "S: Print the drawing as SVG\n" +\
                "I: Print the drawing as IPE\n" +\
                "D: Delete everything", justify=LEFT)
usage_label.pack(side = BOTTOM, anchor=W)

status_label = Label(canvas, text = "", justify=RIGHT)
status_label.pack(side = TOP, anchor=E)

while True:
    try:
        mainloop()
        break
    except UnicodeDecodeError:
        pass
