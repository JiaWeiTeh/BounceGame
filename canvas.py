# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np

boardx = 400
boardy = 400

angle = np.linspace(0, 2*np.pi, 200)

# rad, r = sqrt(x^2+y^2)
rad = 180
mid = 200

x = rad*np.cos(angle) + mid
y = rad*np.sin(angle) + mid

fig = plt.figure(figsize = (7,7), dpi = 100)
ax = plt.axes(xlim=(0, boardx), ylim=(0, boardy))
ax.plot(x, y)
plt.show()