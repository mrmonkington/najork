"""
Define all entities used in our scene graph.
See `../docs/modeling/classes.gaphor`

Our units of distance are effetively pixels, since these map quite
reasonably well to MIDI/OSC controller resolution (0-127). A scene
at 100% zoom should show plenty of elements and the overall structure.

The geometry engine is Shapely and so:
    - We can take advantage of intersections and modifiers, such as buffer
    - We can create segments and interpolate along any construction
    - We cannot model curves exactly (e.g. circles) and everything is a
      polyline
    - It's pretty fast

We model any construction in a deterministic and closed form fashion. Thus
`t` (time) is passed to most methods. I've avoided using any sort of
context-based techniques since frequently we'll need the model at `t_n` and
`t_n+1` in order to find collisions, etc, and context (fancy globals!) just
makes this nightmare to unpick, merely for the sake of a little terseness.

TODO probably Numpy all of this.
"""

from abc import ABC, abstractmethod
from shapely import geometry as geos
from shapely import ops as geops

from .osc import TemplatedOSCMessage
from math import atan2, degrees

XY = tuple[float, float]

# pixels
BOUND_TOLERANCE = 5

# number of segments used to model a quarter circle
# when buffering points or
# chamfering edges
CIRCLE_RES = 16


def clamp(v: float, m=0.0, M=1.0) -> float:
    """ CLAMP
    do do do, do do do, do dodo do do
    CLAMP
    """
    return min(max(m, v), M)


def angle(line: geos.LineString) -> float:
    """ Computer angle of line
    """
    s = line.coords[0]
    e = line.coords[-1]
    dy = e.y - s.y
    dx = e.x - s.x

    return degrees(atan2(dy, dx))


class ImpossibleGeometry(Exception):
    """ You tried to make a Line out of two circles, or
    something mad, or set a negative radius, I dunno"""


def XY_add(a: XY, b: XY) -> XY:
    return (a[0]+b[0] + a[1]+b[1])


class Entity(ABC):
    """ Base for anything that can appear on the canvas
    """
    _uid: str = ""
    _rank: int = 0

    def __init__(self, uid: str, rank: int):
        self._uid = uid
        self.set_rank(rank)

    def set_rank(self, rank: int):
        """ Set validated rank
        """
        for d in self.get_dependencies():
            if d.get_rank() >= rank:
                raise ImpossibleGeometry("Entities must have rank greater than"
                                         " all childrens' ranks")
        self._rank = rank

    def get_rank(self) -> int:
        return self._rank

    # TODO: @abstractmethod
    def get_representation(self, t: float):
        """ Returns a shape to be rendered by view
        """

    @abstractmethod
    def get_bounds(self, t: float) -> tuple[XY, XY]:
        """ Returns a simplified shape suitable for picking
        """

    def get_dependencies(self) -> list['Entity']:
        """ Returns list of other entities this one depends on
        """
        return ()

class ShapelyProxy(ABC):
    @abstractmethod
    def get_impl(self, t: float) -> geos.base.BaseGeometry:
        """ Get a shapely version of whatever this is
        """

    def get_bounds(self, t: float) -> tuple[XY, XY]:
        """ Re-chunk shapely's bounds method
        """
        mx, my, Mx, My = self.get_impl(t).bounds
        return ((mx,my), (Mx, My))


class ShapelyConcrete(ShapelyProxy):
    """ An invariant entity which can
    bake in its representation
    """
    _impl: geos.base.BaseGeometry = None

    def get_impl(self, t: float) -> geos.base.BaseGeometry:
        """ Returns actual internal repr. `t` is discarded since we
            assume the representation does not change with time
        """
        return self._impl


class Point(Entity):
    """Base class for any 1D item
    """

    @abstractmethod
    def get_coords(self, t: float) -> XY:
        """X then Y
        """

    def get_bounds(self, t: float):
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
        self.set_coords(initial_position)
        super().__init__(uid, rank)

    def set_coords(self, coords: XY):
        """ Set's initial (t=0) position
        """
        self._impl = geos.Point(coords)

    def get_coords(self, t: float) -> XY:
        """Anchors are invariant"""
        return (self._impl.x, self._impl.y)


