from najork.osc import ConcreteMessage, TemplatedMessage
import pytest
from pytest import approx

from oscpy.server import OSCThreadServer

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
from najork.config import DEFAULT_SETTINGS

from najork.entities import (
    Anchor, Line, Slider, Circle, Intersection, Distance,
    Angle, Control, Bumper
)

import time


"""
def test_concrete():
    c = ConcreteMessage(b"/bums", (1, 2, "monk"))
    assert c.get_path(1.0)


def test_osc_client(s, e, oscmsg):
    e.send_osc_msg(b"/bums", (1, 2, b"monk"))
    time.sleep(0.1)
    assert oscmsg["path"] == b"/bums"
    assert oscmsg["values"] == (1, 2, b"monk")


def test_expr():
    def bindings(t: float):
        return {"in_1": t+2.0}
    c = TemplatedMessage(b"/bums", ("in_1 + 1.0 + t", "\"monk\""), bindings)
    d = c.get_data(1.0)
    assert d == approx((5.0, "monk"))

"""

def test_engine_bumps(s, e, oscmsg):
    p1 = s.create_entity(Anchor, (0.0, 0.0))
    p2 = s.create_entity(Anchor, (1.0, 0.0))
    l1 = s.create_entity(Line, (p1, p2))

    p3 = s.create_entity(Anchor, (0.5, 1.0))
    p4 = s.create_entity(Anchor, (0.5, -1.0))

    l2 = s.create_entity(Line, (p3, p4))

    b1 = s.create_entity(
        Bumper,
        l1, 0.0, 1.0,
        l2, b"/bump",
        loop=False, inherit_velocity=False
    )

    b1.msg.set_data([
        "1",
    ])

    e.start()
    RUNTIME = 1.0
    time.sleep(RUNTIME)
    e.pause()
    t = e.pos
    # shoulda got a bump
    assert t == approx(RUNTIME)
    assert oscmsg["path"] == b"/bump"
    assert oscmsg["values"] == (1,)
