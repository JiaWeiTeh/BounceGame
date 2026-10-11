# -*- coding: utf-8 -*-
"""Functions to draw the boundary and to move and bounce the ball."""

import numpy as np


def draw(ax, rad, cent, sides=0):
    """
    Draw the boundary on ax: a circle, or a polygon with that many sides.
    """
    if sides == 0:
        angle = np.linspace(0, 2*np.pi, 200)
    else:
        # corners, going all the way round back to the first one
        angle = -np.pi/2 - np.pi/sides + 2*np.pi*np.arange(sides + 1)/sides

    x = rad*np.cos(angle) + cent
    y = rad*np.sin(angle) + cent

    ax.plot(x, y, c='green')


def move(xpos, ypos, xvel, yvel, g, dt):
    """
    Return position and velocity after a time dt, from the trajectory equation.
    """
    # projectile motion, exact for any dt since g is constant
    xpos = xpos + xvel * dt
    ypos = ypos + yvel * dt - 0.5 * g * dt**2
    yvel = yvel - g * dt

    return xpos, ypos, xvel, yvel


def drag(xvel, yvel, k, dt):
    """
    Return velocity after air drag k slows the ball down over a time dt.
    """
    # v -> v * (1-k)^dt, so the total drag doesn't depend on dt
    factor = (1 - k)**dt

    return xvel * factor, yvel * factor


def walls(xpos, ypos, cent, rad, sides):
    """
    Return the walls of the boundary as (nx, ny, a): the outward norm of each
    wall and its distance a from the centre.
    """
    if sides == 0:
        # circle: the wall is the tangent at the point closest to the ball
        dx = xpos - cent
        dy = ypos - cent
        dist = np.sqrt(dx**2 + dy**2)
        if dist == 0:
            # ball exactly in the middle, nowhere near the wall
            return []
        return [(dx/dist, dy/dist, rad)]
    # polygon with its corners on the circle of radius rad, flat side at the
    # bottom. every side faces outwards at its own angle
    angle = -np.pi/2 + 2*np.pi*np.arange(sides)/sides
    a = rad * np.cos(np.pi/sides)

    return [(np.cos(phi), np.sin(phi), a) for phi in angle]


def reflect(xvel, yvel, nx, ny, e, mu):
    """
    Bounce velocity off a wall whose norm (nx, ny) points inwards.
    """
    # 1. split velocity into normal and tangential components
    vn = xvel * nx + yvel * ny
    if vn >= 0:
        # already moving away from the wall
        return xvel, yvel
    vn_x, vn_y = [vn * nx, vn * ny]
    vt_x, vt_y = [xvel - vn_x, yvel - vn_y]
    # 2. reverse normal component (energy loss from e), and slow down
    # tangential component from friction mu
    xvel = (1 - mu) * vt_x - e * vn_x
    yvel = (1 - mu) * vt_y - e * vn_y

    return xvel, yvel


def bounce(xpos, ypos, xvel, yvel, cent, rad, ball_rad, sides, e, mu):
    """
    If the ball touches or goes past a wall, put it back and bounce it off.
    """
    # in a sharp corner (like in a triangle) pushing the ball back from one
    # wall can push it past the other one, so go round the walls a few times
    for i in range(100):
        inside = True
        for nx, ny, a in walls(xpos, ypos, cent, rad, sides):
            # how far the ball is past this wall
            past = (xpos - cent) * nx + (ypos - cent) * ny - (a - ball_rad)
            if past > 1e-9:
                inside = False
                # push ball back onto the wall, then bounce off it
                xpos, ypos = [xpos - past * nx, ypos - past * ny]
                xvel, yvel = reflect(xvel, yvel, -nx, -ny, e, mu)
        if inside:
            break

    return xpos, ypos, xvel, yvel


def step(xpos, ypos, xvel, yvel, cent, rad, ball_rad, sides, g, dt, e, mu,
         k):
    """
    Move the ball by one timestep dt, and bounce it if it hits the boundary.
    """
    xvel, yvel = drag(xvel, yvel, k, dt)
    xpos, ypos, xvel, yvel = move(xpos, ypos, xvel, yvel, g, dt)
    xpos, ypos, xvel, yvel = bounce(xpos, ypos, xvel, yvel,
                                    cent, rad, ball_rad, sides, e, mu)

    return xpos, ypos, xvel, yvel
