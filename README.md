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

When the ball hits a wall, one equation sets its new velocity:

```math
\mathbf{v}' = (1 - \mu)\,\mathbf{v} - (1 - \mu + e)\,(\mathbf{v} \cdot \hat{\mathbf{n}})\,\hat{\mathbf{n}}
```

Here $\hat{\mathbf{n}}$ is the unit vector pointing out of the wall, into the
board. $e$ is the coefficient of restitution and $\mu$ is the friction with
the wall. The part of the velocity going into the wall is reversed and scaled
by $e$, and the part along the wall is scaled by $1 - \mu$. With $e = 1$ and
$\mu = 0$ it becomes a perfect mirror bounce,
$\mathbf{v}' = \mathbf{v} - 2(\mathbf{v} \cdot \hat{\mathbf{n}})\,\hat{\mathbf{n}}$.
In flight, air drag also scales the speed by $(1 - k)$ per unit of time.

The shape of the boundary only changes $\hat{\mathbf{n}}$. In a circle it
points from the ball towards the centre. In a polygon it is fixed for each
side. That is why every shape uses the same code.

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

To bounce the ball around a different shape:

```bash
python main.py --shape triangle
```

The shapes are `circle`, `triangle`, `square`, `pentagon`, `hexagon` and
`octagon`. Each run turns the shape to a random angle, so the ball does not
always land on a flat side at the bottom. The angle is printed, and `--tilt`
sets it in degrees. For example, `--tilt 0` puts a flat side at the bottom.

## Save a video

```bash
python main.py --save bounce.gif
python main.py --save bounce.mp4 --seconds 20
python main.py --save square.gif --shape square --tilt 45
```

GIF works out of the box. MP4 needs [ffmpeg](https://ffmpeg.org), for
example `brew install ffmpeg` or `conda install -c conda-forge ffmpeg`.
Clips last 12 seconds unless you pass `--seconds`. The demo above was
made with `python main.py --save assets/bounce.gif`.

## Settings

Edit the values at the top of `main.py`. The main ones are:

| Name | Default | Meaning |
|---|---|---|
| `shape` | `'circle'` | Shape of the boundary, also set with `--shape` |
| `tilt` | `None` | Angle to turn the shape by, in degrees. `None` picks a random angle each run |
| `rad` | 340 | Radius of the circle, or distance from the centre to the corners of other shapes |
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
