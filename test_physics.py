# -*- coding: utf-8 -*-
"""Unit tests for the physics module."""

import math
import numpy as np
import pytest
import physics


# ---- get_pos ----

class TestGetPos:
    def test_stationary_at_t0(self):
        """At t=0, position should equal initial position."""
        x, y = physics.get_pos(0, 0, 5.0, 10.0, 10, 0.5)
        assert x == pytest.approx(5.0)
        assert y == pytest.approx(10.0)

    def test_horizontal_motion(self):
        """With theta=0, x moves linearly and y only affected by gravity."""
        t, vel, g = 2.0, 10.0, 1.0
        x, y = physics.get_pos(t, 0, 0, 0, vel, g)
        assert x == pytest.approx(vel * t)
        assert y == pytest.approx(-0.5 * g * t**2)

    def test_vertical_motion(self):
        """With theta=pi/2, x stays at origin and y is projectile."""
        t, vel, g = 3.0, 5.0, 2.0
        x, y = physics.get_pos(t, np.pi / 2, 0, 0, vel, g)
        assert x == pytest.approx(0, abs=1e-10)
        assert y == pytest.approx(vel * t - 0.5 * g * t**2)

    def test_arbitrary_angle(self):
        """Position matches hand-calculated projectile at 45 degrees."""
        t, vel, g = 1.0, 10.0, 0.5
        theta = np.pi / 4
        x, y = physics.get_pos(t, theta, 0, 0, vel, g)
        expected_x = vel * np.cos(theta) * t
        expected_y = vel * np.sin(theta) * t - 0.5 * g * t**2
        assert x == pytest.approx(expected_x)
        assert y == pytest.approx(expected_y)

    def test_offset_origin(self):
        """Initial position offsets the result."""
        x, y = physics.get_pos(1.0, 0, 100, 200, 5, 0)
        assert x == pytest.approx(105.0)
        assert y == pytest.approx(200.0)


# ---- get_vel ----

class TestGetVel:
    def test_initial_velocity(self):
        """At t=0, velocity equals launch components."""
        vx, vy = physics.get_vel(0, np.pi / 6, 10.0, 1.0)
        assert vx == pytest.approx(10.0 * np.cos(np.pi / 6))
        assert vy == pytest.approx(10.0 * np.sin(np.pi / 6))

    def test_gravity_decelerates_y(self):
        """Gravity reduces vy over time, vx is constant."""
        t, vel, g = 4.0, 10.0, 2.0
        vx, vy = physics.get_vel(t, 0, vel, g)
        assert vx == pytest.approx(vel)
        assert vy == pytest.approx(-g * t)

    def test_zero_velocity(self):
        """Zero initial speed gives only gravity contribution."""
        vx, vy = physics.get_vel(3.0, np.pi / 4, 0, 1.0)
        assert vx == pytest.approx(0)
        assert vy == pytest.approx(-3.0)


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
        """Ball exactly at center gets pushed to an arbitrary valid position."""
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
