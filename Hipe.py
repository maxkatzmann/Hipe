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

# Reference: https://info host.nmt.edu/tcc/help/pubs/tkinter/web/index.html
import copy
import datetime
import functools
import math
import sys
from enum import Enum
from subprocess import call
from tkinter import *

import drawing
import embedded_graph
import euclidean_coordinates
import gui
import native_coordinates
import printing

# Modes
Mode = Enum("Mode", "select translate mark circle polygon")

# Mode Selection


def update_mode_indicator():
    global gui
    global current_mode

    unhighlighted_color = "white"
    highlighted_color = gui.menu_color

    gui.select_label.configure(foreground=unhighlighted_color,
                               background=unhighlighted_color)
    gui.translate_label.configure(foreground=unhighlighted_color,
                                  background=unhighlighted_color)
    gui.mark_label.configure(foreground=unhighlighted_color,
                             background=unhighlighted_color)
    gui.circle_label.configure(foreground=unhighlighted_color,
                               background=unhighlighted_color)
    gui.polygon_label.configure(foreground=unhighlighted_color,
                                background=unhighlighted_color)

    if current_mode == Mode.select:
        gui.select_label.configure(foreground=highlighted_color,
                                   background=highlighted_color)
    elif current_mode == Mode.translate:
        gui.translate_label.configure(foreground=highlighted_color,
                                      background=highlighted_color)
    elif current_mode == Mode.mark:
        gui.mark_label.configure(foreground=highlighted_color,
                                 background=highlighted_color)
    elif current_mode == Mode.circle:
        gui.circle_label.configure(foreground=highlighted_color,
                                   background=highlighted_color)
    else:
        gui.polygon_label.configure(foreground=highlighted_color,
                                    background=highlighted_color)


def set_mode_select():
    global current_mode
    global current_polygon

    current_mode = Mode.select

    # When we change the mode we cancel creating a polygon
    current_polygon = []

    update_mode_indicator()
    update_help_label()


def set_mode_translate():
    global current_mode
    global current_polygon

    current_mode = Mode.translate

    # When we change the mode we cancel creating a polygon
    current_polygon = []

    update_mode_indicator()
    update_help_label()


def set_mode_mark():
    global current_mode
    global current_polygon

    current_mode = Mode.mark

    # When we change the mode we cancel creating a polygon
    current_polygon = []

    update_mode_indicator()
    update_help_label()


def set_mode_circle():
    global current_mode
    global current_polygon

    current_mode = Mode.circle

    # When we change the mode we cancel creating a polygon
    current_polygon = []

    update_mode_indicator()
    update_help_label()


def set_mode_polygon():
    global current_mode

    current_mode = Mode.polygon
    update_mode_indicator()
    update_help_label()


### Drawing

selected_nodes = []
current_circle_size = 10.0
current_mode = Mode.select
mouse_location = None
current_possible_selections = []
current_polygon = []

# Drawing History
drawing_history = [([], [])]


# Save the current drawing state so we can back to it by undoing later steps.
def save_current_state():
    global drawing_history
    drawing_history.append(
        (copy.deepcopy(drawer.items), copy.deepcopy(drawer.edges)))


def undo(event):
    global drawer
    global selected_nodes
    global mouse_location
    global current_possible_selections
    global current_polygon
    global drawing_history

    if len(drawing_history) > 2:
        drawing_history.pop()
        (old_items, old_edges) = drawing_history[-1]

        # Mark current items for "redraw" (will be removed).
        drawer.mark_all_items_for_redraw()

        drawer.items = old_items
        drawer.edges = old_edges
        selected_nodes = []
        mouse_location = None
        current_possible_selections = []
        current_polygon = []
        set_status_label_text("Undid last action.")

        # Mark new items for redraw.
        drawer.mark_all_items_for_redraw()
        redraw()

    elif len(drawing_history) == 2:
        drawing_history = [([], [])]

        # Mark current items for "redraw" (will be removed).
        drawer.mark_all_items_for_redraw()

        drawer.items = []
        drawer.edges = []
        selected_nodes = []
        mouse_location = None
        current_possible_selections = []
        current_polygon = []
        set_status_label_text("Undid last action.")
        redraw()
    else:
        set_status_label_text("Cannot undo anymore.")


### Snapping

# While dragging an item can snap to other vertices with
# respect to the radial or angular coordinate.

is_snap_enabled = False

snapped_item_radial = None
snapped_item_angular = None


