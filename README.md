# BounceGame

A small hobby project. I'm interested in the trajectory of a ball bouncing
around inside a circle, and wanted to see if I could still implement the
high school maths behind it and visualise it with Python and Matplotlib.

![Ball bouncing inside a circular wall](assets/bounce.gif)

## The maths

Between bounces the ball follows one trajectory equation, projectile motion
under gravity:

```math
x = x_0 + v_x t, \qquad y = y_0 + v_y t - \tfrac{1}{2} g t^2
```

Each frame moves the ball along this parabola for one timestep. When the ball
reaches the wall, its velocity is split into the part pointing into the wall
and the part along it. The part into the wall is reversed, and the ball sets
off on a new parabola. Restitution, wall friction and air drag each take a
little energy away, so the bounces slowly die down.

## Install

You need Python 3.10 or newer.

```bash
git clone https://github.com/JiaWeiTeh/BounceGame.git
cd BounceGame
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

No git? Click **Code → Download ZIP** on GitHub, unzip it, and run the last
three commands inside the folder. If `python` is not found, use `python3`.

## Run

```bash
python main.py
```

A window opens with the animation. Close it to stop.

## Save a video

```bash
python main.py --save bounce.gif
python main.py --save bounce.mp4 --seconds 20
```

GIF works out of the box. MP4 needs [ffmpeg](https://ffmpeg.org), for
example `brew install ffmpeg` or `conda install -c conda-forge ffmpeg`.
Clips last 12 seconds unless you pass `--seconds`. The demo above was
made with `python main.py --save assets/bounce.gif`.

## Settings

Edit the values at the top of `main.py`. The main ones are:

| Name | Default | Meaning |
|---|---|---|
| `rad` | 340 | Radius of the circular boundary |
| `ball_rad` | 10 | Ball radius used for collisions |
| `ball_ms` | 10 | Drawn ball size, in points |
| `v0` | 10 | Launch speed |
| `theta` | 20° | Launch angle above horizontal |
| `g` | 0.3 | Gravitational acceleration |
| `e` | 0.9 | Coeff of restitution: share of speed into the wall kept per bounce (0–1) |
| `mu` | 0.05 | Friction: share of speed along the wall lost per bounce (0–1) |
| `k` | 0.005 | Air drag: share of speed lost per unit time in flight (0–1) |
| `dt` | 0.6 | Timestep per frame |

Units are arbitrary: distances are plot coordinates and time is simulation
time.

## Files

- `main.py` holds the settings, draws the board and runs the animation.
- `physics.py` holds the functions for the motion, bounce and drag.
- `test_physics.py` and `test_main.py` hold the tests.
- `assets/bounce.gif` is the demo animation.

## Test

```bash
pip install -r requirements-dev.txt
pytest
```

## License

MIT. See [LICENSE](LICENSE).
