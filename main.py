# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import canvas

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
canvas.draw(ax, rad, cent)
ax.xaxis.set_ticks([])
ax.yaxis.set_ticks([])
# plot ball
plot_ball, = ax.plot([], [], 'o', mec = 'k', mfc = 'w', ms = 10)
# initialize timestep
dt = 0
# initial velocity
vel = 10
# launch angle
theta = np.deg2rad(45)
# gravitational acceleration
g = 2
# coeff of restitution
e = 0.9


def get_vel(t, theta):
    """
    Return velocity component at time t given intial launching angle.
    """
    xvel = vel * np.cos(theta)
    yvel = vel * np.sin(theta) - g * t
    
    return xvel, yvel
    
    
def get_pos(t, theta, x0, y0):
    """
    Return position (x,y) at time t given initial launching angle and position.
    
    """
    xpos = vel * np.cos(theta) * t + x0
    ypos = vel * np.sin(theta) * t - 0.5 * g * t**2 + y0
    
    return xpos, ypos

# =============================================================================
# Initial condition
# =============================================================================
    
def init():
    plot_ball.set_data([200,200])
    return plot_ball,

# =============================================================================
# Animation
# =============================================================================

xInit, yInit = [200,200]

def animate(i):
    global dt, xInit, yInit, theta, vel
    dt += .2
    xpos, ypos = get_pos(dt, theta, xInit, yInit)
    
    if (np.sqrt((xpos-mid)**2 + (ypos-mid)**2)) >= (rad-10):
        
        # 2. calculate gradient from point to mid. This will be the 
        # norm of contact point
        norm = (ypos - mid)/(xpos - mid)
        # 3. instantaneous gradient of circular boundary at point of contact
        grad = -1/norm
        # 4. gradient of ball
        grad_ball = ypos/xpos
        # 5. collision angle = reflect + angle w.r.t. horizon
        theta = np.arctan(abs((grad_ball  - grad)/(1 + grad_ball*grad))) +\
            np.arctan(abs(grad))
        # 6. reset t = 0 for equation of motion. Reset also x0, y0
        dt = .2
        xInit, yInit = [xpos, ypos]
        # 7. account for energy loss
        vel *= e
        # 8. recalculate and plot
        xpos, ypos = get_pos(dt, theta, xInit, yInit)
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
path2save = r"/Users/jwt/Documents/Code/Bounce_Game/"
anim.save(path2save+'stage4.mp4', fps=30,
          extra_args=['-vcodec', 'libx264'])