# Mixin must come first as it implements an abstract method Entity::get_bounds
# see 
class Shape(ShapelyProxy, Entity):
    """ A 2D thing
    """

    def calc_procession_xy(self, t: float, length_fraction: float):
        """ Find coords of a point located on the shape perimeter, at some
            proportion of perimiter length measured from 'zero'
        """
        p = self.get_impl(t).interpolate(clamp(length_fraction), normalized=True).coords
        return p[0]

    @property
    def start(self):
        """ Get the root, or start of this shape
        """
        return self.calc_procession_xy(1.0, 0.0)


class Intersection(Point):
    """ A point where two shapes cross

    Some shapes will have more than one intersection - we just
    keep it simple and take the first in an /undefined/ (TODO) order

    If two shapes are wholly or partially congruent, shapely may produce
    a substring as one of the intersections. Let's consider this a
    non-intersection.

    Where there is no intersection, return the first coord of first shape.
    """
    def __init__(self, uid: str, rank: int, parents: list[Shape]):
        if len(parents) != 2:
            raise ImpossibleGeometry(
                "Trying to build Intersection of {} shapes".format(len(parents)))
        self._parents = parents
        """ Which two shapes are we intersecting? """
        super().__init__(uid, rank)

    def get_dependencies(self) -> list[Entity]:
        return self._parents

    def get_coords(self, t: float) -> XY:
        if self._parents[0].get_impl(t).crosses(self._parents[1].get_impl(t)):
            imp = self._parents[0].get_impl(t).intersection(self._parents[1].get_impl(t))
            return (imp.x, imp.y)
        else:
            return self._parents[0].start.get_coords(t)


class Slider(Point):
    """ A point attached to a parent shape, which has a position
    defined as a fraction of the total length of the parent shape
    and has a 
    """

    # what are we sliding along?
    _parent: Shape = None
    # initially, how far along it are we as a function of length?
    _procession: float = None
    # how fast along it are we moving in length per second units?
    _velocity: float = None

    def __init__(self, uid: str, rank: int, parent: Shape, procession: float,
                 velocity: float, loop: bool = False):
        self._parent = parent
        self.set_procession(procession) 
        self.set_velocity(velocity) 
        self.set_loop(loop) 
        # what are we sliding along?
        super().__init__(uid, rank)

    def set_procession(self, proc: float):
        """ Sets initial (t=0) position along parent.

        If > 1.0 will clamp
        """
        self._procession = clamp(proc, 0.0, 1.0)

    def set_velocity(self, velocity: float):
        """ Sets velocity in length/s units e.g. 0.1 = 1/10 of total
        parent length per second
        """
        self._velocity = velocity

    def set_loop(self, loop: bool):
        self._loop = loop

    def get_coords(self, t: float) -> XY:
        """ Calculate coordinates of current position at time t
        using initial position and velocity. (Wraps)
        """
        # TODO accuracy implication from wrapping?
        if self._loop:
            return self._parent.calc_procession_xy(t,
                (self._procession + self._velocity * t) % 1.0)
        else:
            return self._parent.calc_procession_xy(t,
                clamp(self._procession + self._velocity * t))

    def get_dependencies(self) -> list[Entity]:
        """ Returns list of other entities this one depends on
        """
        return [self._parent, ]

    def get_bounds(self, t: float) -> tuple[XY, XY]:
        x, y = self.get_coords(t)
        return ((x-BOUND_TOLERANCE, y-BOUND_TOLERANCE),
                (x+BOUND_TOLERANCE, y+BOUND_TOLERANCE))


class Line(Shape):
    """ A line *segment*
    """

    _parents: tuple[Point, Point] = None
    _impl: geos.LineString = None

    def __init__(self, uid:str, rank:int, endpoints: tuple[Point, Point]):
        if endpoints[0] == endpoints[1]:
            raise ImpossibleGeometry("Line endpoints are the same point")
        self._parents = endpoints
        super().__init__(uid, rank)

    def get_impl(self, t: float):
        """ Make a shapely Line
            TODO - cache this!
        """
        return geos.LineString((self._parents[0].get_coords(t),
                                self._parents[1].get_coords(t)))

    @property
    def start(self):
        # optimised for lines
        return self._parents[0]


class PolyLine(Shape):
    """_parents: tuple[Point, Point]
    _impl: geos.LineString
    """