def toggle_snap():
    global is_snap_enabled
    global gui
    is_snap_enabled = not is_snap_enabled

    if is_snap_enabled:
        gui.snap_button.configure(text="[F1-4] Snap: On")
    else:
        gui.snap_button.configure(text="[F1-4] Snap: Off")


def resize(event):
    drawer.mark_all_items_for_redraw()
    drawer.clear()
    redraw()


def redraw():
    global selected_nodes
    global mouse_location
    global snapped_item_radial
    global snapped_item_angular

    # Make sure to always update the selected nodes.
    redraw_selected_nodes()
    drawer.draw(drawer.items, drawer.edges, selected_nodes, mouse_location,
                snapped_item_radial, snapped_item_angular)


def add_circle_at(position_E):
    global current_circle_size
    global selected_nodes

    coordinate_H = drawer.hyperbolic_coordinate_from_canvas_point(position_E)

    circle = drawing.circle(coordinate_H=coordinate_H,
                            radius=current_circle_size,
                            color=0)
    drawer.items.append(circle)
    index = len(drawer.items) - 1

    # The selected nodes are about to change, we need to redraw them.
    redraw_selected_nodes()

    selected_nodes = [index]

    # After adding a circle, we save the current state to the history.
    save_current_state()

    redraw()
    update_status_label()
    return index


def add_point_at(position_E):
    global selected_nodes

    coordinate_H = drawer.hyperbolic_coordinate_from_canvas_point(position_E)

    point = drawing.point(coordinate_H=coordinate_H, color=0)
    drawer.items.append(point)
    index = len(drawer.items) - 1

    # The selected nodes are about to change, we need to redraw them.
    redraw_selected_nodes()
    selected_nodes = [index]

    # After adding a point, we save the current state to the history.
    save_current_state()

    redraw()
    update_status_label()
    return index


def add_edge_between(node1, node2):
    new_edge = drawing.edge(node1, node2)

    edge_already_present = False
    for edge in drawer.edges:
        if (edge.index1 == node1
                and edge.index2 == node2) or (edge.index2 == node1
                                              and edge.index1 == node2):
            drawer.mark_edge_for_redraw(edge)
            drawer.edges.remove(edge)
            edge_already_present = True
            break

    if not edge_already_present:
        drawer.edges.append(new_edge)

    # After adding an edge, we save the current state to the history.
    save_current_state()

    redraw()


def remove_current_polygon():
    global current_polygon

    sorted_polygon_points = sorted(current_polygon)

    for polygon_node in reversed(sorted_polygon_points):
        del drawer.items[polygon_node]

    current_polygon = []


### Saving ###


def save_as_ipe():
    call(["mkdir", "-p", "output"])
    old_stdout = sys.stdout
    time_string = str(datetime.datetime.now())
    time_string = time_string.replace(" ", "_")
    time_string = time_string.replace(":", "-")
    time_string = time_string.replace(".", "-")
    filename = './output/' + time_string + '.ipe'
    sys.stdout = open(filename, "w")
    print_ipe()
    sys.stdout = old_stdout
    global status_label
    set_status_label_text("Drawing saved as " + filename)


def print_ipe():
    global selected_nodes
    printer = printing.printer(drawer)
    printer.print_ipe(drawer.items, drawer.edges, selected_nodes)

    # We just drew to something else than the canvas. Meaning all items were
    # redrawn (to the file) and afterwards not redrawn on the canvas. We do
    # that now.
    drawer.mark_all_items_for_redraw()
    redraw()


def save_as_svg():
    call(["mkdir", "-p", "output"])
    old_stdout = sys.stdout
    time_string = str(datetime.datetime.now())
    time_string = time_string.replace(" ", "_")
    time_string = time_string.replace(":", "-")
    time_string = time_string.replace(".", "-")
    filename = './output/' + time_string + '.svg'
    sys.stdout = open(filename, "w")
    print_svg()
    sys.stdout = old_stdout
    global status_label
    set_status_label_text("Drawing saved as " + filename)


def print_svg():
    global items
    global edges
    global selected_nodes
    printer = printing.printer(drawer)
    printer.print_svg(drawer.items, drawer.edges, selected_nodes)

    # We just drew to something else than the canvas. Meaning all items were
    # redrawn (to the file) and afterwards not redrawn on the canvas. We do
    # that now.
    drawer.mark_all_items_for_redraw()
    redraw()


# Internally, the angle 0 is on the left. We want it on the right.
def converted_angle_from_native_angle(angle):
    return (3.0 * math.pi - angle) % (2.0 * math.pi)


# Labels


def set_help_label_text(text):
    global help_label
    help_label['text'] = text


