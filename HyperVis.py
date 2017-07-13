# This program visualizes hyperbolic circles using the native representation.
# Copyright (C) 2017    Maximilian Katzmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# You can contact the author via email: max.katzmann@gmail.com

from tkinter import *
# Reference: https://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
import math
import sys
import native_coordinates
import euclidean_coordinates

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
circle_sizes = []
circle_colors = []
selected_node = -1
current_circle_size = 5.0
colors = ["black", "red", "green", "blue", "orange", "magenta"];

def redraw(canvas):
    global selected_node
    canvas.delete("all")
    center = euclidean_coordinates.EuclideanCoordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    draw_circle(canvas, center, 2.0, 0.0, 2.0 * math.pi, True, "blue")

    scale = 50.0
    render_detail = 360
    render_detail_half = render_detail / 2

    for index, point in enumerate(points):

        circle_size = circle_sizes[index]
        relative_point = euclidean_coordinates.coordinate_relative_to_coordinate(point, center)
        native_point = relative_point.to_native_coordinate_with_scale(scale)
        native_point.phi += math.pi

        if index == selected_node:
            draw_circle(canvas, point, 2.0, 0.0, 2.0 * math.pi, True, "red")
        else:
            draw_circle(canvas, point, 2.0, 0.0, 2.0 * math.pi, True, "black")

        additional_render_detail = 4 * math.floor(native_point.r)
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
                draw_line_from_coordinate_to_coordinate(canvas, circle_points[i - 1], circle_points[i], colors[circle_colors[index]])

        draw_line_from_coordinate_to_coordinate(canvas, circle_points[len(circle_points) - 1], circle_points[0], colors[circle_colors[index]])


# Mouse Interaction
def mouse_pressed(event):
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)

    shortest_distance = sys.float_info.max
    global selected_node

    for index, point in enumerate(points):
        distance = euclidean_coordinates.distance_between(mouse_location, point)
        if distance < shortest_distance:
            selected_node = index
            shortest_distance = distance
    redraw(canvas)

def mouse_dragged(event):
    global selected_node
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)
    if selected_node >= 0:
        points[selected_node] = mouse_location
    redraw(canvas)

def right_mouse_pressed(event):
    global current_circle_size
    mouse_location = euclidean_coordinates.EuclideanCoordinate(event.x, event.y)
    points.append(mouse_location)
    circle_sizes.append(current_circle_size)
    circle_colors.append(0)
    redraw(canvas)

def mouse_scrolled_with_delta(delta):
    global selected_node
    global current_circle_size
    if selected_node >= 0:
        current_circle_size = circle_sizes[selected_node]
        current_circle_size += 0.1 * delta

        if current_circle_size < 0.1:
            current_circle_size = 0.1

        circle_sizes[selected_node] = current_circle_size
        redraw(canvas)

def mouse_scrolled(event):
    mouse_scrolled_with_delta(event.delta)

def mouse_scroll_up(event):
    mouse_scrolled_with_delta(1)

def mouse_scroll_down(event):
    mouse_scrolled_with_delta(-1)

# Keyboard Interaction
def delete_pressed(event):
    global selected_node
    if selected_node >= 0:
        points.pop(selected_node)
        circle_sizes.pop(selected_node)
        circle_colors.pop(selected_node)
        selected_node = -1
        redraw(canvas)

def c_pressed(event):
    global selected_node
    if selected_node >= 0:
        selected_node_color_index = circle_colors[selected_node]
        selected_node_color_index += 1
        selected_node_color_index %= len(colors)
        circle_colors[selected_node] = selected_node_color_index
        redraw(canvas)


canvas.bind("<Configure>", resize)
canvas.bind("<Button-1>", mouse_pressed)
canvas.bind("<B1-Motion>", mouse_dragged)
canvas.bind("<Button-2>", right_mouse_pressed)
canvas.bind("<Button-3>", right_mouse_pressed)
canvas.bind("<Button-4>", mouse_scroll_up)
canvas.bind("<Button-5>", mouse_scroll_down)
root.bind("<BackSpace>", delete_pressed)
root.bind("<MouseWheel>", mouse_scrolled)
root.bind("c", c_pressed)
root.bind("+", mouse_scroll_up)
root.bind("-", mouse_scroll_down)

message = Label(canvas, text = "Right Click adds a point and circle, Left Click " +\
    "selects a point, Back Space deletes the selected point.\nThe radius of a " +\
    "selected circle can be changed using the mouse wheel or the '+' and '-' buttons.\n" +\
    "New circles are black and will have the same radius as the last one that was edited.\n" +\
    "You can cycle through the colors [Black, Green, Red, Blue, Orange and Magenta]\nof the " +\
    "selected circle using the 'C' key.")
message.pack(side = TOP)

while True:
    try:
        mainloop()
        break
    except UnicodeDecodeError:
        pass
