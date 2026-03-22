import math
import csv
import random
import numpy as np

import numpy as np

starts = list(np.linspace(-0.3, 0.3, 30))  # 30 evenly spaced angles from -0.3 to +0.3 radians
# add velocity-only starts
starts += [(0.0, v) for v in [-2.0, -1.0, 1.0, 2.0]]

def pendulum_step(theta, theta_dot, U, dt=0.01, L=0.15, g=9.81):
    theta_ddot = (g * np.sin(theta) - U * np.cos(theta)) / L
    # theta = current tilt angle in radians 0 = perfectly straight, positive = forward
    # theta_ddot = angular acceleration. How quickly the tilt is speeding up or slowing down.
    # g * sin(theta) = gravity term. When theta is small, little fall but increases. when 0 no effect
    # u * cos(theta) = control term. when upright cos(theta) = almost 1, so almost full authority, decrases if falling
    # L = the distance from the wheel contact point with ground to center of gravity in meter
    theta_dot = theta_dot + theta_ddot *dt
    theta = theta + theta_dot *dt
    return theta, theta_dot

def pid(theta, theta_dot, kp=40.0, kd=8.0):
    u = kp * theta + kd * theta_dot
    return max(-30.0, min(30.0, u))
        
log =[]

episode_id = 0
for start in starts:
    if isinstance(start, tuple):
        theta, theta_dot = start
    else:
        theta, theta_dot = start, 0.0
    for step in range(3000):
        if random.random() < 0.015:
            theta_dot += random.uniform(-4.0, 4.0)
        
        u = pid(theta, theta_dot)
        theta, theta_dot = pendulum_step(theta, theta_dot, u)
        
        if abs(theta) > 0.005 or abs(u) > 0.5:
            log.append([episode_id, theta, theta_dot, u])  # ← episode_id added
    
    episode_id += 1  # increment at end of each episode

with open('balance_data_extremes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['episode', 'theta', 'theta_dot', 'u'])
    writer.writerows(log)

print(f'saved {len(log)} rows')
