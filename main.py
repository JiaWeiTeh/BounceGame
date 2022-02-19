# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import canvas




boardx, boardy = [400, 400]

# draw canvas
fig = plt.figure(figsize = (7,7), dpi = 100)
ax = plt.axes(xlim=(0-200, boardx+200), ylim=(0-200, boardy+200))
ax.xaxis.set_ticks([])
ax.yaxis.set_ticks([])
# customise colours of ball and bars here by changing the keyword mfc
plot_ball, = ax.plot([], [], 'o', mec = 'k', mfc = 'w', ms = 10)
canvas.draw(ax)

rad = 180
mid = 200
dt = 0
vel = 10
theta = np.deg2rad(45)
g = 2
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

xcon, ycon = [200,200]

def animate(i):
    global dt, xcon, ycon, theta, vel
    dt += .2
    xpos = vel * np.cos(theta) * dt + xcon
    ypos = vel * np.sin(theta) * dt - 0.5 * g * dt**2 + ycon
    
    if (np.sqrt((xpos-mid)**2 + (ypos-mid)**2)) >= rad:
        xcon, ycon = [xpos, ypos]
        
        # 2. calculate gradient from point to mid. This will be the 
        # norm of contact point
        norm = (ypos - mid)/(xpos - mid)
        # 3. gradient of circular boundary at point of contact
        grad = -1/norm
        # 4. gradient of ball
        grad_ball = (vel * np.sin(theta) - g * dt)/(vel * np.cos(theta))
        # 5. collision angle
        theta = np.arctan(abs((grad_ball  - grad)/(1 + grad_ball*grad))) + np.arctan(grad_ball)
        dt = .2
        vel *= e
        xpos = vel * np.cos(theta) * dt + xcon
        ypos = vel * np.sin(theta) * dt - 0.5 * g * dt**2 + ycon
        
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
# anim.save(path2save+'stage3.mp4', fps=30,
#           extra_args=['-vcodec', 'libx264'])






