import pytest

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
import logging
import time

@pytest.fixture
def s():
    return Scene()

def test_engine_timing(caplog, s):
    e = Engine(s)
    e.start()
    RUNTIME = 1.0
    time.sleep(RUNTIME)
    e.pause()
    t = e.pos
    e.shutdown()
    # we want tick clock to match real elapsed time
    assert t == pytest.approx(RUNTIME, abs=1E-6)