def set_status_label_text(text):
    global status_label
    status_label['text'] = text


def update_help_label():
    global current_mode
    help_text = ""

    if current_mode == Mode.select:
        help_text = \
            "Mouse 1: Select object\n" +\
            "Shift Mouse 1: Add to selection\n" +\
            "e: Add/remove edge between selected objects\n" +\
            "h: Add hypercycle around the line between 2 selected objects\n" +\
            "r: Set radii of selected objects to match radius of primary selection"

    elif current_mode == Mode.translate:
        help_text = \
            "Drag to move the primary selection"
    elif current_mode == Mode.mark:
        help_text = \
            "Mouse 1: Add a point"
    elif current_mode == Mode.circle:
        help_text = \
            "Mouse 1: Add a circle\n" +\
            "o: Add circle centered at the origin"
    else:
        help_text = \
            "Mouse 1: Add polygon point\n" +\
            "Mouse 2: Stop adding points\n" +\
            "Shift Mouse 2: Close polygon"

    help_text += "\n" +\
        "g: Add/remove grid\n" +\
        "G: Add/remove drawing of embedded input graph\n" +\
        "R: Add/remove regular grid\n" +\
        "c: Change color of selected objects\n" +\
        "d: Clear all\n" +\
        "z: Undo\n" +\
        "Mouse wheel / (+,-): Change current radius\n" +\
        "Shift Mouse wheel / (*,_): Change radii of selected items\n" +\
        "Control Mouse wheel / (Up,Down): Change scale\n" +\
        "Backspace: Delete selected objects\n" +\
        "Esc: Clear selection"

    set_help_label_text(help_text)


def update_status_label():
    global selected_nodes

    status_label_text = "Current scale: " + "{:1.4f}".format(
        drawer.scale) + "\n"
    status_label_text += "Current circle radius: " + "{:1.4f}".format(
        current_circle_size) + "\n"

    if len(selected_nodes) > 0:
        for selected_node in selected_nodes:
            item = drawer.items[selected_node]
            if drawing.is_circle_item(drawer.items[selected_node]):
                circle_center_H = item.coordinate_H
                status_label_text += "Circle Center: (" + "{:1.4f}".format(
                    circle_center_H.r) + ", " + "{:1.4f}".format(
                        converted_angle_from_native_angle(circle_center_H.phi)
                    ) + "), Radius: " + "{:1.4}".format(item.radius) + "\n"
            else:
                coordinate_H = item.coordinate_H
                status_label_text += "Point: (" + "{:1.4f}".format(
                    coordinate_H.r) + ", " + "{:1.4f}".format(
                        converted_angle_from_native_angle(
                            coordinate_H.phi)) + ")" + "\n"

    set_status_label_text(status_label_text)


def redraw_selected_nodes():
    global selected_nodes

    for index in selected_nodes:
        item = drawer.items[index]
        drawer.mark_item_for_redraw(item)


# Mouse Interaction
def mouse_down(event):
    global drawer
    global current_mode
    global mouse_location
    global selected_nodes

    current_mouse_location_E = euclidean_coordinates.euclidean_coordinate(
        event.x, event.y)

    if current_mode == Mode.select:
        global current_possible_selections

        # The selected nodes will now change, make sure to redraw the currently
        # selected ones.
        redraw_selected_nodes()
        selected_nodes = []

        def distance_cmp(a, b):
            if a[1] > b[1]:
                return 1
            elif a[1] == b[1]:
                return 0
            else:
                return -1

        possible_selections = []

        for index, item in enumerate(drawer.items):
            item_position_E = drawer.canvas_point_from_hyperbolic_coordinate(
                item.coordinate_H)
            distance = euclidean_coordinates.distance_between(
                current_mouse_location_E, item_position_E)

            if distance < drawer.selection_radius:
                possible_selections.append((index, distance))

        possible_selections = sorted(possible_selections,
                                     key=functools.cmp_to_key(distance_cmp))
        current_possible_selections = [x[0] for x in possible_selections]

        if len(current_possible_selections) > 0:
            selected_nodes.append(current_possible_selections[0])

        mouse_location = current_mouse_location_E
        update_status_label()
        redraw()

    elif current_mode == Mode.circle:
        add_circle_at(current_mouse_location_E)
    elif current_mode == Mode.mark:
        add_point_at(current_mouse_location_E)
    elif current_mode == Mode.polygon:
        global current_polygon

        if len(current_polygon) == 0:
            index1 = add_point_at(current_mouse_location_E)
            index2 = add_point_at(current_mouse_location_E)
            current_polygon.append(index1)
            current_polygon.append(index2)
            add_edge_between(index1, index2)
        elif len(current_polygon) > 0:
            index1 = current_polygon[-1]
            index2 = add_point_at(current_mouse_location_E)
            current_polygon.append(index2)
            add_edge_between(index1, index2)

        selected_nodes = current_polygon

        redraw()


