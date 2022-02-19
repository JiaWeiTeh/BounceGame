# -*- coding: utf-8 -*-

"""This script describes ball-ball, ball-boundary collision algorithms."""

import matplotlib.pyplot as plt
import numpy as np
from canvas import rad, mid

def collide(pts):
    # 1. check if point is inside circle
    # calculate distance from mid to point
    x, y = pts
    dist = np.sqrt((x-mid)**2 + (y-mid)**2)
    if dist < rad:
        return
    # 2. calculate gradient from point to mid. This will be the 
    # norm of contact point
    norm = (y - mid)/(x - mid)
    # 3. gradient of circular boundary at point of contact
    grad = -1/norm
    # 4. gradient of ball
    grad_ball = y/x
    # 5. collision angle
    theta = np.arctan(abs((grad_ball  - grad)/(1 + grad)))
    return