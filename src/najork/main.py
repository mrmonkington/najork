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
from gi.repository import Gtk, Gio, GLib

import yaml

from .window import NajorkWindow
from .scene import Scene
from .engine_sched import Engine

from najork.config import settings

#logging.basicConfig(level=logging.DEBUG)

RENDER_FRAME_TIME = 1.0 / settings["clock_rate"] # let's do PAL for now

class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.verynoisy.najork',
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.connect("shutdown", self.on_quit)
        self.connect("open", self.app_open)
        self.scene = Scene()
        self.engine = Engine(self.scene, settings)
        self.window = None
        self.add_main_option(
            "debug",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Verbose output",
            None,
        )
        self.add_main_option(
            "start",
            ord("s"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Start engine immediately",
            None,
        )


        # self.add_main_option("lint", "l", str, "Lint input file, then exit", None)

    def on_quit(self, *args):
        self.engine.pause()
        self.engine.shutdown()
        self.quit()

    def do_activate(self):
        if not self.window:
            self.window = NajorkWindow(engine=self.engine, application=self)
        self.window.present()

#    def do_command_line(self, args):
#        Gtk.Application.do_command_line(self, args)
#        return 0
#        options = args.get_options_dict()
#        # convert GVariantDict -> GVariant -> dict
#        options = options.end().unpack()
#
#        if "test" in options:
#            # This is printed on the main instance
#            print("Test argument recieved: %s" % options["test"])
#
#        self.activate()
#        return 0

    def app_open(self, app, files, n_files, hint):
        import time
        logging.debug("Opening file")
        f = files[0]
        f.load_contents_async(None, self.load_file, None)
        self.activate()

    def load_file(self, source, result, user_data):
        success, content, nb = source.load_contents_finish(result)
        self.start_session(content)

    def start_session(self, content: str):
        self.engine.pause()
        self.engine.shutdown()
        scene_def: dict = yaml.load(content, Loader=yaml.Loader)
        self.scene = Scene()
        self.scene.load_from_dict(scene_def)
        self.engine = Engine(self.scene, settings)
        self.window.engine = self.engine
        if has_option("-s", "--start"):
            logging.debug("starting")
            self.engine.start()

def has_option(*options):
    return any(o in sys.argv for o in options)

def main(version):

    if has_option("-d", "--debug"):
        logging.basicConfig(level=logging.DEBUG)


    app = Application()
    return app.run(sys.argv)
