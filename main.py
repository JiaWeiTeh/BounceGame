# -*- coding: utf-8 -*-
"""
Ball bouncing inside a circular boundary.

Run `python main.py` to watch it, or `python main.py --save bounce.gif` to
save it as a video.
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
# radius and center of circle
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
dpi = {'.mp4': 100, '.gif': 80}


def get_args(argv=None):
    """
    Read options from the command line.
    """
    parser = argparse.ArgumentParser(
        description="Ball bouncing inside a circular boundary."
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

    # draw boundary
    fig = plt.figure(figsize=(7, 7), dpi=100)
    ax = plt.axes(xlim=(0-pad, boardx+pad), ylim=(0-pad, boardy+pad))
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    physics.draw(ax, rad, cent)
    # plot ball
    plot_ball, = ax.plot([], [], 'o', mec='k', mfc='w', ms=ball_ms)
    # launch ball from (x0, y0) with speed v0 at angle theta
    xpos, ypos = [x0, y0]
    xvel, yvel = [v0 * np.cos(theta), v0 * np.sin(theta)]

    def init():
        plot_ball.set_data([xpos], [ypos])
        return plot_ball,

    def animate(i):
        nonlocal xpos, ypos, xvel, yvel
        for _ in range(steps):
            xpos, ypos, xvel, yvel = physics.step(xpos, ypos, xvel, yvel,
                                                  cent, rad, ball_rad,
                                                  g, dt, e, mu, k)
        plot_ball.set_data([xpos], [ypos])
        return plot_ball,

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
