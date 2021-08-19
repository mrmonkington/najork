from najork.osc import ConcreteMessage, TemplatedMessage
import pytest
from pytest import approx

from oscpy.server import OSCThreadServer

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
from najork.config import DEFAULT_SETTINGS

from najork.entities import Control

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


def test_engine_static_messages(s, e, osccount):
    a1 = s.create_entity(Control, 0.0, 0.0, b"/bums")

    RUNTIME = 1.0
    time.sleep(RUNTIME)
    e.pause()
    t = e.pos
    # we want tick clock to match real elapsed time
    assert osccount["count"] == 24
"""
