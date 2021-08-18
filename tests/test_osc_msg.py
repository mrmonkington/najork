from najork.osc import ConcreteMessage, TemplatedMessage
import pytest
from pytest import approx
import asyncio
from oscpy.server import OSCThreadServer

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
from najork.config import DEFAULT_SETTINGS

from najork.entities import Control

import time

@pytest.fixture
def s():
    return Scene()

@pytest.fixture
def e(s):
    eng = Engine(s, DEFAULT_SETTINGS)
    eng.start()
    yield eng
    eng.shutdown()


@pytest.fixture
def oscmsg():
    """ A little OSC server that can listen for anything
    and will be able to report the last message received
    """

    msg = {}
    msg["values"] = []

    def callback(address, *values):
        nonlocal msg
        msg["path"] = address
        msg["values"] = values

    osc = OSCThreadServer(default_handler=callback)

    osc.listen(address=DEFAULT_SETTINGS["osc"]["ip"],
               port=DEFAULT_SETTINGS["osc"]["port"],
               default=True)

    yield msg
    osc.stop()

@pytest.fixture
def osccount():
    """ A little OSC server that can listen for anything
    and will be able to report the number of messages received
    """

    msg = {}
    msg["path"] = ""
    msg["values"] = []
    msg["count"] = 0

    def callback(address, *values):
        nonlocal msg
        msg["path"] = address
        msg["values"] = values
        msg["count"] += 1
        print(address, *values)

    osc = OSCThreadServer(default_handler=callback)

    osc.listen(address=DEFAULT_SETTINGS["osc"]["ip"],
               port=DEFAULT_SETTINGS["osc"]["port"],
               default=True)

    yield msg
    osc.stop()


def test_concrete():
    c = ConcreteMessage(b"/bums", (1, 2, "monk"))
    assert c.get_path(1.0)

def test_osc_client(s, e, oscmsg):
    """ This is quite dodgy
    """
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

