# import pytest
from pytest import approx
import logging

from najork.entities import (
    Anchor, Line, Slider, Circle, Intersection, Distance,
    Angle
)

from najork.scene import Scene

import pytest


@pytest.fixture
def s():
    return Scene()


def test_sequence(s):
    assert s.get_next_id("anchor") == "000001"
    assert s.get_next_id("slider") == "000001"
    assert s.get_next_id("anchor") == "000002"
    assert s.get_next_id("slider") == "000002"
    assert s.get_next_id("anchor") == "000003"
    assert s.get_next_id("anchor") == "000004"


def test_entity_factory(s):
    a = Anchor("anchor-000001", 1, (0.0, 0.0))
    b = s.create_entity(Anchor, (0.0, 0.0))
    c = s.create_entity(Anchor, (0.0, 0.0))
    assert a._rank == b._rank
    assert a._uid == b._uid
    assert a.get_coords(0.0) == b.get_coords(0.0)
    assert a._rank == c._rank
    assert a._uid != c._uid
    assert a.get_coords(0.0) == b.get_coords(0.0)


def test_entity_factory_2rank(s):
    a1 = s.create_entity(Anchor, (0.0, 0.0))
    a2 = s.create_entity(Anchor, (1.0, 1.0))
    l1 = s.create_entity(Line, (a1, a2))
    assert a1.rank == 1
    assert a2.rank == 1
    assert l1.rank == 2

def load_yaml(f):
    import yaml
    with open("tests/input/{}".format(f)) as inp:
        return yaml.load(inp.read(), Loader=yaml.Loader)

@pytest.fixture
def y1():
    return load_yaml("simple_1.yml")

@pytest.fixture
def y2():
    return load_yaml("simple_2.yml")

@pytest.fixture
def yb1():
    return load_yaml("big_1.yml")

def test_load_from_yaml_1(s, y1):
    s.load_from_dict(y1)
    assert len(s._registry) == 1

def test_load_from_yaml_2(s, y2):
    s.load_from_dict(y2)
    assert len(s._registry) == 4
    s1 = s.get_by_id("s1")
    assert s1.get_coords(0.0) == approx((100, 100))
    assert s1.get_coords(1.0) == approx((200, 100))

def test_load_from_yaml_big_1(s, yb1):
    s.load_from_dict(yb1)
