from najork.osc import ConcreteMessage, TemplatedMessage
import pytest
import asyncio
from oscpy.server import OSCThreadServer

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
from najork.config import DEFAULT_SETTINGS

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


def test_concrete():
    c = ConcreteMessage(b"/bums", (1, 2, "monk"))
    assert c.path

def test_osc_client(s, e, oscmsg):
    """ This is quite dodgy
    """
    e.send_osc_msg(b"/bums", (1, 2, b"monk"))
    time.sleep(0.1)
    assert oscmsg["path"] == b"/bums"
    assert oscmsg["values"] == (1, 2, b"monk")
