# BounceGame

A 2D physics simulation of a ball bouncing inside a circular boundary, built with Python, NumPy, and Matplotlib.

## Features

- Projectile motion with configurable gravity
- Collision detection and vector-based reflection off a circular wall
- Energy loss via coefficient of restitution (applied to normal velocity component)
- Collision friction (tangential energy loss on wall contact)
- Air drag (velocity-dependent resistance during flight)
- Real-time animation using Matplotlib's `FuncAnimation`

## Requirements

- Python 3.8+
- NumPy >= 1.20
- Matplotlib >= 3.4

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The simulation opens a Matplotlib window showing a ball bouncing inside a green circle. Close the window to exit.

## Configuration

All simulation parameters are defined as constants at the top of `main.py`:

| Constant | Default | Description |
|---|---|---|
| `BOARD_SIZE` | 800 | Size of the coordinate space |
| `RADIUS` | 340 | Radius of the circular boundary |
| `BALL_MARKER_SIZE` | 10 | Visual size of the ball (marker size in points) |
| `BALL_COLLISION_RADIUS` | 10 | Collision offset from boundary (data coordinates) |
| `INITIAL_SPEED` | 10 | Launch speed |
| `INITIAL_ANGLE` | 20° | Launch angle (set via `np.deg2rad`) |
| `GRAVITY` | 0.3 | Gravitational acceleration |
| `RESTITUTION` | 0.9 | Coefficient of restitution for normal component (0–1) |
| `FRICTION` | 0.05 | Tangential energy loss on wall collision (0–1) |
| `AIR_DRAG` | 0.005 | Air resistance coefficient (0–1) |
| `DT` | 0.6 | Simulation timestep per frame |

## Running Tests

```bash
pip install pytest
pytest
```

## License

MIT
