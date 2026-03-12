# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import functions

# =============================================================================
# Initial setup
# =============================================================================
# Dimension of board
boardx, boardy = [800, 800]
# Radius and center of circle
cent = 400
rad = 340
# draw boundary
fig = plt.figure(figsize = (7,7), dpi = 100)
ax = plt.axes(xlim=(0-200, boardx+200), ylim=(0-200, boardy+200))
ax.xaxis.set_ticks([])
ax.yaxis.set_ticks([])
functions.draw(ax, rad, cent)
# plot ball
plot_ball, = ax.plot([], [], 'o', mec = 'k', mfc = 'w', ms = 10)
# initialize timestep
t = 0
dt = .6   # fast/slow motion by changing dt
# initial velocity
v0 = 10
# launch angle
theta = np.deg2rad(0)
# gravitational acceleration
g = 0.5
# coeff of restitution
e = 0.99
# initial position of ball
x0, y0 = [400,400]

# =============================================================================
# Initial condition
# =============================================================================
    
def init():
    plot_ball.set_data(x0, y0)
    return plot_ball,

# =============================================================================
# Animation
# =============================================================================



def animate(i):
    global t, x0, y0, theta, v0
    t += dt
    xpos, ypos = functions.get_pos(t, theta, x0, y0, v0, g)

    # Effective boundary radius accounting for visual ball size
    ball_radius = 10
    effective_rad = rad - ball_radius

    # Check if ball is outside boundary
    dist = np.sqrt((xpos - cent)**2 + (ypos - cent)**2)
    if dist >= effective_rad:
        # 1. Clamp position back onto the boundary surface
        xpos, ypos = functions.clamp_to_boundary(
            xpos, ypos, cent, rad, ball_radius
        )
        # 2. Get current velocity at moment of collision
        xvel, yvel = functions.get_vel(t, theta, v0, g)
        # 3. Reflect velocity off the circular wall (restitution on normal only)
        new_vx, new_vy = functions.reflect_velocity(
            xvel, yvel, xpos, ypos, cent, e
        )
        # 4. Convert reflected velocity back to speed + angle for equations of motion
        v0 = np.sqrt(new_vx**2 + new_vy**2)
        theta = np.arctan2(new_vy, new_vx)
        # 5. Reset time and origin for the next trajectory segment
        t = dt
        x0, y0 = xpos, ypos
        # 6. Recalculate position for this frame
        xpos, ypos = functions.get_pos(t, theta, x0, y0, v0, g)

    plot_ball.set_data(xpos, ypos)
    return plot_ball,

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=500, #change length of the animation
                               interval=5, # change to slow/fast motion
                                blit=True,
                                repeat = True
                               )

# =============================================================================
# Save movie
# =============================================================================
# path2save = r"./"
# anim.save(path2save+'stage5.mp4', fps=30,
#           extra_args=['-vcodec', 'libx264'])






