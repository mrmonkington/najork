# main.py
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

import logging

import sys
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

from .window import NajorkWindow
from .scene import Scene
from .engine_sched import Engine

from najork.config import DEFAULT_SETTINGS

logging.basicConfig(level=logging.DEBUG)

RENDER_FRAME_TIME = 1.0 / 24.0 # let's do PAL for now

class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.verynoisy.najork',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("shutdown", self.on_quit)
        self.scene = Scene()
        self.engine = Engine(self.scene, DEFAULT_SETTINGS)
        self.window = None

    def on_quit(self, *args):
        self.engine.pause()
        self.engine.shutdown()
        self.quit()

    def do_activate(self):
        if not self.window:
            self.window = NajorkWindow(engine=self.engine, application=self)
        self.window.present()
        #self.engine.start()


def main(version):
    app = Application()
    return app.run(sys.argv)
