# -*- coding: utf-8 -*-
"""Unit tests for the physics module."""

import math
import numpy as np
import pytest
import physics


# ---- move ----

class TestMove:
    def test_zero_dt_no_change(self):
        """With dt=0, position and velocity are unchanged."""
        assert physics.move(5.0, 10.0, 3.0, -2.0, 0.5, 0) == pytest.approx(
            (5.0, 10.0, 3.0, -2.0)
        )

    def test_horizontal_motion(self):
        """Horizontal launch: x moves linearly, y only falls under gravity."""
        dt, vel, g = 2.0, 10.0, 1.0
        x, y, vx, vy = physics.move(0, 0, vel, 0, g, dt)
        assert x == pytest.approx(vel * dt)
        assert y == pytest.approx(-0.5 * g * dt**2)
        assert vx == pytest.approx(vel)
        assert vy == pytest.approx(-g * dt)

    def test_vertical_motion(self):
        """Vertical launch: x stays put and y follows a projectile."""
        dt, vel, g = 3.0, 5.0, 2.0
        x, y, _, vy = physics.move(0, 0, 0, vel, g, dt)
        assert x == pytest.approx(0)
        assert y == pytest.approx(vel * dt - 0.5 * g * dt**2)
        assert vy == pytest.approx(vel - g * dt)

    def test_offset_origin(self):
        """Initial position offsets the result."""
        x, y, _, _ = physics.move(100, 200, 5, 0, 0, 1.0)
        assert x == pytest.approx(105.0)
        assert y == pytest.approx(200.0)

    def test_small_steps_match_one_large_step(self):
        """Ten steps of dt/10 land exactly where one step of dt does."""
        state = (0.0, 0.0, 7.0, 4.0)
        for _ in range(10):
            state = physics.move(*state, 0.5, 0.3)
        expected = physics.move(0.0, 0.0, 7.0, 4.0, 0.5, 3.0)
        assert state == pytest.approx(expected)


# ---- clamp_to_boundary ----

class TestClampToBoundary:
    def test_outside_clamped_to_surface(self):
        """A point outside the circle is pulled back to the inner surface."""
        # Point at (750, 400), center=400, radius=340, ball_radius=10
        x, y = physics.clamp_to_boundary(750, 400, 400, 340, 10)
        dist = math.sqrt((x - 400)**2 + (y - 400)**2)
        assert dist == pytest.approx(330)  # radius - ball_radius

    def test_preserves_direction(self):
        """Clamped point is on the same ray from center as the original."""
        x, y = physics.clamp_to_boundary(500, 500, 400, 340, 10)
        # Direction from center should be (1, 1) normalized
        dx, dy = x - 400, y - 400
        angle = math.atan2(dy, dx)
        assert angle == pytest.approx(math.pi / 4)

    def test_at_center_degenerate(self):
        """Ball exactly at center is pushed to a valid boundary position."""
        x, y = physics.clamp_to_boundary(400, 400, 400, 340, 10)
        dist = math.sqrt((x - 400)**2 + (y - 400)**2)
        assert dist == pytest.approx(330)

    def test_already_inside(self):
        """A point inside still gets projected to the boundary surface."""
        x, y = physics.clamp_to_boundary(410, 400, 400, 340, 10)
        dist = math.sqrt((x - 400)**2 + (y - 400)**2)
        assert dist == pytest.approx(330)


# ---- reflect_velocity ----

