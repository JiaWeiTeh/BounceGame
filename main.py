# -*- coding: utf-8 -*-
"""
Ball bouncing inside a circular boundary, or a triangle, square, etc.

Run `python main.py` to watch it, `python main.py --shape square` for another
shape, or `python main.py --save bounce.gif` to save it as a video.
"""

import argparse
import os

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import physics

# =============================================================================
# Initial setup
# =============================================================================
# dimension of board
boardx, boardy = [800, 800]
# shape of the boundary ('all' shows every shape side by side), and how many
# sides each one has (0 for a circle)
shape = 'circle'
sides = {'circle': 0, 'triangle': 3, 'square': 4, 'pentagon': 5,
         'hexagon': 6, 'octagon': 8}
# angle to turn the shape by, in degrees. None picks a random one each time,
# so the ball doesn't always land on a flat side at the bottom
tilt = None
# center of board, and radius of circle (or distance to the corners of the
# other shapes)
cent = 400
rad = 340
# empty space around the board in the plot
pad = 200
# ball radius (for collisions) and marker size (for plotting, in points)
ball_rad = 10
ball_ms = 10
# initial position of ball
x0, y0 = [cent, cent]
# initial velocity
v0 = 10
# launch angle
theta = np.deg2rad(20)
# gravitational acceleration
g = 0.3
# coeff of restitution
e = 0.9
# friction with the wall, slows the ball along the wall at each bounce
mu = 0.05
# air drag
k = 0.005
# timestep
dt = 0.6   # fast/slow motion by changing dt

# =============================================================================
# Animation
# =============================================================================
frames = 500    # change length of the animation
interval = 5    # change to slow/fast motion

# =============================================================================
# Save movie
# =============================================================================
seconds = 12
steps_per_sec = 50   # timesteps shown per second of video
fps = {'.mp4': 50, '.gif': 25}    # gif timing is only exact at 25 fps
dpi = {'.mp4': 100, '.gif': 70}


def get_args(argv=None):
    """
    Read options from the command line.
    """
    parser = argparse.ArgumentParser(
        description="Ball bouncing inside a circle, or another shape."
    )
    parser.add_argument(
        '--save', metavar='FILE',
        help="save the animation to FILE (.gif, or .mp4 with ffmpeg) "
             "instead of opening a window",
    )
    parser.add_argument(
        '--seconds', type=float, default=seconds,
        help="length of the saved video in seconds (default: %(default)s)",
    )
    parser.add_argument(
        '--shape', choices=list(sides) + ['all'], default=shape,
        help="shape of the boundary, or all of them side by side "
             "(default: %(default)s)",
    )
    parser.add_argument(
        '--tilt', type=float, default=tilt, metavar='DEG',
        help="angle to turn the shape by, in degrees (default: random)",
    )
    return parser.parse_args(argv)


def get_writer(path):
    """
    Return movie writer and dpi based on the file extension.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.gif':
        return animation.PillowWriter(fps=fps[ext]), dpi[ext]
    if ext == '.mp4':
        if not animation.writers.is_available('ffmpeg'):
            raise SystemExit(
                "Saving .mp4 needs ffmpeg. Install it, or save a .gif instead."
            )
        writer = animation.FFMpegWriter(
            fps=fps[ext], extra_args=['-movflags', '+faststart'],
        )
        return writer, dpi[ext]
    raise SystemExit(f"Cannot save '{path}': use a .gif or .mp4 name.")


def main(argv=None):
    args = get_args(argv)

    if args.save:
        writer, save_dpi = get_writer(args.save)
        plt.switch_backend('Agg')   # draw off screen, no window
        # gif has fewer frames per second, so move more timesteps per frame
        steps = steps_per_sec // writer.fps
        nframes = max(1, round(args.seconds * writer.fps))
    else:
        steps = 1
        nframes = frames

    # shapes to show: just one, or all of them side by side
    if args.shape == 'all':
        shapes = list(sides)
        fig, axes = plt.subplots(2, 3, figsize=(10.5, 7), dpi=100)
        axes = axes.flatten()
    else:
        shapes = [args.shape]
        fig = plt.figure(figsize=(7, 7), dpi=100)
        axes = [plt.axes()]

    balls = []
    turns = []
    plot_balls = []
    for shape, ax in zip(shapes, axes):
        # draw boundary
        ax.set_xlim(0-pad, boardx+pad)
        ax.set_ylim(0-pad, boardy+pad)
        ax.xaxis.set_ticks([])
        ax.yaxis.set_ticks([])
        if len(shapes) > 1:
            # panels are small, so zoom in on the shape
            ax.set_xlim(cent-rad-30, cent+rad+30)
            ax.set_ylim(cent-rad-30, cent+rad+30)
            ax.set_aspect('equal')
            ax.set_title(shape)
        deg = args.tilt
        if deg is None:
            deg = np.random.randint(360)
            if sides[shape] > 0 and len(shapes) == 1:
                print(f"{shape} turned by {deg} degrees, "
                      f"use --tilt {deg} to get the same one again")
            elif sides[shape] > 0:
                print(f"{shape} turned by {deg} degrees")
        turns.append(np.deg2rad(deg))
        physics.draw(ax, rad, cent, sides[shape], turns[-1])
        # plot ball
        plot_ball, = ax.plot([], [], 'o', mec='k', mfc='w', ms=ball_ms)
        plot_balls.append(plot_ball)
        # launch ball from (x0, y0) with speed v0 at angle theta
        balls.append([x0, y0, v0 * np.cos(theta), v0 * np.sin(theta)])
    if len(shapes) > 1:
        fig.tight_layout()

    def init():
        for ball, plot_ball in zip(balls, plot_balls):
            plot_ball.set_data([ball[0]], [ball[1]])
        return plot_balls

    def animate(i):
        for j, shape in enumerate(shapes):
            for _ in range(steps):
                balls[j] = physics.step(*balls[j], cent, rad, ball_rad,
                                        sides[shape], g, dt, e, mu, k,
                                        turns[j])
            plot_balls[j].set_data([balls[j][0]], [balls[j][1]])
        return plot_balls

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=nframes,
                                   interval=interval,
                                   blit=True,
                                   repeat=not args.save)

    if args.save:
        anim.save(args.save, writer=writer, dpi=save_dpi)
        plt.close(fig)
        print(f"Saved {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
