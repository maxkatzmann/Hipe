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
import euclidean_coordinates
import collections

sampled_hypercycle = collections.namedtuple("sampled_hypercycle", ["upper_samples", "lower_samples"])

# Polar Coordinates
class polar_coordinate:
    def __init__(self, r, phi):
        self.r = r
        self.phi = phi

    def __str__(self):
        return "(r = " + str(self.r) + ", phi = " + str(self.phi) + ")"

    def to_euclidean_coordinate_with_scale(self, scale):
        return euclidean_coordinates.euclidean_coordinate(\
        self.r * math.cos(self.phi) * scale, \
        self.r * math.sin(self.phi) * scale)

    def to_euclidean_coordinate(self):
        return to_euclidean_coordinate_with_scale(1.0)

def coordinate_rotated_around_origin_by_angle(coordinate, angle):
    if coordinate.r == 0:
        return coordinate

    result = polar_coordinate(coordinate.r, coordinate.phi)
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
    return polar_coordinate(coordinate.r, -(coordinate.phi - (2.0 * math.pi)))

def coordinate_translated_along_x_axis_by_hyperbolic_distance(coordinate, distance):
    if coordinate.phi != math.pi:
        original_point = polar_coordinate(0.0, 0.0)
        original_point.r = coordinate.r
        original_point.phi = coordinate.phi

        reference_point = polar_coordinate(0.0, 0.0)
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

        translated_coordinate = polar_coordinate(radial_coordinate, angular_coordinate);
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

        return polar_coordinate(newRadius, newAngle);

def render_points_for_line_from_to(point1, point2):

    render_detail = 100
    if point1.r == 0 or point2.r == 0:
        return [point1, point2]
    else:
        angular_distance = point2.phi - point1.phi
        if (angular_distance > 0.0 and angular_distance < math.pi) or angular_distance < -math.pi:
            temp = point1
            point1 = point2
            point2 = temp

        distance = distance_between(point1, point2)

        cos_gamma_2 = 0.0
        try:
            cos_gamma_2 = (((math.cosh(point2.r) * math.cosh(distance)) - math.cosh(point1.r)) / (math.sinh(point2.r) * math.sinh(distance)))
        except (ZeroDivisionError, ValueError):
            pass

        line_points = []
        for i in range(0, render_detail):
            partial_distance = distance * (i / float(render_detail))
            r = 0.0
            try:
                r = math.acosh((math.cosh(point2.r) * math.cosh(partial_distance) - (math.sinh(point2.r) * math.sinh(partial_distance) * cos_gamma_2)))
            except (ZeroDivisionError, ValueError):
                pass
            gamma_prime = 0.0
            try:
                gamma_prime = math.acos(((math.cosh(r) * math.cosh(point2.r)) - math.cosh(partial_distance)) / (math.sinh(r) * math.sinh(point2.r)))
            except (ZeroDivisionError, ValueError):
                pass

            phi = point2.phi + gamma_prime
            native_line_point = polar_coordinate(r, phi)

            line_points.append(native_line_point)
        return line_points


def render_points_for_circle_with_center_and_radius(center, radius, scale):
    render_detail = 360
    render_detail_half = render_detail / 2

    additional_render_detail = math.floor(center.r * center.r)
    render_detail_factor = 0

    if center.r > 0:
        render_detail_factor = min(1.0, 0.75 * scale / (center.r * center.r))
    angular_point_distance = 2.0 * math.pi / render_detail

    circle_points = []
    for i in range(render_detail):
        native_circle_point = polar_coordinate(radius, i * angular_point_distance)
        circle_points.append(native_circle_point)

        if i == render_detail_half:
            for j in range(additional_render_detail):
                native_circle_point = polar_coordinate(radius, \
                i * angular_point_distance + j * (render_detail_factor * angular_point_distance / additional_render_detail))
                circle_points.append(native_circle_point)
        elif i == render_detail_half - 1:
            for j in range(additional_render_detail):
                native_circle_point = polar_coordinate(radius, \
                (i + (1.0 - render_detail_factor)) * angular_point_distance + j * (render_detail_factor * angular_point_distance / additional_render_detail))
                circle_points.append(native_circle_point)
        elif abs(i - render_detail_half) <= 7 * render_detail_factor - 4:
            for j in range(math.floor(additional_render_detail * render_detail_factor * render_detail_factor)):
                native_circle_point = polar_coordinate(radius, \
                i * angular_point_distance + j * (angular_point_distance / (additional_render_detail * render_detail_factor * render_detail_factor)))
                circle_points.append(native_circle_point)

    for i in range(len(circle_points)):
        native_circle_point = circle_points[i]
        translated_point = coordinate_translated_along_x_axis_by_hyperbolic_distance(native_circle_point, center.r)
        rotated_point = coordinate_rotated_around_origin_by_angle(translated_point, center.phi)
        circle_points[i] = rotated_point

    return circle_points

def render_points_for_hypercycle_around_points(point1, point2, radius):
    # Rotate the points such that the first lies on the x-axis We don't
    # actually move the first point, as we can infer everything we know from
    # its current position.
    rotation_angle1 = -point1.phi
    rotated_point2 = coordinate_rotated_around_origin_by_angle(point2, rotation_angle1)

    # Rotate the points such that the first lies on the origin
    translation_distance = -point1.r
    translated_point2 = coordinate_translated_along_x_axis_by_hyperbolic_distance(rotated_point2, translation_distance)

    # Rotate everything such that the second points is on the x-axis.
    # We don't actually perform the rotation (as it is not necessary).
    rotation_angle2 = -translated_point2.phi

    # The first point is now on the origin, the second points is on the x-axis.
    # Now we sample the points for the two lines representing the hypercycle.
    render_detail = 100

    # The reference point is the one that is translated along the x-axis to get
    # the sampling points.
    reference_point = polar_coordinate(radius, math.pi / 2.0)

    upper_sample_points = []
    lower_sample_points = []

    for i in range(render_detail):
        current_x = translated_point2.r / render_detail
        upper_sample_point = coordinte_translated_along_x_axis_by_hyperbolic_distance(reference_point, current_x)
        upper_sample_points.append(sample_point)
        lower_sample_point = polar_coordinate(upper_sample_point.r,
                                              2.0 * math.pi - upper_sample_point.phi)
        lower_sample_points.append(lower_sample_point)

    return sampled_hypercycle(upper_samples = upper_sample_points,
                              lower_samples = lower_sample_points)
