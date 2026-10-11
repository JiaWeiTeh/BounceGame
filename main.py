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
BALL_MARKER_SIZE = 10       # visual marker size in points
BALL_COLLISION_RADIUS = 10  # collision offset in data coordinates
INITIAL_SPEED = 10
INITIAL_ANGLE = np.deg2rad(20)
INITIAL_X, INITIAL_Y = CENTER, CENTER

# Physics
GRAVITY = 0.3
RESTITUTION = 0.9
FRICTION = 0.05           # tangential energy loss on wall collision (0–1)
AIR_DRAG = 0.005          # air resistance coefficient (0–1)
DT = 0.6

# Animation
NUM_FRAMES = 500
FRAME_INTERVAL_MS = 5


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
    plot_ball, = ax.plot([], [], 'o', mec='k', mfc='w', ms=BALL_MARKER_SIZE)
    return fig, plot_ball


def main():
    """Run the bounce simulation."""
    fig, plot_ball = setup_figure()

    # Mutable simulation state, captured by the closures below
    state = {
        'x': float(INITIAL_X),
        'y': float(INITIAL_Y),
        'vx': INITIAL_SPEED * np.cos(INITIAL_ANGLE),
        'vy': INITIAL_SPEED * np.sin(INITIAL_ANGLE),
    }

    def init():
        plot_ball.set_data([state['x']], [state['y']])
        return plot_ball,

    def animate(_frame):
        state['x'], state['y'], state['vx'], state['vy'] = physics.step(
            state['x'], state['y'], state['vx'], state['vy'],
            dt=DT,
            gravity=GRAVITY,
            center=CENTER,
            radius=RADIUS,
            ball_radius=BALL_COLLISION_RADIUS,
            restitution=RESTITUTION,
            friction=FRICTION,
            drag=AIR_DRAG,
        )
        plot_ball.set_data([state['x']], [state['y']])
        return plot_ball,

    _anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=NUM_FRAMES,
        interval=FRAME_INTERVAL_MS,
        blit=True,
        repeat=True,
    )

    plt.show()


if __name__ == "__main__":
    main()
