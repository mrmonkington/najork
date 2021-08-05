"""
Define all entities used in our scene graph
See `../docs/modeling/classes.gaphor`
"""

from abc import ABC, abstractmethod
from shapely import geometry as geos

from .osc import *

XY = tuple[float, float]

BOUND_TOLERANCE = 5 # pixels

class ImpossibleGeometry(Exception):
    """ You tried to make a Line out of two circles, or
    something mad, or set a negative radius, I dunno"""


def XY_add(a, b):
    return (a[0]+b[0] + a[1]+b[1])


class Entity(ABC):
    """ Base for anything that can appear on the canvas
    """
    _uid: str = ""
    _rank: int = 0

    def __init__(self, uid: str, rank: int):
        self._uid = uid
        self._rank = rank # probably not needed

    # TODO: @abstractmethod
    def get_representation(self, t:float):
        """ Returns a shape to be rendered by view
        """

    @abstractmethod
    def get_bounds(self, t:float) -> tuple[XY, XY]:
        """ Returns a simplified shape suitable for picking
        """

class ShapelyProxy(ABC):
    @abstractmethod
    def get_impl(self) -> geos.base.BaseGeometry:
        """ Get a shapely version of whatever this is
        """

class ShapelyConcrete(ShapelyProxy):
    """ An invariant entity which can
    bake in its representation
    """
    _impl: geos.base.BaseGeometry = None
    def get_impl(self) -> geos.base.BaseGeometry:
        """ Returns actual internal repr
        """
        return self._impl

class Point(Entity):
    """Base class for any 1D item
    """

    @abstractmethod
    def get_coords(self, t:float) -> XY:
        """X then Y
        """

    def get_bounds(self, t:float):
        """Bounding box for a point is a smol square around it
        """
        x, y = self.get_coords(t)
        return ((x-BOUND_TOLERANCE, y-BOUND_TOLERANCE),
                (x+BOUND_TOLERANCE, y+BOUND_TOLERANCE))


class Anchor(Point, ShapelyConcrete):
    """Static point dependent on nothing else
    """
    # _impl: geos.Point = None

    def __init__(self, uid: str, rank: int, initial_position: XY):
        super().__init__(uid, rank)
        self.set_coords(initial_position)

    def set_coords(self, coords: XY):
        """ Set's initial (t=0) position
        """
        self._impl = geos.Point(coords)

    def get_coords(self, t:float) -> XY:
        """Anchors are invariant"""
        return (self._impl.x, self._impl.y)




class Intersection(Point):
    """ A point where two shapes cross

    Some shapes will have more than one intersection - we just
    keep it simple and take the first in an /undefined/ (TODO) order
    """


class Shape(Entity, ShapelyProxy):
    """ A 2D thing
    """

    def calc_procession_xy(self, length_fraction: float):
        impl = self.get_impl()
        l = impl.length
        segment = geos.substring(impl, l*length_fraction)
        return segment.coords[-1]


class Slider(Point):
    """
    """

    # what are we sliding along?
    _parent: Shape = None
    # initially, how far along it are we as a function of length?
    _procession: float = None
    # how fast along it are we moving in length per second units?

    def set_procession(self, proc: float):
        """ Set's initial (t=0) position along parent
        """
        self._procession = proc

    def get_coords(self, t:float) -> XY:
        """ Calculate coordinates of current position at time t
        using initial position and velocity
        """
        return self._parent.calc_procession_xy((self._procession + self._velocity * t) % 1.0)


class Line(Shape):
    """ A line *segment*
    """

    _parents: tuple[Point, Point] = None
    _impl: geos.LineString = None

    def __init__(self, uid:str, rank:int, endpoints: tuple[Point, Point]):
        if endpoints[0] == endpoints[1]:
            raise ImpossibleGeometry("Line endpoints are the same point")
        _parents = endpoints
        super().__init__(uid, rank)

    def get_impl(self, t: float):
        """ Make a shapely Line
            TODO - cache this!
        """
        return geos.LineString((self._parents[0].get_coords(t), self._parents[1].get_coords(t)))


class PolyLine(Shape):
    """_parents: tuple[Point, Point]
    _impl: geos.LineString
    """


class Circle(Shape):
    """_centre: Point = None
    _radius: float = 0.0
    _impl: geos.LineString
    """

class Roller(Circle):
    """ I can't remember how this works
    Always write your ideas down immediately and fully
    """
    _rolling_surface: Shape = None
    _rolling_ang_vel: float = 0.0


class Measurement(ABC):
    """ A value computed from some property of other entites
    """
    @abstractmethod
    def get_value(self, t: float):
        """ What is this measurement's concrete value at time t?
        """


class Angle(Measurement):
    """_parents: tuple[Line, Line]
    """

class Distance(Measurement):
    """_parents: tuple[Point, Point]
    """

class Port:
    """inputs: dict[str, Measurement] = None
    """

class Bumper(Slider, Port):
    """An OSC 'event' emitting slider
    """
    _collision_parent: Shape = None
    _msg: TemplatedOSCMessage = None

    def __init__(self, parent: Shape, collides_with: Shape):
        if parent == collides_with:
            raise ImpossibleGeometry("Bumper cannot collide with its own parent")
        self._collision_parent = collides_with

    def get_bounds(self, t:float) -> tuple[XY, XY]:
        return ((self.x-BOUND_TOLERANCE, self.y-BOUND_TOLERANCE),
                (self.x+BOUND_TOLERANCE, self.y+BOUND_TOLERANCE))


class Control(Entity):
    x: float = 0.0
    y: float = 0.0

    def __init__(self, uid: str, x: float, y: float, msg: TemplatedOSCMessage):
        super().__init__(uid, rank)

    def get_representation(self, t:float):
        """ Returns a shape to be rendered by view
        """
        # some sort of point

    def get_bounds(self, t:float) -> tuple[XY, XY]:
        return ((self.x-BOUND_TOLERANCE, self.y-BOUND_TOLERANCE),
                (self.x+BOUND_TOLERANCE, self.y+BOUND_TOLERANCE))