class TestReflectVelocity:
    def test_head_on_collision(self):
        """Ball moving straight outward reflects straight inward."""
        # Ball at (740, 400), moving right (+x), center at 400
        vx, vy = physics.reflect_velocity(10, 0, 740, 400, 400, 1.0)
        assert vx == pytest.approx(-10)
        assert vy == pytest.approx(0)

    def test_restitution_reduces_normal_speed(self):
        """Restitution < 1 reduces only the normal component."""
        vx, vy = physics.reflect_velocity(10, 0, 740, 400, 400, 0.5)
        assert vx == pytest.approx(-5)
        assert vy == pytest.approx(0)

    def test_tangential_preserved(self):
        """Tangential velocity component is unchanged by reflection."""
        # Ball at (740, 400), moving right and up
        vx, vy = physics.reflect_velocity(10, 5, 740, 400, 400, 1.0)
        # Normal is along x (outward = +x), tangential is along y
        assert vx == pytest.approx(-10)
        assert vy == pytest.approx(5)

    def test_restitution_does_not_affect_tangential(self):
        """Even with low restitution, tangential speed stays the same."""
        vx, vy = physics.reflect_velocity(10, 7, 740, 400, 400, 0.5)
        assert vx == pytest.approx(-5)
        assert vy == pytest.approx(7)

    def test_diagonal_collision(self):
        """Ball hitting wall at 45-degree position reflects correctly."""
        # Ball at 45 degrees on the circle
        r = 330
        pos_x = 400 + r / math.sqrt(2)
        pos_y = 400 + r / math.sqrt(2)
        # Moving directly outward at 45 degrees
        speed = 10
        vel_x = speed / math.sqrt(2)
        vel_y = speed / math.sqrt(2)

        new_vx, new_vy = physics.reflect_velocity(
            vel_x, vel_y, pos_x, pos_y, 400, 1.0
        )
        # Should reflect to inward direction
        assert new_vx == pytest.approx(-vel_x)
        assert new_vy == pytest.approx(-vel_y)

    def test_degenerate_at_center(self):
        """Ball at exact center returns velocity unchanged."""
        vx, vy = physics.reflect_velocity(5, 3, 400, 400, 400, 1.0)
        assert vx == pytest.approx(5)
        assert vy == pytest.approx(3)

    def test_friction_reduces_tangential(self):
        """Friction reduces tangential component on collision."""
        # Ball at (740, 400) moving right and up; normal is x, tangential y
        vx, vy = physics.reflect_velocity(
            10, 8, 740, 400, 400, 1.0, friction=0.5
        )
        assert vx == pytest.approx(-10)  # normal fully reflected
        assert vy == pytest.approx(4)    # tangential halved

    def test_friction_zero_is_default(self):
        """With friction=0, tangential is fully preserved (backward compat)."""
        vx, vy = physics.reflect_velocity(
            10, 8, 740, 400, 400, 1.0, friction=0.0
        )
        assert vx == pytest.approx(-10)
        assert vy == pytest.approx(8)

    def test_full_friction_zeroes_tangential(self):
        """With friction=1, all tangential speed is lost."""
        vx, vy = physics.reflect_velocity(
            10, 8, 740, 400, 400, 1.0, friction=1.0
        )
        assert vx == pytest.approx(-10)
        assert vy == pytest.approx(0)

    def test_friction_with_restitution(self):
        """Friction and restitution apply independently to their components."""
        vx, vy = physics.reflect_velocity(
            10, 6, 740, 400, 400, 0.5, friction=0.5
        )
        assert vx == pytest.approx(-5)  # normal * restitution
        assert vy == pytest.approx(3)   # tangential * (1 - friction)


# ---- apply_drag ----

