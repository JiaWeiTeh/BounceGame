# -*- coding: utf-8 -*-
"""Tests for the physics functions."""

import numpy as np
import pytest
import physics

# same board and ball as in main.py
cent, rad, ball_rad = [400, 340, 10]


def dist(xpos, ypos):
    # distance from the centre of the board
    return np.sqrt((xpos - cent)**2 + (ypos - cent)**2)


def bounce(xpos, ypos, xvel, yvel, e=1, mu=0):
    return physics.bounce(xpos, ypos, xvel, yvel, cent, rad, ball_rad, e, mu)


def step(xpos, ypos, xvel, yvel, g, dt, e=1, mu=0, k=0):
    return physics.step(xpos, ypos, xvel, yvel, cent, rad, ball_rad,
                        g, dt, e, mu, k)


# =============================================================================
# Move
# =============================================================================

def test_move_horizontal():
    # x moves in a straight line, y only falls from gravity
    assert physics.move(0, 0, 10, 0, 1, 2) == pytest.approx((20, -2, 10, -2))


def test_move_vertical():
    xpos, ypos, xvel, yvel = physics.move(0, 0, 0, 5, 2, 3)
    assert xpos == pytest.approx(0)
    assert ypos == pytest.approx(5*3 - 0.5*2*3**2)
    assert yvel == pytest.approx(5 - 2*3)


def test_move_zero_dt():
    assert physics.move(5, 10, 3, -2, 0.5, 0) == pytest.approx((5, 10, 3, -2))


def test_move_small_steps_same_as_big_step():
    # 10 steps of 0.3 land on the same parabola as 1 step of 3
    ball = (0, 0, 7, 4)
    for i in range(10):
        ball = physics.move(*ball, 0.5, 0.3)
    assert ball == pytest.approx(physics.move(0, 0, 7, 4, 0.5, 3))


# =============================================================================
# Drag
# =============================================================================

def test_no_drag():
    assert physics.drag(10, 5, 0, 1) == pytest.approx((10, 5))


def test_drag_slows_ball():
    factor = (1 - 0.2)**1.5
    assert physics.drag(-7, 3, 0.2, 1.5) == pytest.approx((-7*factor,
                                                           3*factor))


def test_drag_same_for_any_dt():
    # 2 steps of 1 give the same drag as 1 step of 2
    xvel, yvel = physics.drag(10, 10, 0.1, 1)
    xvel, yvel = physics.drag(xvel, yvel, 0.1, 1)
    assert (xvel, yvel) == pytest.approx(physics.drag(10, 10, 0.1, 2))


# =============================================================================
# Bounce
# =============================================================================

def test_bounce_puts_ball_back_on_boundary():
    xpos, ypos, _, _ = bounce(750, 400, 10, 0)
    assert dist(xpos, ypos) == pytest.approx(330)


def test_bounce_keeps_direction_from_centre():
    xpos, ypos, _, _ = bounce(700, 700, 10, 10)
    assert np.arctan2(ypos - cent, xpos - cent) == pytest.approx(np.pi/4)


def test_bounce_head_on():
    _, _, xvel, yvel = bounce(730, 400, 10, 0)
    assert (xvel, yvel) == pytest.approx((-10, 0))


def test_bounce_restitution():
    # e only slows the normal component, tangential one is kept
    _, _, xvel, yvel = bounce(730, 400, 10, 7, e=0.5)
    assert (xvel, yvel) == pytest.approx((-5, 7))


def test_bounce_friction():
    # mu only slows the tangential component
    _, _, xvel, yvel = bounce(730, 400, 10, 8, mu=0.5)
    assert (xvel, yvel) == pytest.approx((-10, 4))


def test_bounce_full_friction():
    _, _, xvel, yvel = bounce(730, 400, 10, 8, mu=1)
    assert (xvel, yvel) == pytest.approx((-10, 0))


def test_bounce_diagonal():
    # ball at 45 degrees moving straight out comes straight back
    r = 330 / np.sqrt(2)
    v = 10 / np.sqrt(2)
    _, _, xvel, yvel = bounce(cent + r, cent + r, v, v)
    assert (xvel, yvel) == pytest.approx((-v, -v))


# =============================================================================
# Step
# =============================================================================

def test_step_free_flight():
    # away from the wall and without drag, step is just move
    assert step(400, 400, 3, 2, 0.3, 0.6) == pytest.approx(
        physics.move(400, 400, 3, 2, 0.3, 0.6))


def test_step_follows_parabola():
    ball = (400, 400, 2, 3)
    for i in range(15):
        ball = step(*ball, 0.3, 0.6)
    t = 15 * 0.6
    assert ball[0] == pytest.approx(400 + 2*t)
    assert ball[1] == pytest.approx(400 + 3*t - 0.5*0.3*t**2)


def test_step_with_drag_moves_one_timestep():
    # with drag on, the ball should still only move one timestep per step
    xpos, _, _, _ = step(400, 400, 10, 0, 0, 0.6, k=0.005)
    assert xpos - 400 == pytest.approx(10 * (1 - 0.005)**0.6 * 0.6)


def test_step_bounce_lands_on_wall():
    # a step that goes past the wall ends on the boundary, not past it
    xpos, ypos, xvel, yvel = step(728, 400, 10, 0, 0, 1, e=0.8)
    assert dist(xpos, ypos) == pytest.approx(330)
    assert (xvel, yvel) == pytest.approx((-8, 0))


def test_ball_stays_inside():
    # settings from main.py, ball should never leave the board
    ball = (400, 400, 10*np.cos(np.deg2rad(20)), 10*np.sin(np.deg2rad(20)))
    furthest = 0
    for i in range(5000):
        ball = step(*ball, 0.3, 0.6, e=0.9, mu=0.05, k=0.005)
        furthest = max(furthest, dist(ball[0], ball[1]))
    assert furthest <= 330 + 1e-9
