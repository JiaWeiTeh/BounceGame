# -*- coding: utf-8 -*-
"""Physics helper functions for the bounce simulation.

Provides drawing, kinematics, and collision-reflection utilities.
"""

import numpy as np


def draw(ax, radius, center):
    """Draw circular boundary on the given axes."""
    angle = np.linspace(0, 2 * np.pi, 200)

    x = radius * np.cos(angle) + center
    y = radius * np.sin(angle) + center

    ax.plot(x, y, c='green')


def get_vel(t, theta, vel, g):
    """Return velocity components (vx, vy) at time t given initial launch angle."""
    xvel = vel * np.cos(theta)
    yvel = vel * np.sin(theta) - g * t

    return xvel, yvel


def get_pos(t, theta, x0, y0, vel, g):
    """Return position (x, y) at time t given initial launch angle and position."""
    xpos = vel * np.cos(theta) * t + x0
    ypos = vel * np.sin(theta) * t - 0.5 * g * t**2 + y0

    return xpos, ypos


def clamp_to_boundary(xpos, ypos, center, radius, ball_radius):
    """Project a position back onto the circle boundary (minus ball radius).

    Returns the clamped (x, y) on the inner boundary surface.
    """
    dx = xpos - center
    dy = ypos - center
    dist = np.sqrt(dx**2 + dy**2)
    if dist == 0:
        # Degenerate: ball exactly at center, push in arbitrary direction
        return center + (radius - ball_radius), center
    max_dist = radius - ball_radius
    scale = max_dist / dist
    return center + dx * scale, center + dy * scale


def reflect_velocity(xvel, yvel, xpos, ypos, center, restitution):
    """Reflect velocity off the circular boundary using vector math.

    Uses the inward-pointing normal of the circle at the contact point.
    The coefficient of restitution is applied only to the normal component
    of velocity, preserving tangential speed.

    Returns (new_vx, new_vy).
    """
    # Normal vector pointing inward (from contact point toward center)
    nx = center - xpos
    ny = center - ypos
    n_mag = np.sqrt(nx**2 + ny**2)
    if n_mag == 0:
        # Degenerate case: ball at exact center, return velocity unchanged
        return xvel, yvel
    nx /= n_mag
    ny /= n_mag

    # Decompose velocity into normal and tangential components
    v_dot_n = xvel * nx + yvel * ny
    # Normal component (into the wall is negative v_dot_n)
    vn_x = v_dot_n * nx
    vn_y = v_dot_n * ny
    # Tangential component
    vt_x = xvel - vn_x
    vt_y = yvel - vn_y

    # Reflect: reverse normal component, apply restitution only to normal
    new_vx = vt_x - restitution * vn_x
    new_vy = vt_y - restitution * vn_y

    return new_vx, new_vy
