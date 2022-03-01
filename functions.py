# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np


def draw(ax):
    
    boardx = 400
    boardy = 400
    
    angle = np.linspace(0, 2*np.pi, 200)
    
    rad = 180
    mid = 200
    
    x = rad*np.cos(angle) + mid
    y = rad*np.sin(angle) + mid
    
    ax.plot(x, y)
