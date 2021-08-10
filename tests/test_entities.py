# import pytest
from pytest import approx
import logging

from najork.entities import Anchor, Line, Slider, Circle, Intersection

def test_anchor():
    p = Anchor("p1",1,(0.0, 0.0))
    for t in range(0, 11):
        assert p.get_coords(t/10.0) == approx((0.0, 0.0))

def test_anchored_line():
    p1 = Anchor("p1",1,(0.0, 0.0))
    p2 = Anchor("p2",1,(2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    for t in range(0, 11):
        # should be invariant
        assert l1.calc_procession_xy(t/10.0, 0.0) == approx((0.0, 0.0))
        assert l1.calc_procession_xy(t/10.0, 1.0) == approx((2.0, 2.0))
        assert l1.calc_procession_xy(t/10.0, 0.5) == approx((1.0, 1.0))

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
        assert i5.get_coords(t/10.0) == approx((1.0, 1.0))

def test_no_intersection():
    p1 = Anchor("p1",1,(0.0, 1.0))
    p2 = Anchor("p2",1,(2.0, 1.0))
    p3 = Anchor("p3",1,(1.0, 2.0))
    p4 = Anchor("p4",1,(1.0, 4.0))
    l1 = Line("l1", 2, (p1, p2))
    l2 = Line("l2", 2, (p3, p4))
    i5 = Intersection("i5", 3, (l1, l2))
    for t in range(0, 11):
        assert i5.get_coords(t/10.0) == approx(p1.get_coords(t))

def test_anchroed_circle_intersection():
    p1 = Anchor("p1",1,(0.0, 1.0))
    p2 = Anchor("p2",1,(2.0, 1.0))
    p3 = Anchor("p3",1,(2.0, 1.0))
    l1 = Line("l1", 2, (p1, p2))
    c1 = Circle("c1", 2, p3, 1.0, 0.0) 
    i5 = Intersection("i5", 3, (l1, c1))
    for t in range(0, 11):
        assert i5.get_coords(t/10.0) == approx((1.0, 1.0))

def test_linear_slider_unlooped():
    p1 = Anchor("p1",1,(0.0, 0.0))
    p2 = Anchor("p2",1,(2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    s1 = Slider("s1", 3, l1, 0.0, 1.0, loop=False)
    assert s1.get_coords(0.0) == approx((0.0, 0.0))
    assert s1.get_coords(0.5) == approx((1.0, 1.0))
    assert s1.get_coords(1.0) == approx((2.0, 2.0))

def test_linear_slider_looped():
    p1 = Anchor("p1",1,(0.0, 0.0))
    p2 = Anchor("p2",1,(2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    s1 = Slider("s1", 3, l1, 0.0, 1.0, loop=True)
    assert s1.get_coords(0.0) == approx((0.0, 0.0))
    assert s1.get_coords(0.5) == approx((1.0, 1.0))
    assert s1.get_coords(0.9) == approx((1.8, 1.8))
    assert s1.get_coords(1.0) == approx((0.0, 0.0))

def test_line_linear_slider_unlooped():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 2, (0.0, 1.0))

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=False)

    l2 = Line("l2", 4, (s1, p3))
    # check length goes from 1 to sqr(2)
    from math import sqrt
    assert l2.get_impl(0.0).length == approx(1.0)
    assert l2.get_impl(1.0).length == approx(sqrt(2.0))

def test_line_linear_slider_looped():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 2, (0.0, 1.0))

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=True)

    l2 = Line("l2", 4, (s1, p3))
    # check length goes from 1 to sqr(2)
    from math import sqrt
    assert l2.get_impl(0.0).length == approx(1.0)
    assert l2.get_impl(1.0).length == approx(1.0)

def test_moving_intersection_linear_slider_unlooped():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 1, (0.0, 2.0))
    p4 = Anchor("p4", 1, (1.0, 2.0))
    l2 = Line("l2", 2, (p3, p4))

    # needs to extend slightly to avoid intersection
    # failing due to FP tolerances
    p3 = Anchor("p3", 1, (-0.1, 1.0))
    p4 = Anchor("p4", 1, (1.1, 1.0))
    l3 = Line("l3", 2, (p3, p4))

    s1 = Slider("s1", 3, l1, 0.0, 1.0, loop=False)
    s2 = Slider("s2", 3, l2, 0.0, 1.0, loop=False)

    l4 = Line("l2", 4, (s1, s2))

    i1 = Intersection("i1", 5, (l3, l4))

    # check length goes from 1 to sqr(2)
    for t in range(0, 11):
        assert i1.get_coords(t/10.0) == approx((t/10.0, 1.0))
