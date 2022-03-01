# -*- coding: utf-8 -*-
"""This script draws the boundary"""

import matplotlib.pyplot as plt
import numpy as np


def draw(ax, rad, cent):
    
    angle = np.linspace(0, 2*np.pi, 200)
    
    x = rad*np.cos(angle) + cent
    y = rad*np.sin(angle) + cent
    
    ax.plot(x, y)
