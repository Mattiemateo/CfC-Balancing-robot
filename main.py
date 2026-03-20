from numpy import *
import math
import csv
import random

def pendulum_step(theta, theta_dot, U, dt=0.01, L=0.15, g=9.81):
    theta_ddot = (g * sin(theta) - U * cos(theta)) / L
    # theta = current tilt angle in radians 0 = perfectly straight, positive = forward
    # theta_ddot = angular acceleration. How quickly the tilt is speeding up or slowing down.
    # g * sin(theta) = gravity term. When theta is small, little fall but increases. when 0 no effect
    # u * cos(theta) = control term. when upright cos(theta) = almost 1, so almost full authority, decrases if falling
    # L = the distance from the wheel contact point with ground to center of gravity in meter
    theta_dot = theta_dot + theta_ddot *dt
    theta = theta + theta_dot *dt
    return theta, theta_dot

def pid(theta, theta_dot, kp=120.0, kd=25.0):
    return (kp * theta + kd * theta_dot)

theta = 0.1
theta_dot = 0.0
log =[]

for start in [0.05, 0.1, 0.15, 0.2, 0.25, -0.05, -0.1, -0.15, -0.2]:
    theta = start
    theta_dot = 0.0
    for step in range(100000):
        # random disturbance every ~100 steps
        if random.random() < 0.01:
            theta_dot += random.uniform(-1.5, 1.5)
        
        u = pid(theta, theta_dot)
        theta, theta_dot = pendulum_step(theta, theta_dot, u)
        
        if abs(theta) > 0.001 or abs(u) > 0.01:
            log.append([theta, theta_dot, u])

with open('balance_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['theta', 'theta_dot', 'u'])
    writer.writerows(log)

print(f'saved {len(log)} rows')
