# -*- coding: utf-8 -*-

"""This script plots and tests the location of balls"""

import matplotlib.pyplot as plt


boardx = 100
boardy = 100



fig = plt.figure(figsize = (7,7), dpi = 100)
ax = plt.axes(xlim=(0, boardx), ylim=(0, boardy))
# ax.xaxis.set_ticks([])
# ax.yaxis.set_ticks([])

centerx, centery = [boardx/2,boardy/2]
space_between = 4

def pts(x, y):
    return centerx + x*space_between, centery + y*space_between


#b 
ax.scatter(*pts(-2, 3))
ax.scatter(*pts(-2.5, 3.5))
ax.scatter(*pts(-2.5, 2.5))
ax.scatter(*pts(-2.5, 4.5))
ax.scatter(*pts(-2, 5))
ax.scatter(*pts(-3, 4))
ax.scatter(*pts(-3, 2))
ax.scatter(*pts(-3.5, 2.5))
ax.scatter(*pts(-3.5, 3.5))
ax.scatter(*pts(-4, 3))
ax.scatter(*pts(-1.5, 5.5))


#r
ax.scatter(*pts(0, 1))
ax.scatter(*pts(-.5, 1.5))
ax.scatter(*pts(-1, 2))
ax.scatter(*pts(-1.5, 1.5))
ax.scatter(*pts(-2, 1))

#u
ax.scatter(*pts(0, -1))
ax.scatter(*pts(.5, -.5))
ax.scatter(*pts(.5, -1.5))
ax.scatter(*pts(1, 0))
ax.scatter(*pts(1, -2))
ax.scatter(*pts(1.5, -1.5))
ax.scatter(*pts(2, -1))

#h
ax.scatter(*pts(2, -3))
ax.scatter(*pts(2.5, -2.5))
ax.scatter(*pts(3, -2))
ax.scatter(*pts(3, -4))
ax.scatter(*pts(3.5, -1.5))
ax.scatter(*pts(3.5, -2.5))
ax.scatter(*pts(3.5, -3.5))
ax.scatter(*pts(4, -1))
ax.scatter(*pts(4, -3))
ax.scatter(*pts(4.5, -.5))




