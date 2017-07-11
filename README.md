## HyperVis

HyperVis is a Python tool that visualizes circles in hyperbolic space using its
native representation.

# Installation
1. Make sure you have Python 3 installed
1. Install [Tk](http://www.tkdocs.com/tutorial/install.html) if not installed already.
1. Download the code from this repository.

# Usage
Launch the tool by calling `python3 HyperVis.py`

# Controls
* `Right Click` adds a circle centered at the current location of the mouse
* `Left Click` on a point selects the point and the circle that it is centered in
* `Mouse Drag` moves the circle on the plane
* `BackSpace` deletes a selected point
* `Mouse Wheel` changes the size of the selected circle
* `C` cycles through the colors of the selected circle `[Black, Green, Red, Blue, Orange and Magenta]`

# Notes
* The blue point at the center represents the origin of the hyperbolic plane
* New circles are black and have the same size as the last circle that was edited

# Known Issues
* Tk does not seem to recognize mouse scroll events in macOS High Sierra

# Screenshot
![Screenshot](screenshot.png)
