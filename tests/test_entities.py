import pytest
import logging

from najork.entities import *

def test_anchor():
    p = Anchor("p1",1,(0.0, 0.0))
    assert p.get_coords(0.0) == (0.0, 0.0)
