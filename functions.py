# -*- coding: utf-8 -*-
"""This script draws the boundary"""

import numpy as np


def draw(ax, rad, cent):
    
    angle = np.linspace(0, 2*np.pi, 200)
    
    x = rad*np.cos(angle) + cent
    y = rad*np.sin(angle) + cent
    
    ax.plot(x, y, c = 'green')


def get_vel(t, theta, vel, g):
    """
    Return velocity component at time t given intial launching angle.
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