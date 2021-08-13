import pytest

from najork.engine_sched import Engine, CV_FRAME_TIME
from najork.scene import Scene
from najork.config import DEFAULT_SETTINGS
import logging
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

def test_engine_timing(e):
    RUNTIME = 1.0
    time.sleep(RUNTIME)
    e.pause()
    t = e.pos
    # we want tick clock to match real elapsed time
    assert t == pytest.approx(RUNTIME, abs=1E-6)
