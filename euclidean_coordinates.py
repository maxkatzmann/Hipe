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

import math
import native_coordinates


class euclidean_coordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(x = " + str(self.x) + ", y = " + str(self.y) + ")"

    def to_native_coordinate_with_scale(self, scale):
        return native_coordinates.polar_coordinate(
            math.sqrt(self.x / scale * self.x / scale +
                      self.y / scale * self.y / scale),
            math.atan2(self.y / scale, self.x / scale) + math.pi)

    def to_native_coordinate(self):
        return self.to_native_coordinate_with_scale(1.0)


def coordinate_relative_to_coordinate(coord1, coord2):
    result = euclidean_coordinate(coord1.x - coord2.x, coord1.y - coord2.y)
    return result


def distance_between(coord1, coord2):
    difference = coordinate_relative_to_coordinate(coord1, coord2)
    return math.sqrt(difference.x * difference.x + difference.y * difference.y)
