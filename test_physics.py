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


def bounce(xpos, ypos, xvel, yvel, e=1, mu=0, sides=0):
    return physics.bounce(xpos, ypos, xvel, yvel, cent, rad, ball_rad, sides,
                          e, mu)


def launch(xpos, ypos, xvel, yvel):
    # ball (t, theta, x0, y0, v0) launched from (xpos, ypos) with (xvel, yvel)
    return (0, np.arctan2(yvel, xvel), xpos, ypos, np.hypot(xvel, yvel))


def step(ball, g, dt, e=1, mu=0, k=0, sides=0):
    return physics.step(*ball, cent, rad, ball_rad, sides, g, dt, e, mu, k)


def furthest_past_wall(xpos, ypos, sides, tilt=0):
    # how far the ball is past the wall it is closest to going through
    return max((xpos - cent) * nx + (ypos - cent) * ny - (a - ball_rad)
               for nx, ny, a in physics.walls(xpos, ypos, cent, rad, sides,
                                              tilt))


# =============================================================================
# Trajectory
# =============================================================================

def test_pos_at_launch():
    assert physics.get_pos(0, 0.3, 5, 10, 10, 0.5) == pytest.approx((5, 10))


def test_pos_horizontal():
    # x moves in a straight line, y only falls from gravity
    assert physics.get_pos(2, 0, 0, 0, 10, 1) == pytest.approx((20, -2))


def test_pos_vertical():
    xpos, ypos = physics.get_pos(3, np.pi/2, 0, 0, 5, 2)
    assert xpos == pytest.approx(0, abs=1e-12)
    assert ypos == pytest.approx(5*3 - 0.5*2*3**2)


def test_pos_45_degrees():
    t, v, g = [1, 10, 0.5]
    xpos, ypos = physics.get_pos(t, np.pi/4, 0, 0, v, g)
    assert xpos == pytest.approx(v * np.cos(np.pi/4) * t)
    assert ypos == pytest.approx(v * np.sin(np.pi/4) * t - 0.5 * g * t**2)


def test_vel_at_launch():
    xvel, yvel = physics.get_vel(0, np.pi/6, 10, 1)
    assert (xvel, yvel) == pytest.approx((10*np.cos(np.pi/6),
                                          10*np.sin(np.pi/6)))


def test_gravity_slows_yvel():
    # gravity only changes yvel, xvel stays the same
    assert physics.get_vel(4, 0, 10, 2) == pytest.approx((10, -8))


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
    _, _, xvel, yvel = bounce(735, 400, 10, 0)
    assert (xvel, yvel) == pytest.approx((-10, 0))


def test_bounce_restitution():
    # e only slows the normal component, tangential one is kept
    _, _, xvel, yvel = bounce(735, 400, 10, 7, e=0.5)
    assert (xvel, yvel) == pytest.approx((-5, 7))


def test_bounce_friction():
    # mu only slows the tangential component
    _, _, xvel, yvel = bounce(735, 400, 10, 8, mu=0.5)
    assert (xvel, yvel) == pytest.approx((-10, 4))


def test_bounce_full_friction():
    _, _, xvel, yvel = bounce(735, 400, 10, 8, mu=1)
    assert (xvel, yvel) == pytest.approx((-10, 0))


def test_bounce_moving_away_from_wall():
    # ball on the wall but already heading back in is left alone
    _, _, xvel, yvel = bounce(731, 400, -10, 3)
    assert (xvel, yvel) == pytest.approx((-10, 3))


def test_reflect_matches_readme_equation():
    # v' = (1 - mu) v - (1 - mu + e) (v.n) n, with n pointing into the board
    rng = np.random.default_rng(0)
    for i in range(100):
        v = rng.normal(size=2)
        n = rng.normal(size=2)
        n = n / np.linalg.norm(n)
        if v @ n >= 0:
            v = -v   # only bounce when moving into the wall
        e, mu = rng.uniform(size=2)
        expected = (1 - mu) * v - (1 - mu + e) * (v @ n) * n
        assert physics.reflect(*v, *n, e, mu) == pytest.approx(expected)


def test_bounce_diagonal():
    # ball just past the wall at 45 degrees, moving straight out, comes
    # straight back
    r = 335 / np.sqrt(2)
    v = 10 / np.sqrt(2)
    _, _, xvel, yvel = bounce(cent + r, cent + r, v, v)
    assert (xvel, yvel) == pytest.approx((-v, -v))


# =============================================================================
# Step
# =============================================================================

