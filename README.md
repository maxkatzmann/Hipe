# Hipe

Hipe is a Python tool that visualizes drawings in hyperbolic space using the
native representation.  Its controls are inspired by
[Ipe](https://github.com/otfried/ipe).

![Screenshot](screenshot.png)

## Installation

1. Make sure you have Python 3 installed
1. Install [Tk](http://www.tkdocs.com/tutorial/install.html) if not installed
   already.
1. Install the latest version of [NetworkX](https://networkx.github.io).
1. Download the code from this repository.

## Usage

Launch the tool by calling `python3 Hipe.py`

## Controls

Different ways of manipulating the drawing is split into different modes.  A red
bar beneath the corresponding button indicates which mode you are in.  Each mode
can be activated by either pressing the corresponding button or by pressing the
key in square brackets.

### Select

The select mode is used to select objects and manipulate the selection.  The
shortcut key is `s`.  The primary selection (red) is the last object selected.
Secondary selections are marked purple.

* `Mouse 1`: Selects the object within the selection radius (indicated by a
  magenta circle) that is closest to the mouse cursor.
* `Shift Mouse 1`: Adds to the selection.
* `Space`: Pressing space while pressing the mouse button down cycles through
  the objects within the selection radius.  If the object is a circle it will be
  highlighted in magenta.
* `e`: Adds/removes an edge between two selected objects.
* `r`: Sets the radii of all selected objects to match the radius of the primary
  selection.
* `h`: If exactly two nodes are selected, adds/removes the hypercycle with the
  current radius around the corresponding edge.

### Translate

The translate mode is used to translate the primary selection.  The shortcut key
is `t`.

* `Mouse Drag`: Moves the primary selection to the current cursor position.
  Upon further dragging the object follows the mouse cursor.

### Mark

The mark mode is used to add points to the canvas.  The shortcut key is `m`.

* `Mouse 1`: Add a point at the current cursor position..

### Circle

The circle mode is used to add circles to the canvas.  The shortcut key is `o`.
A newly added circle will have the `current circle radius`, which can be
adjusted using the mouse wheel or the `+` / `-` keys.

* `Mouse 1`: Add a point at the current cursor position.

### Polygon

The polygon mode is used to create polygons, i.e., points (marks) that
are connected by edges, to the canvas.  The shortcut key is `p`.

* `Mouse 1`: Adds a point at the current cursor position.  And another point at
  the same position that will now follow the mouse cursor.
* `Mouse 2`: Places the point currently following the mouse without closing the
  polygon.
* `Shift Mouse 2`: Places the point currently following the mouse and closes the
  polygon.

### Other Controls

These actions are available in all modes:

* `g`: Add/remove a grid within a circle of the `current circle radius` centered
  at the origin.
* `G`: Add/remove the embedded graph that was passed as input parameter.
* `R`: Add/remove a regular grid
* `c`: Change the color of selected objects by cycling through `[Black, Green,
  Red, Blue and Orange]`
* `d`: Clear all, i.e., remove all objects.
* `z / Ctrl-z`: Undo.
* `Mouse wheel` / `+` / `-`: Change the `current circle radius`.
* `Shift mouse wheel` / `*` / `_`: Change the radial coordinate of selected
  objects.
* `Control mouse wheel` / `Up` / `Down`: Change the scale.
* `Backspace`: Delete the currently selected objects.
* `Escape`: Clear selection.

### Snapping

Snapping helps you in matching the radii or angular coordinates of other objects
while translating an object.  By default snapping is turned off.  It can be
turned on, by pressing the Snap button or the keys `F1`, `F2`, `F3` or `F4`.

![Snapping Demo](snapping_demo.gif)

## Drawing an embedded Graph

Hipe allows you to pass a graph together with an embedding as input parameters
which can then be drawn in the app, by pressing `G`.  For example

    python3 Hipe.py path/to/edge_list.txt path/to/coordinates.txt

Where `edge_list.txt` denotes the edge list of a graph (i.e. each line
represents one edge, consisting of two nodes) and in `coordinates.txt` each
line assigns a polar coordinate to a node in the format

    node_label radius angle_in_radians

## Notes

* The blue point at the center represents the origin of the hyperbolic plane
* Trying to add an edge between two already connected points will delete the
  edge between them
* An edge between items of the same color will also have this color
* When saving a drawing as Ipe or SVG a folder called `output` will be created
  where Hipe was launched. The drawing will be saved as SVG or Ipe file using
  the current timestamp as filename.
* The undo functionality is pretty rough.  Sometimes Hipe adds some intermediate
  steps when drawing, which means you might have to undo multiple times until
  certain actions are actually undone.
* The snapping performance is not good at the moment, which is why the feature
  is turned off by default.  Just enabled it shortly when you want to snap
  something. ;)

## Known Issues

* Tk does not seem to recognize mouse scroll events in macOS High Sierra or
  later.
