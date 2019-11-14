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

# Polar Coordinates


class polar_coordinate:
    def __init__(self, r, phi):
        self.r = r
        self.phi = phi

    def __str__(self):
        return "(r = " + str(self.r) + ", phi = " + str(self.phi) + ")"

    def to_euclidean_coordinate_with_scale(self, scale):
        return euclidean_coordinates.euclidean_coordinate(
            self.r * math.cos(self.phi) * scale,
            self.r * math.sin(self.phi) * scale)

    def to_euclidean_coordinate(self):
        return to_euclidean_coordinate_with_scale(1.0)

    def angular_distance_to(self, other):
        return math.pi - abs(math.pi - abs(self.phi - other.phi))


def coordinate_rotated_around_origin_by_angle(coordinate, angle):
    if coordinate.r == 0:
        return coordinate

    result = polar_coordinate(coordinate.r, coordinate.phi)
    result.phi = math.fmod(coordinate.phi + angle, 2.0 * math.pi)

    while result.phi < 0.0:
        result.phi = 2.0 * math.pi + result.phi

    return result


def distance_between(coord1, coord2):
    delta_phi = math.pi - \
        math.fabs(math.pi - math.fabs(coord1.phi - coord2.phi))
    try:
        return math.acosh(
            math.cosh(coord1.r) * math.cosh(coord2.r) -
            math.sinh(coord1.r) * math.sinh(coord2.r) * math.cos(delta_phi))
    except ValueError:
        return 0


def coordinate_mirrored_on_x_axis(coordinate):
    return polar_coordinate(coordinate.r, -(coordinate.phi - (2.0 * math.pi)))


def coordinate_translated_along_x_axis_by_hyperbolic_distance(
        coordinate, distance):
    if coordinate.phi != math.pi:
        original_point = polar_coordinate(0.0, 0.0)
        original_point.r = coordinate.r
        original_point.phi = coordinate.phi

        reference_point = polar_coordinate(0.0, 0.0)
        reference_point.r = math.fabs(distance)
        if distance > 0.0:
            reference_point.phi = math.pi
        elif distance < 0.0:
            reference_point.phi = 0.0
        else:
            return coordinate

        if original_point.phi > math.pi:
            coordinate = coordinate_mirrored_on_x_axis(coordinate)

        radial_coordinate = distance_between(coordinate, reference_point)

        if radial_coordinate == 0.0:
            return polar_coordinate(0.0, 0.0)

        enumerator = (
            math.cosh(math.fabs(distance)) * math.cosh(radial_coordinate) -
            math.cosh(coordinate.r))
        denominator = (math.sinh(math.fabs(distance)) *
                       math.sinh(radial_coordinate))

        try:
            angular_coordinate = math.acos(enumerator / denominator)
            if distance < 0.0:
                angular_coordinate = math.pi - angular_coordinate

        except ValueError:
            angular_coordinate = 0.0

        translated_coordinate = polar_coordinate(radial_coordinate,
                                                 angular_coordinate)
        if original_point.phi > math.pi:
            translated_coordinate = coordinate_mirrored_on_x_axis(
                translated_coordinate)

        return translated_coordinate

    else:
        newAngle = 0.0
        newRadius = math.fabs(coordinate.r + distance)

        if distance < 0.0:
            if fabs(distance) > coordinate.r:
                newAngle = math.pi
                newRadius = coordinate.r - distance
            else:
                newAngle = 0.0
        else:
            if distance > coordinate.r:
                newAngle = 0.0
                newRadius = distance - coordinate.r
            else:
                newAngle = math.pi
                newRadius = coordinate.r - distance

        return polar_coordinate(newRadius, newAngle)


def render_points_for_line_from_to(point1, point2):

    render_detail = 100
    if point1.r == 0 or point2.r == 0 or point1.phi == point2.phi:
        return [point1, point2]

    angular_distance = point2.phi - point1.phi
    if (angular_distance > 0.0
            and angular_distance < math.pi) or angular_distance < -math.pi:
        temp = point1
        point1 = point2
        point2 = temp

    distance = distance_between(point1, point2)

    cos_gamma_2 = 0.0
    try:
        cos_gamma_2 = (((math.cosh(point2.r) * math.cosh(distance)) -
                        math.cosh(point1.r)) /
                       (math.sinh(point2.r) * math.sinh(distance)))
    except (ZeroDivisionError, ValueError):
        pass

    line_points = []
    for i in range(0, render_detail):
        partial_distance = distance * (i / float(render_detail))
        r = 0.0
        try:
            r = math.acosh((math.cosh(point2.r) * math.cosh(partial_distance) -
                            (math.sinh(point2.r) *
                             math.sinh(partial_distance) * cos_gamma_2)))
        except (ZeroDivisionError, ValueError):
            pass
        gamma_prime = 0.0
        try:
            gamma_prime = math.acos(((math.cosh(r) * math.cosh(point2.r)) -
                                     math.cosh(partial_distance)) /
                                    (math.sinh(r) * math.sinh(point2.r)))
        except (ZeroDivisionError, ValueError):
            pass

        phi = point2.phi + gamma_prime
        native_line_point = polar_coordinate(r, phi)

        line_points.append(native_line_point)

    line_points.append(point1)
    return line_points