class Circle(Shape):
    """ An approxiation of a circle with CIRCLE_RES * 4 segments.

    The 'zero' point on a circle is 0 angle on a traditional graph, hence the
    east or rightmost point.
    """
    def __init__(self, uid: str, rank: int, centre: Point, radius: float,
                 orientation: float):
        """ A circle may have its default orientation defined as some
        proportion of one total revolution. (We don't deal in angles or radians
        as they are not intuitively useful for use of these as 'bars' of
        repeating events.
        """
        if radius <= 0.0:
            raise ImpossibleGeometry("Circles must have positive radius")
        self._centre: Point = centre
        self._radius: float = radius
        self._orientation: float = clamp(orientation, 0.0, 1.0)
        super().__init__(uid, rank)

    def get_impl(self, t: float):
        return self._centre.get_impl(t).buffer(self._radius,
                                               resolution=CIRCLE_RES).exterior

    def calc_procession_xy(self, t: float, length_fraction: float):
        """ Find coords of a point located on the shape perimeter, at some
            proportion of perimiter length measured from 'zero'
        """
        p = self.get_impl(t).interpolate(
                (length_fraction + self._orientation) % 1.0,
                normalized=True
            ).coords
        return p[0]

    def get_dependencies(self) -> list['Entity']:
        """ Returns list of other entities this one depends on
        """
        return [self._centre, ]



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
    def get_value(self, t: float) -> float:
        """ What is this measurement's concrete value at time t?
        """


class Angle(Measurement):
    def __init__(self, guid: str, rank: int, parents: tuple[Line, Line]):
        if len(parents) != 2:
            raise ImpossibleGeometry("Angles can only be measured between"
                                     "two Lines")
        self._parents = parents
        super().__init__(guid, rank)

    def get_dependencies(self) -> list['Entity']:
        """ Returns list of other entities this one depends on
        """
        return self._parents

    def get_value(self, t: float):
        """ Shapely doesn't have an angle measuring method!
        """
        return (angle(self._parents[1].get_impl(t))
                - angle(self._parents[2].get_impl(t)))


class Distance(Measurement):
    """_parents: tuple[Point, Point]
    """

    def __init__(self, guid: str, rank: int, parents: tuple[Point, Point]):
        if len(parents) != 2:
            raise ImpossibleGeometry("Distance can only be measured between"
                                     "two Points")
        self._parents = parents
        super().__init__(guid, rank)

    def get_dependencies(self) -> list['Entity']:
        """ Returns list of other entities this one depends on
        """
        return self._parents

    def get_value(self, t: float):
        return self._parents[0].get_impl(t).distance(
            self._parents[1].get_impl(t))


class Port:
    """inputs: dict[str, Measurement] = None
    """


class Bumper(Slider, Port):
    """An OSC 'event' emitting slider
    """
    _collision_parent: Shape = None
    _msg: TemplatedOSCMessage = None

    def __init__(self, uid: str, rank: int, parent: Shape, procession: float,
                 velocity: float, collides_with: Shape, loop: bool = False):
        if parent == collides_with:
            raise ImpossibleGeometry("Bumper cannot collide with its own "
                                     "parent")
        self._collision_parent = collides_with
        super().__init__(uid, rank, parent, procession, velocity, loop)

    def test_collision(self, t: float, t_next: float) -> bool:
        """ Does this slider collide with its collision parent
        during the next time slice `t` -> `t_next`?

        A collision is defined as passing from one side of a line to the other
        or moving from within a form to without
        """
        # calculate trajectory of point
        traj: geos.LineString = geos.LineString((self.get_coords(t),
                                                 self.get_coords(t_next)))
        # does it cross?
        if traj.crosses(self._collision_parent.get_impl()):
            return True
        return False

    def get_dependencies(self) -> list['Entity']:
        """ Returns list of other entities this one depends on
        """
        return [self._parent, self._collision_parent]


class Control(Entity):

    def __init__(self, uid: str, rank: int, x: float, y: float,
                 msg: TemplatedOSCMessage):
        # x and y are purely presentational
        self._x = x
        self._y = y
        self._msg = msg
        super().__init__(uid, rank)

    def get_representation(self, t: float):
        """ Returns a shape to be rendered by view
        """
        # some sort of point

    def get_bounds(self, t: float) -> tuple[XY, XY]:
        return ((self._x-BOUND_TOLERANCE, self._y-BOUND_TOLERANCE),
                (self._x+BOUND_TOLERANCE, self._y+BOUND_TOLERANCE))


