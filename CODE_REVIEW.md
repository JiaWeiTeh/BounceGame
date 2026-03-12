# Comprehensive Code Review: BounceGame

## 1. CRITICAL BUGS

### 1.1 Division by Zero — `main.py:61`
```python
norm = (ypos - cent)/(xpos - cent)
```
When `xpos == cent` (ball is directly above or below the center), this causes a **ZeroDivisionError** crash. This is a real scenario — the ball can easily pass through `x=400`.

### 1.2 Division by Zero — `main.py:65`
```python
grad_ball = ypos/xpos
```
If `xpos` ever reaches `0`, this crashes. More fundamentally, this formula is **mathematically wrong** — the gradient of the ball's path is not `ypos/xpos`. That's the slope of the line from the *origin* to the ball, not the ball's direction of travel. The ball's gradient should be derived from its velocity components: `yvel/xvel`.

### 1.3 Division by Zero — `main.py:69`
```python
theta_iBC = ... abs(np.arctan(abs((grad_ball - grad)/(1 + grad_ball*grad))))
```
When `grad_ball * grad == -1` (perpendicular lines), this produces a division by zero. Should use `np.arctan2` or guard the denominator.

### 1.4 Reflection Angle Logic is Incomplete — `main.py:77-90`
The branching only handles four cases:
- `xvel > 0 and xpos > cent`
- `xvel < 0 and xpos > cent`
- `xvel > 0 and xpos < cent`
- `xvel < 0 and xpos < cent`

**Missing cases:**
- `xvel == 0` (ball moving purely vertically) — no branch handles this, `theta` is never updated, and the ball will behave unpredictably.
- `xpos == cent` (ball at center x) — overlaps with the division-by-zero in line 61.
- `yvel` direction is never considered, meaning the reflection is only correct for some quadrants. The ball can reflect in wrong directions.

### 1.5 Ball Escapes Boundary — `main.py:58`
```python
if (np.sqrt((xpos-cent)**2 + (ypos-cent)**2)) >= (rad-20):
```
The collision detection only checks *after* position update. If `dt` is large enough or velocity is high, the ball can overshoot significantly past the boundary in a single frame. There is no clamping or projection back onto the boundary surface — `x0, y0` are set to the *overshooting* position (line 93), meaning the ball's next trajectory starts from *outside* the circle.

### 1.6 Incorrect `theta` Logic — `main.py:82-88`
```python
if theta > np.pi:
    theta = np.pi - theta      # results in a NEGATIVE angle
elif theta < np.pi:
    theta = (3/2) * np.pi + theta
elif theta == np.pi:
    theta = 0
```
When `theta > np.pi`, `np.pi - theta` yields a **negative angle**, which is almost certainly unintended. Floating-point comparison `theta == np.pi` (line 87) will virtually never be `True`.

---

## 2. PHYSICS / CORRECTNESS ISSUES

### 2.1 Gravity Units are Undocumented — `main.py:32`, `functions.py:33`
```python
g = 0.5
ypos = vel * np.sin(theta) * t - 0.5 * g * t**2 + y0
```
`g = 0.5` is an arbitrary constant with no documented unit. This makes the physics non-physical and hard to reason about or tune.

### 2.2 Coefficient of Restitution Applied to Total Velocity — `main.py:95`
```python
v0 *= e
```
In real physics, the coefficient of restitution applies only to the **normal component** of velocity (perpendicular to the surface), not the entire velocity magnitude. Applying it to total `v0` causes the ball to lose energy in the tangential direction as well, making it decelerate laterally when it shouldn't.

### 2.3 Hardcoded Ball Radius Offset — `main.py:58`
```python
(rad-20)  # -10 due to ball's radius
```
The comment says `-10` but the code uses `-20`. This is a discrepancy. Furthermore, the visual ball size (`ms=10` in matplotlib marker size on line 23) is in **points**, not in data coordinates. The offset of 20 in data units bears no actual relationship to the ball's visual radius — it will look different at different figure sizes/DPIs.

---

## 3. CODE QUALITY & BAD PRACTICES

### 3.1 Heavy Use of Global Mutable State — `main.py:53`
```python
global t, x0, y0, theta, v0, g, dt
```
Seven global variables are mutated inside `animate()`. This is a major anti-pattern:
- Makes the code impossible to test in isolation.
- Makes it extremely hard to reason about state changes.
- Prevents running multiple simulations concurrently.
- `g` and `dt` are declared global but never reassigned — they don't need to be global.

**Recommendation:** Encapsulate all simulation state in a class (e.g., `BallSimulation`) and pass it to the animation function.

### 3.2 No Separation of Concerns
- Physics logic, rendering logic, and configuration are all tangled together in `main.py`.
- The `animate()` function does collision detection, angle calculation, velocity updates, position updates, and rendering — all in one 50-line function.
- The collision/reflection logic (lines 58–100) should be in `functions.py`.

