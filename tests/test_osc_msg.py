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


def test_concrete():
    """ Not sure what we'll use concretemsgs for, perhaps
    providing an external clock?
    """
    c = ConcreteMessage(b"/bums", (1, 2, "monk"))
    assert c.get_path(1.0)

def test_osc_client(s, e, oscmsg):
    """ Slightly ropey test, in that it spawns
    a server (oscmsg), dispatches a msg to it
    then waits a very small amount of time to see if it
    arrived. TBH if the msg *does* takes longer that
    100ms to arrive, then we have timing issues...
    """
    e.start()
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
    s.create_entity(Control, 0.0, 0.0, b"/bums")

    e.start()
    RUNTIME = 1.0
    time.sleep(RUNTIME)
    e.pause()
    # 1 second at 24fps
    # we might needs to +- 1 this on a loaded system?
    assert osccount["count"] == approx(1.0/CV_FRAME_TIME)