def right_mouse_down(event):
    global current_mode

    if current_mode == Mode.polygon:
        global current_polygon
        current_polygon = []

        # After finishing a polygon, we save the current state to the history.
        save_current_state()


def shift_right_mouse_down(event):
    global current_mode

    if current_mode == Mode.polygon:
        global current_polygon

        if len(current_polygon) > 2:
            index1 = current_polygon[-1]
            index2 = current_polygon[0]
            add_edge_between(index1, index2)
        current_polygon = []

        # After closing a polygon, we save the current state to the history.
        save_current_state()


def mouse_up(event):
    global current_mode
    global mouse_location

    if current_mode == Mode.select:
        mouse_location = None
        current_possbile_selections = []
        redraw()
    elif current_mode == Mode.translate:
        # After we're done translating, we save the current state to the history.
        save_current_state()

        # When we're done translating we don't show any snapping lines anymore.
        global snapped_item_radial
        global snapped_item_angular
        snapped_item_radial = None
        snapped_item_angular = None
        redraw()


def shift_mouse_down(event):
    global current_mode
    global mouse_location
    global drawer

    if current_mode == Mode.select:
        global selected_nodes
        global current_possible_selections

        current_mouse_location_E = euclidean_coordinates.euclidean_coordinate(
            event.x, event.y)

        def distance_cmp(a, b):
            if a[1] > b[1]:
                return 1
            elif a[1] == b[1]:
                return 0
            else:
                return -1

        possible_selections = []

        for index, item in enumerate(drawer.items):
            position_E = drawer.canvas_point_from_hyperbolic_coordinate(
                item.coordinate_H)
            distance = euclidean_coordinates.distance_between(
                current_mouse_location_E, position_E)

            if distance < drawer.selection_radius:
                possible_selections.append((index, distance))

        possible_selections = sorted(possible_selections,
                                     key=functools.cmp_to_key(distance_cmp))

        current_possible_selections = [x[0] for x in possible_selections]

        # Selected nodes are about to change, we need to redraw them.
        redraw_selected_nodes()

        if len(current_possible_selections) > 0:
            index = current_possible_selections[0]

            # Remove the index if it is already in there
            if index in selected_nodes:
                selected_nodes.remove(index)

            # Add the index so it becomes the primary selection
            selected_nodes.append(index)

        mouse_location = current_mouse_location_E
        update_status_label()
        redraw()


def mouse_moved(event):
    global current_mode

    if not current_mode == Mode.polygon:
        return

    global current_polygon

    if len(current_polygon) == 0:
        return

    mouse_location_E = euclidean_coordinates.euclidean_coordinate(
        event.x, event.y)
    set_position_of_item_with_index(mouse_location_E, current_polygon[-1])

    status_text = "Polygon Points:\n"
    for polygon_point in current_polygon:
        polygon_point_H = drawer.items[polygon_point].coordinate_H

        status_text += "Point: (" + str("{:4.6f}".format(
            polygon_point_H.r)) + ", " + str("{:4.6f}".format(
                polygon_point_H.phi)) + ")\n"

    # Display the distance between the current and the last polygon
    # point.
    if len(current_polygon) > 1:
        current_item = drawer.items[current_polygon[-1]]
        current_H = current_item.coordinate_H

        previous_item = drawer.items[current_polygon[-2]]
        previous_H = previous_item.coordinate_H

        status_text += "Distance to previous: " + str("{:4.6f}".format(
            native_coordinates.distance_between(current_H, previous_H))) + "\n"

    # Since the status label flickers when its width changes often, we
    # artificially make it very wide by appending a long line.
    status_text += "-----------------------------------"

    set_status_label_text(status_text)


def mouse_dragged(event):
    global current_mode

    if current_mode == Mode.translate:
        mouse_location_E = euclidean_coordinates.euclidean_coordinate(
            event.x, event.y)
        translate_with_location(mouse_location_E)