### 3.3 Magic Numbers Everywhere
| Value | Location | Issue |
|-------|----------|-------|
| `800` | main.py:12 | Board dimensions |
| `400` | main.py:14 | Center |
| `340` | main.py:15 | Radius |
| `200` | main.py:18 | Axis padding |
| `0.6` | main.py:26 | Timestep |
| `10` | main.py:28 | Initial velocity |
| `0.5` | main.py:32 | Gravity |
| `0.99` | main.py:34 | Restitution coefficient |
| `20` | main.py:58 | Ball radius offset |
| `500` | main.py:108 | Frame count |
| `5` | main.py:109 | Animation interval |

None are named constants or configurable.

### 3.4 Inconsistent Naming
- `cent` — abbreviated, should be `center` or `center_xy`.
- `rad` — abbreviated, should be `radius`.
- `e` — extremely poor variable name; `e` typically means Euler's number in math/science contexts. Should be `restitution` or `cor`.
- `boardx, boardy` — but the board is a circle, not a rectangle. These are axis limits, not "board" dimensions.

### 3.5 `functions.py` Module Name is Too Generic
The module is named `functions` which is meaningless. Better names: `physics`, `simulation`, `ball_physics`, `geometry`.

### 3.6 `functions.py` Docstring is Misleading — `functions.py:2`
```python
"""This script draws the boundary"""
```
The module does much more than draw — it also computes velocity and position. The docstring is stale/incomplete.

---

## 4. NON-CONVENTIONAL PRACTICES

### 4.1 No `if __name__ == "__main__":` Guard — `main.py`
All code runs at module import level. This means:
- You can't import `main.py` without executing the entire simulation.
- You can't write tests for any function in `main.py`.
- IDE tools that inspect imports will trigger the animation.

### 4.2 Module-Level Side Effects — `location.py`
`location.py` creates figures and plots points at import time. Same issue as above.

### 4.3 No Type Hints
None of the functions use Python type annotations. For a physics simulation, type hints would significantly improve readability.

### 4.4 Inconsistent Whitespace and Formatting
- `main.py:18`: `0-200` is valid but unconventional; `-200` is clearer.
- `main.py:109`: Misaligned indentation in `FuncAnimation` arguments.
- Trailing blank lines at end of files (main.py has 5, location.py has 3).
- Inconsistent spacing around `=` in keyword arguments (PEP 8 says no spaces around `=` in keyword args).

### 4.5 Using `abs()` Excessively — `main.py:69-73`
Triple-nested `abs()` calls are a code smell — they mask sign errors rather than handling geometry correctly. The reflection algorithm should use vector math (dot products, cross products) instead of manually computing angles. This approach loses quadrant information.

---

## 5. MISSING PROJECT INFRASTRUCTURE

### 5.1 No `requirements.txt` or `pyproject.toml`
Dependencies (`numpy`, `matplotlib`) are not documented.

### 5.2 No `.gitignore`
`__pycache__/`, `.pyc`, IDE config, and OS files can easily be committed.

### 5.3 README is Empty
No description, installation instructions, screenshots, or usage guide.

### 5.4 No Tests
Zero test files. The physics functions are easily unit-testable but have no tests.

### 5.5 No Linting / Formatting Config
No `.flake8`, `pyproject.toml` with ruff/black config, or pre-commit hooks.

---

## 6. `location.py` SPECIFIC ISSUES

### 6.1 Dead/Orphan Code
This file is not referenced by `main.py` or any other file. It appears to spell out "bruh" using scatter points. It should either be removed or moved to an `examples/` directory.

### 6.2 Massively Repetitive Code — `location.py:26-65`
40 individual `ax.scatter()` calls. This should be data-driven:
```python
b_points = [(-2, 3), (-2.5, 3.5), ...]
for p in b_points:
    ax.scatter(*pts(*p))
```

---

## 7. PRIORITY SUMMARY

| Priority | Issue | Recommendation |
|----------|-------|----------------|
| **P0** | Division by zero crashes (3 locations) | Add zero-guards or use `atan2` |
| **P0** | Wrong ball gradient formula | Use `yvel/xvel` from velocity |
| **P0** | Missing `xvel==0` / `xpos==cent` cases | Handle edge cases in reflection |
| **P1** | Ball escapes boundary | Clamp position to boundary on collision |
| **P1** | Global mutable state | Refactor to a class-based design |
| **P1** | Restitution applied to total velocity | Apply only to normal component |
| **P2** | Magic numbers | Extract to named constants or config |
| **P2** | No `__main__` guard | Wrap execution code |
| **P2** | No requirements.txt | Add dependency file |
| **P2** | Generic module name | Rename `functions.py` to `physics.py` |
| **P3** | No tests | Add unit tests for physics functions |
| **P3** | No `.gitignore` | Add standard Python gitignore |
| **P3** | Vector-based reflection | Replace angle arithmetic with vector math |
