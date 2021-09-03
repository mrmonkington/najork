import cairo
import logging
import math

from .scene import Scene
from .entities import (
    Entity, Anchor, Line, Slider, Circle, Intersection,
    Distance, Angle, Control, Bumper
)

from .engine_sched import CV_FRAME_TIME

POINT_SIZE = 10

# rgbeegees
THEME = {
    Anchor: (0.5, 0.5, 0.5),
    Slider: (1.0, 232/255, 17/255),
    Circle: (233/255, 45/255, 0.0),
    Line: (233/255, 45/255, 0.0),
    Control: (1.0, 127/255, 42/255),
    Distance: (15/255, 171/255, 0.0),
    Bumper: (17/255, 162/255, 1.0),
}

def render(scn: Scene, t: float, ctx):
    ctx.scale(1.0, 1.0)
    ctx.set_source_rgb(0.0, 0.0, 0.0)

    for e in scn.sort_by_rank():
        render_entity(e, t, ctx)

def render_entity(e, t: float, ctx):
    """ Build a scene from dict `scene_def` parsed from YAML
    (order something else, we don't care)
    angle
    x circle
    x distance
    x bumper
    x slider
    intersection
    x line
    x anchor
    polyline
    x control
    roller
    """

    if type(e) is Anchor:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(0.0)
        x, y = e.get_repr(t)
        ctx.move_to(x, y)
        ctx.arc(x, y, POINT_SIZE, 0, 2 * math.pi)
        ctx.close_path()
        ctx.fill()

    elif type(e) is Slider:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(0.0)
        x, y = e.get_repr(t)
        ctx.move_to(x, y)
        ctx.arc(x, y, POINT_SIZE, 0, 2 * math.pi)
        ctx.close_path()
        ctx.fill()

    elif type(e) is Control:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(1.0)
        x, y, inps = e.get_repr(t)
        # little pentagon
        stops = [(x+10*math.cos(s), y+10*math.sin(s))
                 for s in (math.pi * (-0.5 + 2/5 * s)
                           for s in range(0, 5))]
        ctx.move_to(*stops[0])
        for stop in stops[1:]:
            ctx.line_to(stop[0], stop[1])
        ctx.close_path()
        ctx.stroke()

        for inp in inps:
            ctx.move_to(x, y)
            ctx.set_dash((5, 5))
            ctx.line_to(inp[0], inp[1])
            ctx.set_dash((5,))
            ctx.stroke()
            ctx.set_dash(())

    elif type(e) is Bumper:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(1.0)
        x, y, inps = e.get_repr(t)
        # little star
        stops = [(x+(5 * (s%2+1))*math.cos(r), y+(5 * (s%2+1))*math.sin(r))
                 for r, s in ((math.pi * (-0.5 + 2/10 * s), s)
                              for s in range(0, 10))]

        ctx.move_to(*stops[0])
        for stop in stops[1:]:
            ctx.line_to(stop[0], stop[1])
        ctx.close_path()
        if e.test_collision(t, t+CV_FRAME_TIME):
            ctx.fill()
        else:
            ctx.stroke()

        for inp in inps:
            ctx.move_to(x, y)
            ctx.set_dash((5, 5))
            ctx.line_to(inp[0], inp[1])
            ctx.set_dash((5,))
            ctx.stroke()
            ctx.set_dash(())

    elif type(e) is Circle:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(2.0)
        x, y, r = e.get_repr(t)
        #ctx.move_to(x, y)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.close_path()
        ctx.stroke()

    elif type(e) is Line:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(2.0)
        x1, y1, x2, y2 = e.get_repr(t)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    elif type(e) is Distance:
        ctx.set_source_rgb(*THEME[type(e)])
        ctx.set_line_width(1.0)
        xm, ym, x1, y1, x2, y2 = e.get_repr(t)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()
        # little triangle
        ctx.set_line_width(0.0)
        stops = [(xm+10*math.cos(s), ym+10*math.sin(s))
                 for s in (math.pi * (-0.5 + 2/3 * s)
                           for s in range(0, 3))]
        ctx.move_to(*stops[0])
        for stop in stops[1:]:
            ctx.line_to(stop[0], stop[1])
        ctx.close_path()
        ctx.fill()

    else:
        pass