def test_step_follows_trajectory():
    # without a bounce or drag the ball stays on one trajectory, t just grows
    ball = (0, 0.4, 400, 400, 5)
    for i in range(15):
        ball = step(ball, 0.3, 0.6)
    assert ball[0] == pytest.approx(15 * 0.6)
    assert ball[1:] == pytest.approx((0.4, 400, 400, 5))


def test_step_with_drag_moves_one_timestep():
    # with drag on, the ball is launched again every timestep but should
    # still only move one timestep
    ball = step(launch(400, 400, 10, 0), 0, 0.6, k=0.005)
    t, theta, x0, y0, v0 = ball
    assert t == 0
    assert x0 - 400 == pytest.approx(10 * 0.6)
    assert v0 == pytest.approx(10 * (1 - 0.005)**0.6)


def test_step_bounce_lands_on_wall():
    # a step that goes past the wall ends on the boundary, and the ball is
    # launched again from there
    ball = step(launch(728, 400, 10, 0), 0, 1, e=0.8)
    xpos, ypos = physics.get_pos(*ball, 0)
    assert ball[0] == 0
    assert dist(xpos, ypos) == pytest.approx(330)
    assert physics.get_vel(*ball[:2], ball[4], 0) == pytest.approx((-8, 0))


def test_no_bounce_inside():
    assert not physics.hit(500, 450, cent, rad, ball_rad, 0)
    assert physics.hit(735, 400, cent, rad, ball_rad, 0)


# =============================================================================
# Other shapes
# =============================================================================

def test_square_walls():
    # square with corners on the circle, so its sides are rad/sqrt(2) away
    a = rad / np.sqrt(2)
    got = sorted((round(nx), round(ny)) for nx, ny, _ in
                 physics.walls(0, 0, cent, rad, 4))
    assert got == [(-1, 0), (0, -1), (0, 1), (1, 0)]
    assert all(w[2] == pytest.approx(a) for w in
               physics.walls(0, 0, cent, rad, 4))


def test_triangle_has_flat_bottom():
    nx, ny, a = physics.walls(0, 0, cent, rad, 3)[0]
    assert (nx, ny) == pytest.approx((0, -1))
    assert a == pytest.approx(rad / 2)


def test_tilted_square_walls():
    # turned by 45 degrees the square stands on a corner, so its walls face
    # diagonally
    got = sorted((round(nx, 6), round(ny, 6)) for nx, ny, _ in
                 physics.walls(0, 0, cent, rad, 4, np.pi/4))
    d = round(1/np.sqrt(2), 6)
    assert got == [(-d, -d), (-d, d), (d, -d), (d, d)]


def test_tilt_does_not_change_circle():
    assert physics.walls(500, 450, cent, rad, 0, 1.0) == pytest.approx(
        physics.walls(500, 450, cent, rad, 0))


def test_square_bounce():
    # past the right wall of the square, moving right and up
    a = rad / np.sqrt(2)
    xpos, ypos, xvel, yvel = bounce(cent + a, 450, 10, 4, e=0.5, sides=4)
    assert (xpos, ypos) == pytest.approx((cent + a - ball_rad, 450))
    assert (xvel, yvel) == pytest.approx((-5, 4))


def test_triangle_corner():
    # deep in the bottom left corner, the ball ends up inside both walls and
    # comes out with both components bounced
    xpos, ypos, xvel, yvel = bounce(80, 200, -5, -5, sides=3)
    assert furthest_past_wall(xpos, ypos, 3) <= 1e-9
    assert np.hypot(xvel, yvel) == pytest.approx(np.hypot(5, 5))
    assert xvel > 0 and yvel > 0


@pytest.mark.parametrize("sides", [0, 3, 4, 5, 6, 8])
@pytest.mark.parametrize("deg", [0, 17, 45, 60, 221])
def test_ball_stays_inside(sides, deg):
    # settings from main.py, ball should never leave the board, however the
    # shape is turned
    tilt = np.deg2rad(deg)
    for k in [0, 0.005]:
        ball = (0, np.deg2rad(20), 400, 400, 10)
        furthest = -rad
        for i in range(3000):
            ball = physics.step(*ball, cent, rad, ball_rad, sides, 0.3, 0.6,
                                0.9, 0.05, k, tilt)
            xpos, ypos = physics.get_pos(*ball, 0.3)
            furthest = max(furthest, furthest_past_wall(xpos, ypos, sides,
                                                        tilt))
        assert furthest <= 1e-9