def render_points_for_circle_with_center_and_radius(center, radius):
    render_detail = 200

    # If the circle is centered at the origin, we simply draw a euclidean
    # circle.
    if center.r == 0.0:

        render_detail = 360
        circle_points = []
        step_size = (2.0 * math.pi) / render_detail

        angle = 0.0
        while angle < (2.0 * math.pi):
            point = polar_coordinate(radius, angle)
            circle_points.append(point)
            angle = angle + step_size

        return circle_points

    # We first determine the points by pretending the node itself had angular
    # coordinate 0.

    r_min = max((radius - center.r), (center.r - radius))
    r_max = center.r + radius

    step_size = (r_max - r_min) / render_detail

    circle_points = []

    # We start computing the render points at the max radius towards the center
    # of the disk, then copy and mirror all points on the x-axis.
    r = r_max
    theta = 0

    additional_render_detail_threshold = 5.0 * step_size
    additional_render_detail = render_detail / 5

    while r >= r_min:
        try:
            theta = math.acos(
                (math.cosh(center.r) * math.cosh(r) - math.cosh(radius)) /
                (math.sinh(center.r) * math.sinh(r)))
        except ValueError:
            pass

        point = polar_coordinate(r, theta)
        circle_points.append(point)

        # Additional render detail
        if r >= r_min and r - r_min < additional_render_detail_threshold:
            additional_step_size = step_size / additional_render_detail

            additional_r = r - additional_step_size

            while additional_r > r - step_size:

                try:
                    theta = math.acos(
                        (math.cosh(center.r) * math.cosh(additional_r) -
                         math.cosh(radius)) /
                        (math.sinh(center.r) * math.sinh(additional_r)))
                except ValueError:
                    pass

                if additional_r >= r_min:
                    additional_point = polar_coordinate(additional_r, theta)
                    circle_points.append(additional_point)

                additional_r = additional_r - additional_step_size

        r = r - step_size

    # Add the point on the ray through the origin and center. Depending on
    # whether the origin is contained in the circle the angle of this points is
    # either pi or 0.
    inner_point_angle = math.pi
    if center.r > radius:
        inner_point_angle = 0.0

    inner_point = polar_coordinate(r_min, inner_point_angle)
    circle_points.append(inner_point)

    # Now we copy all points by mirroring them on the x-axis. We exclude the
    # first and the last point, as they are lying on the x-axis. To obtain a
    # valid path we need walk from the end of the vector to the start.
    i = len(circle_points) - 2  # We don't need to add the inner point twice.
    while i > 0:

        native_circle_point = circle_points[i]
        mirrored_point = polar_coordinate(
            native_circle_point.r, (2.0 * math.pi) - native_circle_point.phi)
        circle_points.append(mirrored_point)
        i = i - 1

    # Finally we rotate all points around the origin to match the angular
    # coordinate of the circle center.
    for i in range(len(circle_points)):
        native_circle_point = circle_points[i]
        rotated_point = coordinate_rotated_around_origin_by_angle(
            native_circle_point, center.phi)
        circle_points[i] = rotated_point

    return circle_points


def render_points_for_hypercycle_around_points(point1, point2, radius):

    # Rotate the points such that the first lies on the x-axis We don't
    # actually move the first point, as we can infer everything we know from
    # its current position.
    rotation_angle1 = -point1.phi
    rotated_point2 = coordinate_rotated_around_origin_by_angle(
        point2, rotation_angle1)

    # Translate the points such that the first lies on the origin
    translation_distance = -point1.r
    translated_point2 = coordinate_translated_along_x_axis_by_hyperbolic_distance(
        rotated_point2, translation_distance)

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
        current_x = i * (translated_point2.r / render_detail)
        upper_sample_point = coordinate_translated_along_x_axis_by_hyperbolic_distance(
            reference_point, current_x)
        upper_sample_points.append(upper_sample_point)
        lower_sample_point = polar_coordinate(
            upper_sample_point.r, 2.0 * math.pi - upper_sample_point.phi)
        lower_sample_points.append(lower_sample_point)

    # Now we need to reverse the translations made earlier.
    for index in range(len(upper_sample_points)):
        upper_sample_point = upper_sample_points[index]
        lower_sample_point = lower_sample_points[index]

        rotated_upper = coordinate_rotated_around_origin_by_angle(
            upper_sample_point, -rotation_angle2)
        rotated_lower = coordinate_rotated_around_origin_by_angle(
            lower_sample_point, -rotation_angle2)

        translated_upper = coordinate_translated_along_x_axis_by_hyperbolic_distance(
            rotated_upper, -translation_distance)
        translated_lower = coordinate_translated_along_x_axis_by_hyperbolic_distance(
            rotated_lower, -translation_distance)

        final_upper = coordinate_rotated_around_origin_by_angle(
            translated_upper, -rotation_angle1)
        final_lower = coordinate_rotated_around_origin_by_angle(
            translated_lower, -rotation_angle1)

        upper_sample_points[index] = final_upper
        lower_sample_points[index] = final_lower

    return upper_sample_points, lower_sample_points
