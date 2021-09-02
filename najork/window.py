# window.py
#
# Copyright 2021 Mark Kennedy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '4.0')
gi.require_foreign('cairo')

from gi.repository import Gtk, GLib

import cairo
import logging

from .renderer import render

@Gtk.Template(filename='najork/window.ui')
class NajorkWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'NajorkWindow'

    main_canvas = Gtk.Template.Child('main_canvas')
    play_button = Gtk.Template.Child('play_button')
    rewind_button = Gtk.Template.Child('rewind_button')

    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.main_canvas.add_tick_callback(self.tick)
        self.main_canvas.set_draw_func(self.draw_scene, {}, None)
        self.play_button.connect("clicked", self.on_playpause)
        self.rewind_button.connect("clicked", self.on_rewind)

    def tick(self, widg, frame_clock, **kwargs):
        #print("tick %i" % (frame_clock.get_frame_time(),))
        #self.testDraw(widg, frame_clock)
        if self.engine.running:
            widg.queue_draw()
        return GLib.SOURCE_CONTINUE

    def draw_scene(self, da, ctx, width, height, *args):
        logging.debug("Width %i, height %i", width, height)
        # TODO get scene bounds
        da.set_content_width(1920)
        da.set_content_height(1280)
        render(self.engine.get_scene(), self.engine.pos, ctx)
        #ctx.scale(width, height)
        #ctx.set_source_rgb(0.0, 0.0, 0.0)
        #ctx.set_line_width(0.1)
        #ctx.move_to(0.0+self.engine.pos, 0)
        #ctx.line_to(1.0-self.engine.pos, 1)
        #ctx.stroke()

    def on_playpause(self, widg, *args):
        logging.debug("Active? %s", widg.get_active())
        if widg.get_active() == True:
            self.engine.start()
            widg.set_icon_name("media-playback-pause-symbolic")
        else:
            self.engine.pause()
            widg.set_icon_name("media-playback-start-symbolic")

    def on_rewind(self, widg, *args):
        self.engine.rewind()