# Updates the location of an item. If snap is enabled, will snap to possible
# radii or angles.
def set_position_of_item_with_index(location_E, item_index):

    # Used to set the final position (after potentially applying the snap.)
    def set_position_of_item_with_index__internal(coordinate_E, item_index):
        item = drawer.items[item_index]
        coordinate_H = drawer.hyperbolic_coordinate_from_canvas_point(
            coordinate_E)
        item.coordinate_H = coordinate_H
        drawer.mark_item_for_redraw(item)

        drawer.items[item_index] = item

        # If the item is part of an edge, the edge needs to be updated.
        for edge in drawer.edges:
            if edge.index1 == selected_nodes[
                    -1] or edge.index2 == selected_nodes[-1]:
                drawer.mark_edge_for_redraw(edge)

        redraw()

    if not is_snap_enabled:
        set_position_of_item_with_index__internal(location_E, item_index)
        return

    # If snap is enabled, we now look for possible snap targets.
    global snapped_item_radial
    global snapped_item_angular

    # At first we assume that the dragged item doesn't snap to anything.
    snapped_item_radial = None
    snapped_item_angular = None

    new_coordinate_E = location_E

    dragged_item_index = selected_nodes[-1]
    new_coordinate_H = drawer.hyperbolic_coordinate_from_canvas_point(
        new_coordinate_E)

    minimum_radial_distance = sys.float_info.max
    minimum_angular_distance = sys.float_info.max

    for index, item in enumerate(drawer.items):
        # We don't snap to the vertex that is currently being dragged.
        if index == dragged_item_index:
            continue

        other_coordinate_H = item.coordinate_H

        radial_distance = abs(other_coordinate_H.r - new_coordinate_H.r)
        angular_distance = new_coordinate_H.angular_distance_to(
            other_coordinate_H)

        if radial_distance < 0.5 and radial_distance < minimum_radial_distance:
            snapped_item_radial = index
            minimum_radial_distance = radial_distance
        elif angular_distance < 0.15:
            snapped_item_angular = index
            minimum_angular_distance = angular_distance

        # If we found something to snap to, we set the coordinates
        # of the current item to the snapped ones.
        if snapped_item_radial is not None:
            snapped_radial_coordinate_H = drawer.items[
                snapped_item_radial].coordinate_H
            new_coordinate_H.r = snapped_radial_coordinate_H.r
        if snapped_item_angular is not None:
            snapped_angular_coordinate_H = drawer.items[
                snapped_item_angular].coordinate_H
            new_coordinate_H.phi = snapped_angular_coordinate_H.phi

        new_coordinate_E = drawer.canvas_point_from_hyperbolic_coordinate(
            new_coordinate_H)

    set_position_of_item_with_index__internal(new_coordinate_E, item_index)


def translate_with_location(location_E):
    global selected_nodes
    global is_snap_enabled

    if len(selected_nodes) == 0:
        return

    # Update the location of the primary selection and snap to radii and
    # angles, if enabled.
    set_position_of_item_with_index(location_E, selected_nodes[-1])
    update_status_label()


def mouse_scrolled_with_delta(delta):
    global selected_nodes
    global current_circle_size

    # Updating the current_circle size when the mouse is scrolled
    current_circle_size += 0.1 * delta
    if current_circle_size < 0.1:
        current_circle_size = 0.1

    # However, if the user selected a circle and scrolled, we change the
    # current_circle_size to this circle's radius and update it afterwards
    for selected_node in selected_nodes:
        item = drawer.items[selected_node]
        if drawing.is_circle_item(item):
            current_circle_size = item.radius
            current_circle_size += 0.1 * delta

            if current_circle_size < 0.1:
                current_circle_size = 0.1

            item.radius = current_circle_size
            drawer.mark_item_for_redraw(item)
            drawer.items[selected_node] = item

        # We also adapt the radii of selected hypercycles
        for edge in drawer.edges:
            if edge.index1 == selected_node or edge.index2 == selected_node:
                if edge.hypercycle_radius > 0:
                    edge.hypercycle_radius = current_circle_size
                    drawer.mark_edge_for_redraw(edge)

    update_status_label()
    redraw()


def shift_mouse_scrolled_with_delta(delta):
    global selected_nodes

    radius_delta = 0.1 * delta

    center_E = euclidean_coordinates.euclidean_coordinate(
        canvas.winfo_width() / 2.0,
        canvas.winfo_height() / 2.0)

    for selected_node in selected_nodes:
        item = drawer.items[selected_node]
        coordinate_H = item.coordinate_H
        coordinate_H.r = max(coordinate_H.r + radius_delta, 0.0)
        item.coordinate_H = coordinate_H

        drawer.mark_item_for_redraw(item)
        drawer.items[selected_node] = item

        # If the item is part of an edge, the edge needs to be updated.
        for edge in drawer.edges:
            if edge.index1 == selected_node or edge.index2 == selected_node:
                drawer.mark_edge_for_redraw(edge)

    update_status_label()
    redraw()


