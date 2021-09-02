# import pytest
from pytest import approx
import logging

from najork.entities import (
    Anchor, Line, Slider, Circle, Intersection, Distance,
    Angle, Control, Bumper
)
from najork.engine_sched import Engine, CV_FRAME_TIME

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
        assert l1.calc_position_xy(t/10.0, 0.0) == approx((0.0, 0.0))
        assert l1.calc_position_xy(t/10.0, 1.0) == approx((2.0, 2.0))
        assert l1.calc_position_xy(t/10.0, 0.5) == approx((1.0, 1.0))

def test_anchored_circle():
    p1 = Anchor("p1", 1, (1.0, 1.0))
    c1 = Circle("c1", 2, p1, 1.0, 0.0) 
    for t in range(0, 11):
        # should be invariant
        assert c1.calc_position_xy(t/10.0, 0.0) == approx((2.0, 1.0))
        assert c1.calc_position_xy(t/10.0, 1.0) == approx((2.0, 1.0))
        assert c1.calc_position_xy(t/10.0, 0.5) == approx((0.0, 1.0))


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
    s1 = Slider("s1", 3, l1, 0.0, 1.0, loop=False, inherit_velocity=False)
    assert s1.get_coords(0.0) == approx((0.0, 0.0))
    assert s1.get_coords(0.5) == approx((1.0, 1.0))
    assert s1.get_coords(1.0) == approx((2.0, 2.0))

def test_linear_slider_looped():
    p1 = Anchor("p1",1,(0.0, 0.0))
    p2 = Anchor("p2",1,(2.0, 2.0))
    l1 = Line("l1", 2, (p1, p2))
    s1 = Slider("s1", 3, l1, 0.0, 1.0, loop=True, inherit_velocity=False)
    assert s1.get_coords(0.0) == approx((0.0, 0.0))
    assert s1.get_coords(0.5) == approx((1.0, 1.0))
    assert s1.get_coords(0.9) == approx((1.8, 1.8))
    assert s1.get_coords(1.0) == approx((0.0, 0.0))

def test_line_linear_slider_unlooped():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 2, (0.0, 1.0))

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=False, inherit_velocity=False)

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

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=True, inherit_velocity=False)

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

    s1 = Slider("s1", 3, l1, 0.0, 1.0, loop=False, inherit_velocity=False)
    s2 = Slider("s2", 3, l2, 0.0, 1.0, loop=False, inherit_velocity=False)

    l4 = Line("l2", 4, (s1, s2))

    i1 = Intersection("i1", 5, (l3, l4))

    # check length goes from 1 to sqr(2)
    for t in range(0, 11):
        assert i1.get_coords(t/10.0) == approx((t/10.0, 1.0))

def test_circle_slider_unlooped():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    c1 = Circle("c1", 2, p1, 1.0, 0.0)

    s1 = Slider("s3", 3, c1, 0.0, 1.0, loop=False, inherit_velocity=False)

    l2 = Line("l2", 4, (p1, s1))
    for t in range(0, 11):
        assert l2.get_impl(t/10.0).length == approx(1.0, rel=1e-3)

    assert s1.get_coords(0.0) == approx((1.0, 0.0))
    assert s1.get_coords(1.0) == approx((1.0, 0.0))
    assert s1.get_coords(0.5) == approx((-1.0, 0.0))
    assert s1.get_coords(0.25) == approx((0.0, -1.0))
    assert s1.get_coords(0.75) == approx((0.0, 1.0))
    # assert l2.get_impl(1.0).length == approx(sqrt(2.0))

def test_distance():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p1", 1, (1.0, 1.0))
    m1 = Distance("d1", 2, (p1, p2))
    from math import sqrt
    assert m1.get_value(0.0) == approx(sqrt(2.0))

