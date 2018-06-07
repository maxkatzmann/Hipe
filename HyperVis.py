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
import drawing
import native_coordinates
import euclidean_coordinates
import printing
from subprocess import call

# Creating the widget
root = Tk()
root.title("HyperVis")

# Creating the canvas
canvas = Canvas(root, width = 800, height = 600)
canvas.pack(fill=BOTH, expand=YES)

scale = 35.0
drawer = drawing.drawer(canvas, scale)

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

def print_ipe():
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    global scale
    printer = printing.printer(canvas, scale)
    printer.print_ipe(points, edges, circle_sizes, circle_colors,
                      selected_nodes, is_circle_node)

def print_svg():
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    global scale
    printer = printing.printer(canvas, scale)
    printer.print_svg(points, edges, circle_sizes, circle_colors,
                      selected_nodes, is_circle_node)

def redraw(canvas):
    global points
    global edges
    global circle_sizes
    global circle_colors
    global selected_nodes
    global is_circle_node
    global scale
    drawer.clear()
    drawer.draw(points,
                edges,
                circle_sizes,
                circle_colors,
                selected_nodes,
                is_circle_node)

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
                circle_center = drawer.hyperbolic_coordinate_from_canvas_point(points[selected_node])
                status_label_text += "Circle Center: (" + "{:1.4f}".format(circle_center.r) + ", " + "{:1.4f}".format(converted_angle_from_native_angle(circle_center.phi)) + "), Radius: " + "{:1.4}".format(circle_sizes[selected_node]) + "\n"
            else:
                coordinate = drawer.hyperbolic_coordinate_from_canvas_point(points[selected_node])
                status_label_text += "Point: (" + "{:1.4f}".format(coordinate.r) + ", " + "{:1.4f}".format(converted_angle_from_native_angle(coordinate.phi)) + ")" + "\n"

    status_label['text'] = status_label_text

# Mouse Interaction
def mouse_pressed(event):
    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)

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
    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)

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
    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)
    if len(selected_nodes) > 0:
        points[selected_nodes[0]] = mouse_location
    update_status_label()
    redraw(canvas)

def right_mouse_pressed(event):
    global current_circle_size
    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)
    points.append(mouse_location)
    is_circle_node.append(True)
    circle_sizes.append(current_circle_size)
    circle_colors.append(0)
    redraw(canvas)

def shift_right_mouse_pressed(event):
    global current_circle_size
    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)
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
            selected_node_color_index %= len(drawer.colors)
            circle_colors[selected_node] = selected_node_color_index
            redraw(canvas)

def o_pressed(event):
    global current_circle_size
    center = euclidean_coordinates.euclidean_coordinate(\
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
        center = euclidean_coordinates.euclidean_coordinate(\
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