def control_mouse_scrolled_with_delta(delta):
    global drawer

    drawer.scale = drawer.scale + 10 * delta
    drawer.scale = max(drawer.scale, 1.0)

    update_status_label()
    drawer.mark_all_items_for_redraw()
    redraw()


def mouse_scrolled(event):
    mouse_scrolled_with_delta(event.delta)


def mouse_scroll_up(event):
    mouse_scrolled_with_delta(1)


def mouse_scroll_down(event):
    mouse_scrolled_with_delta(-1)


def shift_mouse_scrolled(event):
    shift_mouse_scrolled_with_delta(event.delta)


def control_mouse_scrolled(event):
    control_mouse_scrolled_with_delta(event.delta)


def shift_mouse_scroll_up(event):
    shift_mouse_scrolled_with_delta(1)


def shift_mouse_scroll_down(event):
    shift_mouse_scrolled_with_delta(-1)


def control_mouse_scroll_up(event):
    control_mouse_scrolled_with_delta(1)


def control_mouse_scroll_down(event):
    control_mouse_scrolled_with_delta(-1)


# Deletes the selected items and possible edges between them.
def delete_items(items_to_delete):

    sorted_indices = sorted(items_to_delete)

    # Vertices will be deleted so the indices of the other vertices change.
    # Here we determine the map from the old indices to the new ones
    index_map = dict()
    current_new_index = 0
    for index in range(len(drawer.items)):
        if not index in sorted_indices:
            index_map[index] = current_new_index
            current_new_index += 1

    for node_to_remove in reversed(sorted_indices):
        edges_to_remove = []
        for index, edge in enumerate(drawer.edges):
            if edge.index1 == node_to_remove or edge.index2 == node_to_remove:
                edges_to_remove.append(index)

        for edge_index in reversed(sorted(edges_to_remove)):
            # Mark edge for redraw. (Will not actually be redrawn due to
            # deletion.)
            drawer.mark_edge_for_redraw(drawer.edges[edge_index])
            del drawer.edges[edge_index]

        # Mark item for redraw. (Will not actually be redrawn due to deletion.)
        drawer.mark_item_for_redraw(drawer.items[node_to_remove])
        del drawer.items[node_to_remove]

    for index, edge in enumerate(drawer.edges):
        for old_index, new_index in index_map.items():
            if edge.index1 == old_index:
                edge.index1 = new_index
            if edge.index2 == old_index:
                edge.index2 = new_index
            drawer.edges[index] = edge


# Keyboard Interaction
def delete_pressed(event):
    global selected_nodes

    # Precisely the selected nodes will be deleted. We need to "redraw" them.
    delete_items(selected_nodes)
    del selected_nodes[:]

    update_status_label()
    redraw()


def space_pressed(event):
    global current_mode
    global current_possible_selections
    global selected_nodes

    if current_mode == Mode.select:
        if len(selected_nodes) > 0 and len(current_possible_selections) > 0:
            primary_selection = selected_nodes[-1]

            if primary_selection in current_possible_selections:
                index = current_possible_selections.index(primary_selection)
                next_index = (index + 1) % len(current_possible_selections)
                next_item = current_possible_selections[next_index]
                if not next_item in selected_nodes:
                    selected_nodes[-1] = next_item

                update_status_label()
                redraw()


def escape_pressed(event):
    global selected_nodes
    global current_possible_selections
    global current_polygon

    redraw_selected_nodes()

    selected_nodes = []
    current_possible_selection = []

    # If escape is pressed, an we're in the middle of creating a polygon, we
    # consider this process to be canceled and delete the new polygon nodes.
    delete_items(current_polygon)
    current_polygon = []

    update_status_label()
    redraw()


def c_pressed(event):
    global selected_nodes
    for selected_node in selected_nodes:
        item = drawer.items[selected_node]
        selected_node_color_index = item.color
        selected_node_color_index += 1
        selected_node_color_index %= len(drawer.colors)
        item.color = selected_node_color_index
        drawer.items[selected_node] = item

        # The color of the item changed, we need to redraw it.
        drawer.mark_item_for_redraw(item)

        # Additionally, we need to redraw the edges associated with the item.
        for edge in drawer.edges:
            if edge.index1 == selected_node or edge.index2 == selected_nodes:
                drawer.mark_edge_for_redraw(edge)

    # After changing colors, we save the current state to the history.
    save_current_state()

    redraw()


