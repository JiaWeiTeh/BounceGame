# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import functions

# =============================================================================
# Initial setup
# =============================================================================
# Dimension of board
boardx, boardy = [400, 400]
# Radius and center of circle
cent = 200
rad = 180
# draw boundary
fig = plt.figure(figsize = (7,7), dpi = 100)
ax = plt.axes(xlim=(0-200, boardx+200), ylim=(0-200, boardy+200))
ax.xaxis.set_ticks([])
ax.yaxis.set_ticks([])
functions.draw(ax, rad, cent)
# plot ball
plot_ball, = ax.plot([], [], 'o', mec = 'k', mfc = 'w', ms = 10)
# initialize timestep
dt = 0
# initial velocity
v0 = 10
# launch angle
theta = np.deg2rad(45)
# gravitational acceleration
g = 2
# coeff of restitution
e = 0.9


# =============================================================================
# Initial condition
# =============================================================================
    
def init():
    plot_ball.set_data([200,200])
    return plot_ball,

# =============================================================================
# Animation
# =============================================================================

x0, y0 = [200,200]

def animate(i):
    global dt, x0, y0, theta, v0, g
    dt += .2
    xpos, ypos = functions.get_pos(dt, theta, x0, y0, v0, g)
    
    if (np.sqrt((xpos-cent)**2 + (ypos-cent)**2)) >= (rad-10):
        
        # 2. calculate gradient from point to mid. This will be the 
        # norm of contact point
        norm = (ypos - cent)/(xpos - cent)
        # 3. instantaneous gradient of circular boundary at point of contact
        grad = -1/norm
        # 4. gradient of ball
        grad_ball = ypos/xpos
        # 5. collision angle = reflect + angle w.r.t. horizon
        theta = np.arctan(abs((grad_ball  - grad)/(1 + grad_ball*grad))) +\
            np.arctan(abs(grad))
        # 6. reset to next(t = 0) for equation of motion. Reset also x0, y0
        dt = .2
        x0, y0 = [xpos, ypos]
        # 7. account for energy loss
        v0 *= e
        # 8. recalculate and plot
        xpos, ypos = functions.get_pos(dt, theta, x0, y0, v0, g)
        plot_ball.set_data(xpos,ypos)
        
        return plot_ball,
    
    plot_ball.set_data(xpos,ypos)
    
    return plot_ball,

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, #change length of the animation
                               interval=20, # change to slow/fast motion
                                blit=True,
                                repeat = True
                               )

# =============================================================================
# Save movie
# =============================================================================
# path2save = r"/Users/jwt/Documents/Code/Bounce_Game/"
# anim.save(path2save+'stage4.mp4', fps=30,
#           extra_args=['-vcodec', 'libx264'])






