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
import datetime
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
    drawer.clear()
    redraw()

### Main ###

items = []
edges = []
selected_nodes = []
current_circle_size = 10.0

def redraw():
    global items
    global edges
    global selected_nodes

    drawer.clear()
    drawer.draw(items,
                edges,
                selected_nodes)

### Saving ###

def print_ipe():
    global items
    global edges
    global selected_nodes
    printer = printing.printer(drawer)
    printer.print_ipe(items,
                      edges,
                      selected_nodes)

def print_svg():
    global items
    global edges
    global selected_nodes
    printer = printing.printer(drawer)
    printer.print_svg(items,
                      edges,
                      selected_nodes)

# Internally, the angle 0 is on the left. We want it on the right.
def converted_angle_from_native_angle(angle):
    return (3.0 * math.pi - angle) % (2.0 * math.pi)

def set_status_label_text(text):
    global status_label
    status_label['text'] = text

def update_status_label():
    global items
    global selected_nodes

    status_label_text = ""

    if len(selected_nodes) > 0:
        for selected_node in selected_nodes:
            item = items[selected_node]
            if drawing.is_circle_item(items[selected_node]):
                circle_center = drawer.hyperbolic_coordinate_from_canvas_point(item.coordinate)
                status_label_text += "Circle Center: (" + "{:1.4f}".format(circle_center.r) + ", " + "{:1.4f}".format(converted_angle_from_native_angle(circle_center.phi)) + "), Radius: " + "{:1.4}".format(item.radius) + "\n"
            else:
                coordinate = drawer.hyperbolic_coordinate_from_canvas_point(item.coordinate)
                status_label_text += "Point: (" + "{:1.4f}".format(coordinate.r) + ", " + "{:1.4f}".format(converted_angle_from_native_angle(coordinate.phi)) + ")" + "\n"

    set_status_label_text(status_label_text)

# Mouse Interaction
def mouse_pressed(event):
    global selected_nodes

    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)
    shortest_distance = sys.float_info.max

    for index, item in enumerate(items):
        distance = euclidean_coordinates.distance_between(mouse_location, item.coordinate)

        if distance < shortest_distance:
            del selected_nodes[:]
            selected_nodes.append(index)
            shortest_distance = distance

    update_status_label()
    redraw()

def shift_mouse_pressed(event):
    global selected_nodes

    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)
    shortest_distance = sys.float_info.max

    selected_index = -1
    for index, item in enumerate(items):

        distance = euclidean_coordinates.distance_between(mouse_location,
                                                          item.coordinate)

        if distance < shortest_distance:
            selected_index = index
            shortest_distance = distance

    if selected_index >= 0:
        if not selected_index in selected_nodes:
            selected_nodes.append(selected_index)

    update_status_label()
    redraw()

def mouse_dragged(event):
    global selected_nodes

    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)

    if len(selected_nodes) > 0:
        item = items[selected_nodes[0]]
        item.coordinate = mouse_location
        items[selected_nodes[0]] = item

    update_status_label()
    redraw()

def right_mouse_pressed(event):
    global current_circle_size

    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)

    circle = drawing.circle(coordinate = mouse_location,
                            radius = current_circle_size,
                            color = 0)
    items.append(circle)
    redraw()

def shift_right_mouse_pressed(event):
    global current_circle_size

    mouse_location = euclidean_coordinates.euclidean_coordinate(event.x, event.y)

    point = drawing.point(coordinate = mouse_location, color = 0)
    items.append(point)
    redraw()

def mouse_scrolled_with_delta(delta):
    global selected_nodes
    global current_circle_size

    for selected_node in selected_nodes:
        item = items[selected_node]
        if drawing.is_circle_item(item):
            current_circle_size = item.radius
            current_circle_size += 0.1 * delta

            if current_circle_size < 0.1:
                current_circle_size = 0.1

            item.radius = current_circle_size
            items[selected_node] = item

    update_status_label()
    redraw()

def mouse_scrolled(event):
    mouse_scrolled_with_delta(event.delta)

def mouse_scroll_up(event):
    mouse_scrolled_with_delta(1)

def mouse_scroll_down(event):
    mouse_scrolled_with_delta(-1)