def o_pressed(event):
    global current_circle_size
    global current_mode

    if not current_mode == Mode.circle:
        current_mode = Mode.circle
        update_mode_indicator()
        update_help_label()
    else:
        center_E = euclidean_coordinates.euclidean_coordinate(
            canvas.winfo_width() / 2.0,
            canvas.winfo_height() / 2.0)
        add_circle_at(center_E)


def p_pressed(event):
    set_mode_polygon()


def d_pressed(event):
    global items
    global edges
    global selected_nodes

    # Everything needs to be "redrawn"
    drawer.mark_all_items_for_redraw()

    drawer.items = []
    drawer.edges = []
    selected_nodes = []
    current_circle_size = 10.0
    drawer.grid_radius = 0.0
    drawer.regular_grid_depth = 0

    set_status_label_text("Cleared")
    redraw()


def e_pressed(event):
    global current_mode

    if not current_mode == Mode.select or current_mode == Mode.polygon:
        return

    global selected_nodes

    for i in range(0, len(selected_nodes)):
        for j in range(i + 1, len(selected_nodes)):
            selected_node1 = selected_nodes[i]
            selected_node2 = selected_nodes[j]
            add_edge_between(selected_node1, selected_node2)
    redraw()


def g_pressed(event):
    global current_circle_size

    if drawer.grid_radius > 0:
        drawer.grid_radius = 0
    else:
        drawer.grid_radius = current_circle_size

    drawer.mark_grid_for_redraw()
    redraw()


def capital_g_pressed(event):
    # If we already drew the graph, we remove the drawing now.
    if drawer.embedded_graph:
        drawer.mark_embedded_graph_for_redraw()
        drawer.embedded_graph = None
        redraw()
        return

    if len(sys.argv) <= 2:
        set_status_label_text(
            "No graph files provided. Launch Hipe with: python3 Hipe.py path/to/edgelist.txt path/to/embedding.txt"
        )
        return

    graph_file_name = sys.argv[1]
    embedding_file_name = sys.argv[2]

    # We're drawing adding the edges according to the
    # indices in the edge list.
    # If we already have items, we have to offset these
    # indices.
    index_offset = len(drawer.items)

    graph = embedded_graph.embedded_graph()

    with open(embedding_file_name, "rb") as embedding_file:
        lines = embedding_file.readlines()

        for line in lines:
            line = line.strip()
            line_components = line.split()
            if len(line_components) > 0:
                vertex = int(line_components[0])
                radius = float(line_components[1])
                angle = float(line_components[2])

                coordinate_H = native_coordinates.polar_coordinate(
                    radius, angle)
                graph.embedding[vertex] = coordinate_H

    with open(graph_file_name, "rb") as graph_file:
        lines = graph_file.readlines()

        for line in lines:
            line = line.strip()
            line_components = line.split()

            node1 = int(line_components[0]) + index_offset
            node2 = int(line_components[1]) + index_offset

            graph.graph.add_edge(node1, node2)

    drawer.embedded_graph = graph
    redraw()


def h_pressed(event):
    global current_mode

    if not current_mode == Mode.select or current_mode == Mode.polygon:
        return

    global selected_nodes
    global edges

    if len(selected_nodes) != 2:
        set_status_label_text("Select exactly 2 nodes to add a hypercycle!")
        return

    selected_node1 = selected_nodes[0]
    selected_node2 = selected_nodes[1]

    edge_index = -1
    for index, edge in enumerate(drawer.edges):
        if (edge.index1 == selected_node1 and edge.index2 == selected_node2
            ) or (edge.index2 == selected_node1
                  and edge.index1 == selected_node2):
            edge_index = index
            break

    if edge_index >= 0:
        # If the edge already had a hypercycle, we now remove it
        if edge.hypercycle_radius > 0:
            edge.hypercycle_radius = 0
            edge.hypercycle_points = None
        else:
            drawer.edges[edge_index].hypercycle_radius = current_circle_size
    else:
        edge = drawing.edge(selected_node1, selected_node2)
        edge.hypercycle_radius = current_circle_size
        drawer.edges.append(edge)

    # We have just changed the status of this edge. It needs to be marked
    # for redrawing.
    drawer.mark_edge_for_redraw(edge)
    redraw()


def m_pressed(event):
    set_mode_mark()


