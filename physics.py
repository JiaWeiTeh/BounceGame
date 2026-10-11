# -*- coding: utf-8 -*-
"""Functions to draw the boundary and to move and bounce the ball."""

import numpy as np


def draw(ax, rad, cent):
    """
    Draw the circular boundary on ax.
    """
    angle = np.linspace(0, 2*np.pi, 200)

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


def bounce(xpos, ypos, xvel, yvel, cent, rad, ball_rad, e, mu):
    """
    Put the ball back on the boundary and bounce it off.
    """
    # 1. push ball back onto the boundary, along the line from the centre
    dx = xpos - cent
    dy = ypos - cent
    dist = np.sqrt(dx**2 + dy**2)
    scale = (rad - ball_rad) / dist
    xpos = cent + dx * scale
    ypos = cent + dy * scale
    # 2. norm of contact point, pointing in towards the centre
    nx = cent - xpos
    ny = cent - ypos
    norm = np.sqrt(nx**2 + ny**2)
    nx, ny = [nx/norm, ny/norm]
    # 3. split velocity into normal and tangential components
    vn = xvel * nx + yvel * ny
    vn_x, vn_y = [vn * nx, vn * ny]
    vt_x, vt_y = [xvel - vn_x, yvel - vn_y]
    # 4. reverse normal component (energy loss from e), and slow down
    # tangential component from friction mu
    xvel = (1 - mu) * vt_x - e * vn_x
    yvel = (1 - mu) * vt_y - e * vn_y

    return xpos, ypos, xvel, yvel


def step(xpos, ypos, xvel, yvel, cent, rad, ball_rad, g, dt, e, mu, k):
    """
    Move the ball by one timestep dt, and bounce it if it hits the boundary.
    """
    xvel, yvel = drag(xvel, yvel, k, dt)
    xpos, ypos, xvel, yvel = move(xpos, ypos, xvel, yvel, g, dt)
    # if ball touches or goes past the boundary
    if np.sqrt((xpos - cent)**2 + (ypos - cent)**2) >= rad - ball_rad:
        xpos, ypos, xvel, yvel = bounce(xpos, ypos, xvel, yvel,
                                        cent, rad, ball_rad, e, mu)

    return xpos, ypos, xvel, yvel