class TestApplyDrag:
    def test_no_drag(self):
        """With drag=0, velocity is unchanged."""
        vx, vy = physics.apply_drag(10, 5, 0, 1.0)
        assert vx == pytest.approx(10)
        assert vy == pytest.approx(5)

    def test_drag_reduces_speed(self):
        """Drag reduces both velocity components."""
        vx, vy = physics.apply_drag(10, 10, 0.1, 1.0)
        expected = 10 * (1 - 0.1) ** 1.0
        assert vx == pytest.approx(expected)
        assert vy == pytest.approx(expected)

    def test_drag_scales_with_dt(self):
        """Larger dt applies more drag."""
        vx1, _ = physics.apply_drag(10, 0, 0.1, 1.0)
        vx2, _ = physics.apply_drag(10, 0, 0.1, 2.0)
        assert vx2 < vx1  # more time = more drag

    def test_drag_is_framerate_independent(self):
        """Two half-steps of drag equal one full step."""
        vx_full, vy_full = physics.apply_drag(10, 10, 0.1, 2.0)
        vx_half, vy_half = physics.apply_drag(10, 10, 0.1, 1.0)
        vx_two, vy_two = physics.apply_drag(vx_half, vy_half, 0.1, 1.0)
        assert vx_two == pytest.approx(vx_full)
        assert vy_two == pytest.approx(vy_full)

    def test_drag_preserves_direction(self):
        """Drag scales magnitude but doesn't change direction."""
        vx, vy = physics.apply_drag(-7, 3, 0.2, 1.5)
        factor = (1 - 0.2) ** 1.5
        assert vx == pytest.approx(-7 * factor)
        assert vy == pytest.approx(3 * factor)

    def test_negative_drag_treated_as_zero(self):
        """Negative drag coefficient is treated as no drag."""
        vx, vy = physics.apply_drag(10, 5, -0.5, 1.0)
        assert vx == pytest.approx(10)
        assert vy == pytest.approx(5)


# ---- step ----

# Arena used by the step tests: matches the defaults in main.py
ARENA = dict(center=400, radius=340, ball_radius=10)


class TestStep:
    def test_free_flight_matches_move(self):
        """Away from the wall and without drag, step is a plain move."""
        result = physics.step(400, 400, 3, 2, dt=0.6, gravity=0.3,
                              restitution=0.9, **ARENA)
        assert result == pytest.approx(physics.move(400, 400, 3, 2, 0.3, 0.6))

    def test_free_flight_follows_parabola(self):
        """Many steps without drag stay on the analytic projectile path."""
        x, y, vx, vy = 400.0, 400.0, 2.0, 3.0
        dt, g, n = 0.6, 0.3, 15
        for _ in range(n):
            x, y, vx, vy = physics.step(x, y, vx, vy, dt=dt, gravity=g,
                                        restitution=0.9, **ARENA)
        t = n * dt
        assert x == pytest.approx(400 + 2.0 * t)
        assert y == pytest.approx(400 + 3.0 * t - 0.5 * g * t**2)

    def test_drag_moves_one_timestep(self):
        """With drag on, the ball still advances one timestep, not two."""
        vx0, dt, drag = 10.0, 0.6, 0.005
        x, _, _, _ = physics.step(400, 400, vx0, 0, dt=dt, gravity=0,
                                  restitution=0.9, drag=drag, **ARENA)
        assert x - 400 == pytest.approx(vx0 * (1 - drag) ** dt * dt)

    def test_bounce_lands_on_wall(self):
        """A step that crosses the wall ends on the inner surface."""
        x, y, _, _ = physics.step(728, 400, 10, 0, dt=1.0, gravity=0,
                                  restitution=1.0, **ARENA)
        assert math.hypot(x - 400, y - 400) == pytest.approx(330)

    def test_bounce_reverses_outward_velocity(self):
        """After a bounce the ball heads back toward the centre."""
        x, y, vx, vy = physics.step(728, 400, 10, 0, dt=1.0, gravity=0,
                                    restitution=0.8, **ARENA)
        assert vx == pytest.approx(-8)
        assert vy == pytest.approx(0)

    def test_ball_stays_inside_long_run(self):
        """With the default settings the ball never leaves the arena."""
        x, y = 400.0, 400.0
        vx, vy = 10 * np.cos(np.deg2rad(20)), 10 * np.sin(np.deg2rad(20))
        max_dist = 0.0
        for _ in range(5000):
            x, y, vx, vy = physics.step(
                x, y, vx, vy, dt=0.6, gravity=0.3, restitution=0.9,
                friction=0.05, drag=0.005, **ARENA,
            )
            max_dist = max(max_dist, math.hypot(x - 400, y - 400))
        assert max_dist <= 330 + 1e-9
        assert not (math.isnan(x) or math.isnan(y))
