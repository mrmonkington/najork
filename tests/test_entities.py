# import pytest
from pytest import approx
import logging

from najork.entities import *

def test_anchor():
    p = Anchor("p1",1,(0.0, 0.0))
    for t in range(0, 11):
        assert p.get_coords(t/10.0) == (0.0, 0.0)

def test_anchored_line():
    p1 = Anchor("p1",1,(0.0, 0.0))
    p2 = Anchor("p2",1,(2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    for t in range(0, 11):
        # should be invariant
        assert l1.calc_procession_xy(t/10.0, 0.0) == (0.0, 0.0)
        assert l1.calc_procession_xy(t/10.0, 1.0) == (2.0, 2.0)
        assert l1.calc_procession_xy(t/10.0, 0.5) == (1.0, 1.0)

def test_anchored_circle():
    p1 = Anchor("p1", 1, (1.0, 1.0))
    c1 = Circle("c1", 2, p1, 1.0, 0.0) 
    for t in range(0, 11):
        # should be invariant
        assert c1.calc_procession_xy(t/10.0, 0.0) == approx((2.0, 1.0))
        assert c1.calc_procession_xy(t/10.0, 1.0) == approx((2.0, 1.0))
        assert c1.calc_procession_xy(t/10.0, 0.5) == approx((0.0, 1.0))


def test_anchored_intersection():
    p1 = Anchor("p1",1,(0.0, 1.0))
    p2 = Anchor("p2",1,(2.0, 1.0))
    p3 = Anchor("p3",1,(1.0, 0.0))
    p4 = Anchor("p4",1,(1.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    l2 = Line("l2", 2, (p3, p4))
    i5 = Intersection("i5", 3, (l1, l2))
    for t in range(0, 11):
        assert i5.get_coords(t/10.0) == (1.0, 1.0)

def __test_linear_slider():
    p1 = Anchor("p1",1,(0.0, 0.0))
    p2 = Anchor("p2",1,(2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    s1 = Slider("s1", 3, l1)
    for t in range(0, 11):
        # should be invariant
        assert l1.calc_procession_xy(t/10.0, 0.0) == (0.0, 0.0)
        assert l1.calc_procession_xy(t/10.0, 1.0) == (2.0, 2.0)
        assert l1.calc_procession_xy(t/10.0, 0.5) == (1.0, 1.0)


def __test_anchored_line():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    p2 = Slider("s3", 3, l1)
    for t in range(0, 11):
        # should be invariant
        assert l1.calc_procession_xy(t/10.0, 0.0) == (0.0, 0.0)
        assert l1.calc_procession_xy(t/10.0, 1.0) == (2.0, 2.0)
        assert l1.calc_procession_xy(t/10.0, 0.5) == (1.0, 1.0)

