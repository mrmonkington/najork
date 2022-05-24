# scene_view.py
#
# Copyright 2022 Mark Kennedy
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

from .scene import Scene

class SceneView():
    """
        Presents a Scene with zoom, etc
    """
    def __init__(self, scene: Scene):
        self.scene: Scene = scene

    def pick(self, x: int, y: int):
        found: bool
        el: Entity|None
        found, el = self.engine.get_scene().pick(x, y)
        if found:
            # something under pick point
            # highlight_object()
            pass
        else:
            # clear highlight
            pass

    def draw(self, 