def r_pressed(event):
    global current_mode

    if not (current_mode == Mode.select or current_mode == Mode.translate):
        return

    global selected_nodes

    if len(selected_nodes) <= 1:
        return

    center_E = euclidean_coordinates.euclidean_coordinate(
        canvas.winfo_width() / 2.0,
        canvas.winfo_height() / 2.0)
    reference_point_H = drawer.items[selected_nodes[-1]].coordinate_H
    reference_radius = reference_point_H.r
    for i in range(0, len(selected_nodes)):
        item = drawer.items[selected_nodes[i]]
        item.coordinate_H.r = reference_radius

        drawer.mark_item_for_redraw(item)

        drawer.items[selected_nodes[i]] = item

        # If the item is part of an edge, the edge needs to be updated.
        for edge in drawer.edges:
            if edge.index1 == selected_nodes[
                    i] or edge.index2 == selected_nodes[i]:
                drawer.mark_edge_for_redraw(edge)

    # After adjusting circle sizes collectively, we save the current state to the history.
    save_current_state()

    update_status_label()
    redraw()


def capital_r_pressed(event):
    if drawer.regular_grid_depth > 0:
        drawer.regular_grid_depth = 0
    else:
        drawer.regular_grid_depth = 3

    drawer.mark_regular_grid_for_redraw()
    redraw()


def s_pressed(event):
    set_mode_select()


def t_pressed(event):
    set_mode_translate()


# Creating the GUI
root = Tk()
root.title("Hipe")
gui = gui.gui(root)
help_label = gui.help_label
status_label = gui.status_label

gui.select_button.configure(command=set_mode_select)
gui.translate_button.configure(command=set_mode_translate)
gui.mark_button.configure(command=set_mode_mark)
gui.circle_button.configure(command=set_mode_circle)
gui.polygon_button.configure(command=set_mode_polygon)

gui.snap_button.configure(command=toggle_snap)

gui.ipe_save_button.configure(command=save_as_ipe)
gui.svg_save_button.configure(command=save_as_svg)

# So we see the initial circle size
update_mode_indicator()
update_help_label()

canvas = gui.canvas

canvas.bind("<Configure>", resize)
canvas.bind("<Button-1>", mouse_down)
canvas.bind("<ButtonRelease-1>", mouse_up)
canvas.bind("<Shift-Button-1>", shift_mouse_down)
canvas.bind("<B1-Motion>", mouse_dragged)
canvas.bind("<Button-2>", right_mouse_down)
canvas.bind("<Shift-Button-2>", shift_right_mouse_down)
canvas.bind("<Button-3>", right_mouse_down)
canvas.bind("<Shift-Button-3>", shift_right_mouse_down)
canvas.bind("<Button-4>", mouse_scroll_up)
canvas.bind("<Button-5>", mouse_scroll_down)
canvas.bind("<Shift-Button-4>", shift_mouse_scroll_up)
canvas.bind("<Shift-Button-5>", shift_mouse_scroll_down)
canvas.bind("<Motion>", mouse_moved)
root.bind("<BackSpace>", delete_pressed)
root.bind("<space>", space_pressed)
root.bind("<Escape>", escape_pressed)
root.bind("<MouseWheel>", mouse_scrolled)
root.bind("<Shift-MouseWheel>", shift_mouse_scrolled)
root.bind("<Control-MouseWheel>", control_mouse_scrolled)
root.bind("c", c_pressed)
root.bind("d", d_pressed)
root.bind("e", e_pressed)
root.bind("g", g_pressed)
root.bind("G", capital_g_pressed)
root.bind("h", h_pressed)
root.bind("m", m_pressed)
root.bind("o", o_pressed)
root.bind("p", p_pressed)
root.bind("r", r_pressed)
root.bind("R", capital_r_pressed)
root.bind("s", s_pressed)
root.bind("t", t_pressed)
root.bind("+", mouse_scroll_up)
root.bind("-", mouse_scroll_down)
root.bind("*", shift_mouse_scroll_up)
root.bind("_", shift_mouse_scroll_down)
root.bind("<Up>", control_mouse_scroll_up)
root.bind("<Down>", control_mouse_scroll_down)
root.bind("Command-z", undo)
root.bind("Control-z", undo)
root.bind("z", undo)
root.bind("F1", toggle_snap)
root.bind("F2", toggle_snap)
root.bind("F3", toggle_snap)
root.bind("F4", toggle_snap)

# The actual drawer.
scale = 35.0
drawer = drawing.drawer(canvas, scale)

# The status_label needs to know about the drawer. Therefore, it is initialized
# after the drawer was set.
update_status_label()

# Graph Input:

while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass
