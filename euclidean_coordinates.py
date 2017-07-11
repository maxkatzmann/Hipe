import math
import native_coordinates

class EuclideanCoordinate(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(x = " + str(self.x) + ", y = " + str(self.y) + ")"

    def to_native_coordinate_with_scale(self, scale):
        return native_coordinates.PolarCoordinate(\
        math.sqrt(self.x / scale * self.x / scale + self.y / scale * self.y / scale), \
        math.atan2(self.y / scale, self.x / scale))

    def to_native_coordinate(self):
        return to_native_coordinate_with_scale(1.0)

def coordinate_relative_to_coordinate(coord1, coord2):
    result = EuclideanCoordinate(coord1.x - coord2.x, coord1.y - coord2.y)
    return result

def distance_between(coord1, coord2):
    difference = coordinate_relative_to_coordinate(coord1, coord2)
    return math.sqrt(difference.x * difference.x + difference.y * difference.y)