# Keyboard Interaction
def delete_pressed(event):
    global items
    global edges
    global selected_nodes

    sorted_selection_indices = sorted(selected_nodes)

    # Vertices will be deleted so the indices of the other vertices change.
    # Here we determine the map from the old indices to the new ones
    index_map = dict()
    current_new_index = 0
    for index in range(len(items)):
        if not index in sorted_selection_indices:
            index_map[index] = current_new_index
            current_new_index += 1

    for selected_node in reversed(sorted_selection_indices):
        edges_to_remove = []
        for index, edge in enumerate(edges):
            if edge.index1 == selected_node or edge.index2 == selected_node:
                edges_to_remove.append(index)

        for edge_index in reversed(sorted(edges_to_remove)):
            del edges[edge_index]

        del items[selected_node]

    for index, edge in enumerate(edges):
        for old_index, new_index in index_map.items():
            if edge.index1 == old_index:
                edge.index1 = new_index
            if edge.index2 == old_index:
                edge.index2 = new_index
            edges[index] = edge

    del selected_nodes[:]

    update_status_label()
    redraw()

def c_pressed(event):
    global selected_nodes
    for selected_node in selected_nodes:
        item = items[selected_node]
        selected_node_color_index = item.color
        selected_node_color_index += 1
        selected_node_color_index %= len(drawer.colors)
        item.color = selected_node_color_index
        items[selected_node] = item
        redraw()

def o_pressed(event):
    global current_circle_size

    center = euclidean_coordinates.euclidean_coordinate(\
        canvas.winfo_width() / 2.0, \
        canvas.winfo_height() / 2.0)

    origin = drawing.circle(center, current_circle_size, 0)

    items.append(origin)
    redraw()

def d_pressed(event):
    global items
    global edges
    global selected_nodes
    items = []
    edges = []
    selected_nodes = []
    current_circle_size = 10.0

    set_status_label_text("Cleared")
    redraw()

def e_pressed(event):
    global selected_nodes
    global edges

    for i in range(0, len(selected_nodes)):
        for j in range(i + 1, len(selected_nodes)):
            selected_node1 = selected_nodes[i]
            selected_node2 = selected_nodes[j]
            new_edge = drawing.edge(selected_node1, selected_node2)

            edge_already_present = False
            for edge in edges:
                if (edge.index1 == selected_node1 and edge.index2 == selected_node2) or (edge.index2 == selected_node1 and edge.index1 == selected_node2):
                    edges.remove(edge)
                    edge_already_present = True
                    break

            if not edge_already_present:
                edges.append(new_edge)
    redraw()

def h_pressed(event):
    global selected_nodes
    global edges

    if len(selected_nodes) == 2:
        selected_node1 = selected_nodes[0]
        selected_node2 = selected_nodes[1]
        edge = (selected_node1, selected_node2)
        inverse_edge = (selected_node2, selected_node1)

        edge_exists = False
        if edge in edges:
            edge_exists = True
        elif inverse_edge in edges:
            edge = inverse_edge
            edge_exists = True

        if not edge_exists:
            edges.append(edge)

        redraw()

    else:
        set_status_label_text("Select exactly 2 nodes to add a hypercycle!")

def r_pressed(event):
    global selected_nodes

    if len(selected_nodes) > 1:
        center = euclidean_coordinates.euclidean_coordinate(\
                                                           canvas.winfo_width() / 2.0, \
                                                           canvas.winfo_height() / 2.0)
        reference_point = items[selected_nodes[0]].coordinate
        relative_reference_point = euclidean_coordinates.coordinate_relative_to_coordinate(reference_point, center)
        native_reference_point = relative_reference_point.to_native_coordinate_with_scale(1.0)
        reference_radius = native_reference_point.r
        for i in range(1, len(selected_nodes)):
            item = items[selected_nodes[i]]
            original_point = item.coordinate
            relative_original_point = euclidean_coordinates.coordinate_relative_to_coordinate(original_point, center)
            native_original_point = relative_original_point.to_native_coordinate_with_scale(1.0)
            native_original_point.r = reference_radius
            relative_modified_point = native_original_point.to_euclidean_coordinate_with_scale(1.0)
            modified_point = euclidean_coordinates.coordinate_relative_to_coordinate(center, relative_modified_point)
            item.coordinate = modified_point
            items[selected_nodes[i]] = item

        update_status_label()
        redraw()

def s_pressed(event):
    call(["mkdir", "-p", "output"])
    old_stdout = sys.stdout
    filename = './output/' + str(datetime.datetime.now()) + '.svg'
    sys.stdout = open(filename, "w")
    print_svg()
    sys.stdout = old_stdout
    global status_label
    set_status_label_text("Drawing saved as " + filename)

def i_pressed(event):
    call(["mkdir", "-p", "output"])
    old_stdout = sys.stdout
    filename = './output/' + str(datetime.datetime.now()) + '.ipe'
    sys.stdout = open(filename, "w")
    print_ipe()
    sys.stdout = old_stdout
    global status_label
    set_status_label_text("Drawing saved as " + filename)

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
root.bind("h", h_pressed)
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
                "H: Add a hypercycle (partially) around 2 selected nodes \n" +\
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
