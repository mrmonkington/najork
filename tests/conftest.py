import pytest

from oscpy.server import OSCThreadServer

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
from najork.config import DEFAULT_SETTINGS


@pytest.fixture
def s():
    """ Default, empty scene
    """
    return Scene()


@pytest.fixture
def e(s):
    """ Default engine
    """
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
