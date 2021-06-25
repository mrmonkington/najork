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

import sys
import gi

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio

from .window import NajorkWindow

import threading

import logging
logging.basicConfig(level=logging.DEBUG)

FRAME_TIME = 1.0 / 24.0 # let's do PAL for now

class Engine:

    running = False
    state_lock = threading.Lock()

    def __init__(self):
        self.pos = 0.0
    
    def start(self):
        if self.running == False:
            self.t = threading.Timer(FRAME_TIME, self.tick)
            self.t.start()
            self.running = True

    def pause(self):
        if self.t.is_alive():
            self.t.cancel()
            self.running = False

    def rewind(self):
        with self.state_lock:
            self.pos = 0.0

    def tick(self):
        #logging.debug("Engine::Tick")
        with self.state_lock:
            self.pos += 0.01
            if self.pos > 1.0:
                self.pos = 0.0
        self.t = threading.Timer(FRAME_TIME, self.tick)
        self.t.start()
        
class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.verynoisy.najork',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("shutdown", self.on_quit)
        self.engine = Engine()

    def on_quit(self, *args):
        self.engine.pause()
        self.quit()

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = NajorkWindow(engine=self.engine, application=self)
        win.present()
        #self.engine.start()


def main(version):
    app = Application()
    return app.run(sys.argv)
