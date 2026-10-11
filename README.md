# BounceGame

A ball bouncing inside a circular wall, animated with Python and Matplotlib.
The ball follows projectile motion under gravity. It loses energy on each
bounce through restitution and wall friction, and slows in flight from air
drag.

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

## Settings

Edit the constants at the top of `main.py`. The main ones are:

| Constant | Default | Meaning |
|---|---|---|
| `RADIUS` | 340 | Radius of the circular wall |
| `BALL_COLLISION_RADIUS` | 10 | Ball radius used for collisions |
| `BALL_MARKER_SIZE` | 10 | Drawn ball size, in points |
| `INITIAL_SPEED` | 10 | Launch speed |
| `INITIAL_ANGLE` | 20° | Launch angle above horizontal |
| `GRAVITY` | 0.3 | Downward acceleration |
| `RESTITUTION` | 0.9 | Share of speed into the wall kept per bounce (0–1) |
| `FRICTION` | 0.05 | Share of speed along the wall lost per bounce (0–1) |
| `AIR_DRAG` | 0.005 | Share of speed lost per unit time in flight (0–1) |
| `DT` | 0.6 | Simulation time per frame |

Units are arbitrary: distances are plot coordinates and time is simulation
time.

## Files

- `main.py` sets up the figure, holds the settings and runs the animation.
- `physics.py` holds the motion, bounce and drag calculations.
- `test_physics.py` holds the unit tests.

## Test

```bash
pip install -r requirements-dev.txt
pytest
```

## License

MIT. See [LICENSE](LICENSE).
