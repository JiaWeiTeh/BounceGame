# -*- coding: utf-8 -*-
"""Bouncing ball simulation inside a circular boundary.

Animates a ball with projectile motion, gravity, and energy loss
on collision with the circular wall.
"""

import argparse
import os

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

# Saved video (python main.py --save FILE)
VIDEO_SECONDS = 12
VIDEO_STEPS_PER_SECOND = 50    # simulation steps shown per second of video
VIDEO_FPS = {'.mp4': 50, '.gif': 25}  # GIF timing is exact at 25 fps
VIDEO_DPI = {'.mp4': 100, '.gif': 80}


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


def parse_args(argv=None):
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        description="Animate a ball bouncing inside a circular wall."
    )
    parser.add_argument(
        '--save', metavar='FILE',
        help="save the animation to FILE (.gif, or .mp4 with ffmpeg) "
             "instead of opening a window",
    )
    parser.add_argument(
        '--seconds', type=float, default=VIDEO_SECONDS,
        help="length of the saved video in seconds (default: %(default)s)",
    )
    return parser.parse_args(argv)


def make_writer(path):
    """Return a Matplotlib movie writer and dpi for the file extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in VIDEO_FPS:
        raise SystemExit(f"Cannot save '{path}': use a .gif or .mp4 name.")
    fps = VIDEO_FPS[ext]
    if ext == '.gif':
        return animation.PillowWriter(fps=fps), VIDEO_DPI[ext]
    if not animation.writers.is_available('ffmpeg'):
        raise SystemExit(
            "Saving .mp4 needs ffmpeg. Install it, or save a .gif instead."
        )
    writer = animation.FFMpegWriter(
        fps=fps, extra_args=['-movflags', '+faststart'],
    )
    return writer, VIDEO_DPI[ext]


def main(argv=None):
    """Run the bounce simulation in a window, or save it to a file."""
    args = parse_args(argv)
    if args.save:
        writer, dpi = make_writer(args.save)
        plt.switch_backend('Agg')  # render off screen, no window
        steps_per_frame = VIDEO_STEPS_PER_SECOND // writer.fps
        frames = max(1, round(args.seconds * writer.fps))
    else:
        steps_per_frame = 1
        frames = NUM_FRAMES

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
        for _ in range(steps_per_frame):
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

    anim = animation.FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=frames,
        interval=FRAME_INTERVAL_MS,
        blit=True,
        repeat=not args.save,
    )

    if args.save:
        anim.save(args.save, writer=writer, dpi=dpi)
        plt.close(fig)
        print(f"Saved {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
