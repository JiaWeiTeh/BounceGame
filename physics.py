# -*- coding: utf-8 -*-
"""Functions to draw the boundary, and to move and bounce the ball."""

import numpy as np


def draw(ax, rad, cent, sides=0, tilt=0):
    """
    Draw the boundary on ax: a circle, or a polygon with that many sides,
    turned by an angle tilt (in radians).
    """
    if sides == 0:
        angle = np.linspace(0, 2*np.pi, 200)
    else:
        # corners, going all the way round back to the first one
        angle = (-np.pi/2 - np.pi/sides + tilt
                 + 2*np.pi*np.arange(sides + 1)/sides)

    x = rad*np.cos(angle) + cent
    y = rad*np.sin(angle) + cent

    ax.plot(x, y, c='green')


def get_vel(t, theta, vel, g):
    """
    Return velocity component at time t given initial launching angle.
    """
    xvel = vel * np.cos(theta)
    yvel = vel * np.sin(theta) - g * t

    return xvel, yvel


def get_pos(t, theta, x0, y0, vel, g):
    """
    Return position (x,y) at time t given initial launching angle and position.
    """
    xpos = vel * np.cos(theta) * t + x0
    ypos = vel * np.sin(theta) * t - 0.5 * g * t**2 + y0

    return xpos, ypos


def drag(xvel, yvel, k, dt):
    """
    Return velocity after air drag k slows the ball down over a time dt.
    """
    # v -> v * (1-k)^dt, so the total drag doesn't depend on dt
    factor = (1 - k)**dt

    return xvel * factor, yvel * factor


def walls(xpos, ypos, cent, rad, sides, tilt=0):
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
    # polygon with its corners on the circle of radius rad, turned by tilt.
    # with tilt = 0 there is a flat side at the bottom. every side faces
    # outwards at its own angle
    angle = -np.pi/2 + tilt + 2*np.pi*np.arange(sides)/sides
    a = rad * np.cos(np.pi/sides)

    return [(np.cos(phi), np.sin(phi), a) for phi in angle]


def hit(xpos, ypos, cent, rad, ball_rad, sides, tilt=0):
    """
    Check if the ball has gone past any wall of the boundary.
    """
    for nx, ny, a in walls(xpos, ypos, cent, rad, sides, tilt):
        if (xpos - cent) * nx + (ypos - cent) * ny - (a - ball_rad) > 1e-9:
            return True

    return False


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
    # 2. law of restitution: reverse normal component and scale it by e.
    # friction mu slows down the tangential component
    xvel = (1 - mu) * vt_x - e * vn_x
    yvel = (1 - mu) * vt_y - e * vn_y

    return xvel, yvel


def bounce(xpos, ypos, xvel, yvel, cent, rad, ball_rad, sides, e, mu,
           tilt=0):
    """
    If the ball touches or goes past a wall, put it back and bounce it off.
    """
    # in a sharp corner (like in a triangle) pushing the ball back from one
    # wall can push it past the other one, so go round the walls a few times
    for i in range(100):
        inside = True
        for nx, ny, a in walls(xpos, ypos, cent, rad, sides, tilt):
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


def step(t, theta, x0, y0, v0, cent, rad, ball_rad, sides, g, dt, e, mu, k,
         tilt=0):
    """
    Move the ball on by one timestep dt along its trajectory. If it goes past
    the boundary, bounce it off and launch it again from there.

    The ball is (t, theta, x0, y0, v0): time since launch, launch angle,
    launch point and launch speed. Returns the ball after the timestep.
    """
    t = t + dt
    xpos, ypos = get_pos(t, theta, x0, y0, v0, g)
    bounced = hit(xpos, ypos, cent, rad, ball_rad, sides, tilt)

    # with air drag the ball slows down a little every timestep, so it needs
    # a new launch every timestep too. without drag only after a bounce
    if bounced or k > 0:
        xvel, yvel = get_vel(t, theta, v0, g)
        if bounced:
            xpos, ypos, xvel, yvel = bounce(xpos, ypos, xvel, yvel, cent, rad,
                                            ball_rad, sides, e, mu, tilt)
        xvel, yvel = drag(xvel, yvel, k, dt)
        # launch again from here, with t = 0
        t = 0
        theta = np.arctan2(yvel, xvel)
        x0, y0 = [xpos, ypos]
        v0 = np.sqrt(xvel**2 + yvel**2)

    return t, theta, x0, y0, v0