def test_angle():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (0.0, 1.0))
    p3 = Anchor("p3", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))
    l2 = Line("l2", 2, (p1, p3))
    a1 = Angle("a1", 3, (l2, l1))  # l2 -> l1 is positive anticlkwise
    from math import sqrt
    # 1/4 == 90deg
    assert a1.get_value(0.0) == approx(1.0/4.0)

def test_control_simple():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 2, (0.0, 1.0))

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=False, inherit_velocity=False)

    m1 = Distance("d1", 4, (p3, s1))

    c1 = Control("c1", 5, 0.0, 0.0, b"/bums")

    c1.add_input("in_1", m1)
    c1.msg.set_data(["in_1 * 2", ])
    from math import sqrt
    assert c1.msg.get_data(0.0) == approx([2.0, ])
    assert c1.msg.get_data(1.0) == approx([2 * sqrt(2.0), ])

def test_control_simple_2():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 2, (0.0, 1.0))

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=False, inherit_velocity=False)

    l2 = Line("l2", 3, (p3, p1))
    l3 = Line("l3", 4, (p3, s1))

    m1 = Distance("d1", 4, (p3, s1))
    a1 = Angle("a1", 5, (l2, l3))

    c1 = Control("c1", 5, 0.0, 0.0, b"/bums")

    c1.add_input("in_1", m1)
    c1.add_input("in_2", a1)
    c1.msg.set_data([
        "in_1 * 2",
        "in_2",
    ])
    from math import sqrt
    assert c1.msg.get_data(0.0) == approx([2.0, 0.0])  # ||_
    assert c1.msg.get_data(1.0) == approx([2 * sqrt(2.0), 1.0/8.0])  # |\_

def test_control_compound():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 2, (0.0, 1.0))

    s1 = Slider("s3", 3, l1, 0.0, 1.0, loop=False, inherit_velocity=False)

    l2 = Line("l2", 3, (p3, p1))
    l3 = Line("l3", 4, (p3, s1))

    m1 = Distance("d1", 4, (p3, s1))
    a1 = Angle("a1", 5, (l2, l3))

    c1 = Control("c1", 5, 0.0, 0.0, b"/bums")

    c1.add_input("in_1", m1)
    c1.add_input("in_2", a1)
    c1.msg.set_data([
        "in_1 * in_2",
    ])
    from math import sqrt
    assert c1.msg.get_data(0.0) == approx([0.0, ])  # ||_
    assert c1.msg.get_data(1.0) == approx([sqrt(2.0) / 8.0, ])  # |\_

def test_bumper_concrete_point_moves_surface_static():
    p1 = Anchor("p1", 1, (0.0, 0.0))
    p2 = Anchor("p2", 1, (1.0, 0.0))
    l1 = Line("l1", 2, (p1, p2))

    p3 = Anchor("p3", 1, (0.5, 1.0))
    p4 = Anchor("p4", 1, (0.5, -1.0))

    l2 = Line("l2", 2, (p3, p4))

    b1 = Bumper("b1", 3,
                l1, 0.0, 1.0,
                l2, "/bump",
                loop=False, inherit_velocity=False)

    b1.msg.set_data([
        "1",
    ])

    assert b1.test_collision(0.0, 1.0) is True

    assert b1.test_collision(0.0, 0.0 + CV_FRAME_TIME) is False
    # we need to test that collision is only triggered for a single
    # frame if the collision occurs t = t1, t < t2 (NOT t <= t2)
    assert b1.test_collision(0.5 - 2 * CV_FRAME_TIME, 0.5 - CV_FRAME_TIME) is False
    assert b1.test_collision(0.5 - CV_FRAME_TIME, 0.50) is False
    assert b1.test_collision(0.5, 0.5 + CV_FRAME_TIME) is True
    assert b1.test_collision(0.5 - CV_FRAME_TIME/2, 0.50 + CV_FRAME_TIME/2) is True
    assert b1.test_collision(0.5 + CV_FRAME_TIME, 0.5 + 2 * CV_FRAME_TIME) is False

    assert b1.test_collision(1.0, 1.0 + CV_FRAME_TIME) is False


