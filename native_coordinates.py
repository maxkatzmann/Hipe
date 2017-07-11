import math
import euclidean_coordinates

# Polar Coordinates
class PolarCoordinate:
    def __init__(self, r, phi):
        self.r = r
        self.phi = phi

    def __str__(self):
        return "(r = " + str(self.r) + ", phi = " + str(self.phi) + ")"

    def to_euclidean_coordinate_with_scale(self, scale):
        return euclidean_coordinates.EuclideanCoordinate(\
        self.r * math.cos(self.phi) * scale, \
        self.r * math.sin(self.phi) * scale)

    def to_euclidean_coordinate(self):
        return to_euclidean_coordinate_with_scale(1.0)

def coordinate_rotated_around_origin_by_angle(coordinate, angle):
    if coordinate.r == 0:
        return coordinate

    result = PolarCoordinate(coordinate.r, coordinate.phi)
    result.phi = math.fmod(coordinate.phi + angle, 2.0 * math.pi)

    while result.phi < 0.0:
        result.phi = 2.0 * math.pi + result.phi

    return result

def distance_between(coord1, coord2):
    delta_phi = math.pi - math.fabs(math.pi - math.fabs(coord1.phi - coord2.phi))
    return math.acosh(\
    math.cosh(coord1.r) * math.cosh(coord2.r) \
    - math.sinh(coord1.r) * math.sinh(coord2.r) * math.cos(delta_phi));

def coordinate_mirrored_on_x_axis(coordinate):
    return PolarCoordinate(coordinate.r, -(coordinate.phi - (2.0 * math.pi)))

def coordinate_translated_along_x_axis_by_hyperbolic_distance(coordinate, distance):
    if coordinate.phi != math.pi:
        original_point = PolarCoordinate(0.0, 0.0)
        original_point.r = coordinate.r
        original_point.phi = coordinate.phi

        reference_point = PolarCoordinate(0.0, 0.0)
        if distance > 0.0:
            reference_point.r = math.fabs(distance)
            reference_point.phi = math.pi
        elif distance < 0.0:
            reference_point.r = math.fabs(distance)
            reference_point.phi = 0.0
        else:
            return coordinate

        if original_point.phi > math.pi:
            coordinate = coordinate_mirrored_on_x_axis(coordinate)

        radial_coordinate = distance_between(coordinate, reference_point)

        enumerator = (math.cosh(math.fabs(distance)) * math.cosh(radial_coordinate) \
                - math.cosh(coordinate.r))
        denominator = (math.sinh(math.fabs(distance)) * math.sinh(radial_coordinate))

        try:
            angular_coordinate = math.acos(enumerator / denominator)
            if distance < 0.0:
                angular_coordinate = math.pi - angular_coordinate

        except ValueError:
                angular_coordinate = 0.0

        translated_coordinate = PolarCoordinate(radial_coordinate, angular_coordinate);
        if original_point.phi > math.pi:
            translated_coordinate = coordinate_mirrored_on_x_axis(translated_coordinate)

        return translated_coordinate

    else:
        newAngle = 0.0;
        newRadius = 0.0;

        if distance < 0.0:
            newAngle = math.pi
            newRadius = coordinate.r - distance
        else:
            if distance > coordinate.r:
                newAngle = 0.0;
                newRadius = distance - coordinate.r
            else:
                newAngle = math.pi
                newRadius = coordinate.r - distance

        return PolarCoordinate(newRadius, newAngle);
