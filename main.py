# -*- coding: utf-8 -*-
"""Bouncing ball simulation inside a circular boundary.

Animates a ball with projectile motion, gravity, and energy loss
on collision with the circular wall.
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import physics

# =============================================================================
# Configuration
# =============================================================================

# Arena geometry
BOARD_SIZE = 800
CENTER = BOARD_SIZE // 2
RADIUS = 340
AXIS_PADDING = 200

# Ball properties
BALL_RADIUS = 10
INITIAL_SPEED = 10
INITIAL_ANGLE = np.deg2rad(0)
INITIAL_X, INITIAL_Y = CENTER, CENTER

# Physics
GRAVITY = 0.5
RESTITUTION = 0.99
DT = 0.6

# Animation
NUM_FRAMES = 500
FRAME_INTERVAL_MS = 5


# =============================================================================
# Simulation state
# =============================================================================

t = 0
v0 = INITIAL_SPEED
theta = INITIAL_ANGLE
x0, y0 = INITIAL_X, INITIAL_Y


# =============================================================================
# Setup and animation
# =============================================================================

def setup_figure():
    """Create figure, axes, boundary, and ball artist."""
    fig = plt.figure(figsize=(7, 7), dpi=100)
    ax = plt.axes(
        xlim=(-AXIS_PADDING, BOARD_SIZE + AXIS_PADDING),
        ylim=(-AXIS_PADDING, BOARD_SIZE + AXIS_PADDING),
    )
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    physics.draw(ax, RADIUS, CENTER)
    plot_ball, = ax.plot([], [], 'o', mec='k', mfc='w', ms=BALL_RADIUS)
    return fig, plot_ball


def init(plot_ball):
    """Set ball to its initial position."""
    plot_ball.set_data(x0, y0)
    return plot_ball,


def animate(i, plot_ball):
    """Advance simulation by one frame."""
    global t, x0, y0, theta, v0
    t += DT
    xpos, ypos = physics.get_pos(t, theta, x0, y0, v0, GRAVITY)

    effective_rad = RADIUS - BALL_RADIUS
    dist = np.sqrt((xpos - CENTER)**2 + (ypos - CENTER)**2)

    if dist >= effective_rad:
        # Clamp position back onto the boundary surface
        xpos, ypos = physics.clamp_to_boundary(
            xpos, ypos, CENTER, RADIUS, BALL_RADIUS
        )
        # Reflect velocity off the circular wall
        xvel, yvel = physics.get_vel(t, theta, v0, GRAVITY)
        new_vx, new_vy = physics.reflect_velocity(
            xvel, yvel, xpos, ypos, CENTER, RESTITUTION
        )
        # Convert reflected velocity back to speed + angle
        v0 = np.sqrt(new_vx**2 + new_vy**2)
        theta = np.arctan2(new_vy, new_vx)
        # Reset trajectory origin
        t = DT
        x0, y0 = xpos, ypos
        xpos, ypos = physics.get_pos(t, theta, x0, y0, v0, GRAVITY)

    plot_ball.set_data(xpos, ypos)
    return plot_ball,


def main():
    """Run the bounce simulation."""
    fig, plot_ball = setup_figure()

    _anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=lambda: init(plot_ball),
        fargs=(plot_ball,),
        frames=NUM_FRAMES,
        interval=FRAME_INTERVAL_MS,
        blit=True,
        repeat=True,
    )

    plt.show()


if __name__ == "__main__":
    main()
