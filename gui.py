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

import tkinter as tk
from tkinter import *

class gui:

    def toggle_help(self):
        self.help_is_shown = not self.help_is_shown
        self.show_help_label(self.help_is_shown)

    def show_help_label(self, show):
        if show:
            self.help_label.pack(side = BOTTOM, anchor = W)
        else:
            self.help_label.pack_forget()

    def __init__(self, root):
        self.root = root
        self.entry = tk.Entry(root)
        stvar = tk.StringVar()
        stvar.set("one")

        self.menu_color = "blue"

        frame = Frame(self.root, bg = "white")
        frame.pack(side = TOP, anchor = W)

        self.select_button = Button(frame, text = "[S]elect")
        self.select_button.grid(row = 0, column = 0, sticky = W)

        self.translate_button = Button(frame, text = "[T]ranslate")
        self.translate_button.grid(row = 0, column = 1, sticky = W)

        self.mark_button = Button(frame, text = "[M]ark")
        self.mark_button.grid(row = 0, column = 2, sticky = W)

        self.circle_button = Button(frame, text = "[O]Circle")
        self.circle_button.grid(row = 0, column = 3, sticky = W)

        self.polygon_button = Button(frame, text = "[P]olygon")
        self.polygon_button.grid(row = 0, column = 4, sticky = W)

        highlight_text = "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"

        self.select_label = Label(frame,
                                  text = highlight_text,
                                  foreground = self.menu_color,
                                  background = self.menu_color,
                                  font = "Helvetica 1 bold italic")
        self.select_label.grid(row = 1, column = 0)

        self.translate_label = Label(frame,
                                     text = highlight_text,
                                     foreground = self.menu_color,
                                     background = self.menu_color,
                                     font = "Helvetica 1 bold italic")
        self.translate_label.grid(row = 1, column = 1)

        self.mark_label = Label(frame,
                                text = highlight_text,
                                foreground = self.menu_color,
                                background = self.menu_color,
                                font = "Helvetica 1 bold italic")
        self.mark_label.grid(row = 1, column = 2)

        self.circle_label = Label(frame,
                                  text = highlight_text,
                                  foreground = self.menu_color,
                                  background = self.menu_color,
                                  font = "Helvetica 1 bold italic")
        self.circle_label.grid(row = 1, column = 3)

        self.polygon_label = Label(frame,
                                  text = highlight_text,
                                  foreground = self.menu_color,
                                  background = self.menu_color,
                                  font = "Helvetica 1 bold italic")
        self.polygon_label.grid(row = 1, column = 4)

        Label(frame,
              text = " | ",
              foreground = "black",
              background = "white").grid(row = 0,
                                         column = 5)

        self.snap_button = Button(frame, text = "[F1-4] Snap: Off")
        self.snap_button.grid(row = 0, column = 6)

        Label(frame,
              text = " | ",
              foreground = "black",
              background = "white").grid(row = 0,
                                         column = 7)

        self.ipe_save_button = Button(frame, text = "Save as Ipe")
        self.ipe_save_button.grid(row = 0, column = 8, sticky = E)

        self.svg_save_button = Button(frame, text = "Save as SVG")
        self.svg_save_button.grid(row = 0, column = 9, sticky = E)

        Label(frame,
              text = " | ",
              foreground = "black",
              background = "white").grid(row = 0,
                                         column = 10)

        self.help_button = Button(frame, text = "?",
                                  command = self.toggle_help)
        self.help_button.grid(row = 0, column = 11, sticky = E)

        self.canvas = tk.Canvas(root,
                                width = 800,
                                height = 600,
                                background = "white")
        self.canvas.pack(fill = BOTH, expand = YES)

        self.help_label = Label(self.canvas,
                                text = "",
                                bg = "white",
                                justify = LEFT)

        self.help_is_shown = False

        self.status_label = Label(self.canvas,
                                  text = "",
                                  bg = "white",
                                  justify = LEFT)
        self.status_label.pack(side = TOP, anchor = W)
