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

import euclidean_coordinates
import native_coordinates
import math
import drawing

class printer:

    def __init__(self, drawer):
        self.drawer = drawer

    def print_ipe(self, items, edges, selected_nodes):

        print("<?xml version=\"1.0\"?>\n" +\
              "<!DOCTYPE ipe SYSTEM \"ipe.dtd\">\n" +\
              "<ipe version=\"70206\" creator=\"Ipe 7.2.7\">\n" +\
              "<info created=\"D:20170719160807\" modified=\"D:20170719160807\"/>\n" +\
              "<ipestyle name=\"basic\">\n" +\
              "</ipestyle>\n" +\
              "<page>\n" +\
              "<layer name=\"alpha\"/>\n" +\
              "<view layers=\"alpha\" active=\"alpha\"/>\n")

        self.drawer.draw_with_functions(items,
                                        edges,
                                        selected_nodes,
                                        None,
                                        self.print_ipe_path,
                                        self.print_ipe_circle)

        print("</page>\n" +\
              "</ipe>")

    def print_ipe_circle(self, center, radius, start_angle, end_angle, is_clockwise, fill_color, border_color, width):
        if len(fill_color) > 0:
            print("<path stroke=\"" + str(fill_color) + "\" fill=\"" + str(fill_color) + "\"> " + str(radius) + " 0 0 " + str(radius) + " " + str(center.x) + " " + str(center.y) + " e </path>")
        else:
            print("<path stroke=\"" + str(border_color) + "\"> " + str(radius) + " 0 0 " + str(radius) + " " + str(center.x) + " " + str(center.y) + " e </path>")

    def print_ipe_path(self, points, is_closed, color, width):
        print("<path stroke=\"" + color + "\">")
        if len(points) > 0:
            print(str(points[0].x) + " " + str(points[0].y) + " m")
        for index in range(1, len(points)):
            print(str(points[index].x) + " " + str(points[index].y) + " l")

        if is_closed:
            print("h")
        print("</path>")

    ### SVG ###

    def print_svg(self, items, edges, selected_nodes):
        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE svg PUBLIC " +\
              "\"-//W3C//DTD SVG 1.1//EN\" " +\
              "\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n\n<svg " +\
              "xmlns=\"http://www.w3.org/2000/svg\"\nxmlns:xlink=\"http://" +\
              "www.w3.org/1999/xlink\" " +\
              "xmlns:ev=\"http://www.w3.org/2001/xml-events\"\nversion=\"1.1\" " +\
              "baseProfile=\"full\"\nwidth=\"" + str(self.drawer.canvas.winfo_width()) + "\" height=\"" + str(self.drawer.canvas.winfo_height()) + "\">\n\n")

        self.drawer.draw_with_functions(items,
                                        edges,
                                        selected_nodes,
                                        None,
                                        self.print_svg_path,
                                        self.print_svg_circle)

        print("\n</svg>\n")

    def print_svg_circle(self, center, radius, start_angle, end_angle, is_clockwise, fill_color, border_color, width):
        if len(fill_color) > 0:
            print("<circle cx=\"" + str(center.x) + "\" cy=\"" + str(center.y) + "\" r=\"" + str(radius) + "\" fill=\"" + str(fill_color) + "\" stroke=\"" + str(border_color) + "\" stroke-width=\"" + str(width) + "\"/>\n")
        else:
            print("<circle cx=\"" + str(center.x) + "\" cy=\"" + str(center.y) + "\" r=\"" + str(radius) + "\" fill=\"none\" stroke=\"" + str(border_color) + "\" stroke-width=\"" + str(width) + "\"/>\n")

    def print_svg_path(self, points, is_closed, color, width):
        path_string = "<path d =\""

        if len(points) > 0:
            path_string += "M " + str(points[0].x) + "," + str(points[0].y) + " "

            print(len(points))
            for index in range(1, len(points)):
                path_string += "L " + str(points[index].x) + "," + str(points[index].y) + " "
        if is_closed:
            path_string += "Z"

        path_string += "\" stroke = \"" + color + "\" stroke-width = \"" + str(width) + "\" fill=\"none\"/>"
        print(path_string)
