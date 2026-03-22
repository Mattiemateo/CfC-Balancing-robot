#!/usr/bin/env python3
"""
Inverted Pendulum Simulation - Pre-calculate PID values for balancing robot
Simulates a two-wheel robot with stepper motors balancing on an inverted pendulum model
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# ============= ROBOT PARAMETERS =============
# Robot dimensions
L = 0.11  # Center of mass height (11 cm)
m = 0.25  # Estimated robot mass (250g)
g = 9.81  # Gravity
r_wheel = 0.075  # Wheel radius = 75mm (CRITICAL PARAMETER!)

# Motor parameters
R_wheel = 0.03  # Wheel radius (3 cm)
wheel_base = 0.07  # Distance between wheels
STEP_ANGLE = 1.8 * np.pi / 180  # 1.8 degrees in radians
MAX_STEP_FREQ = 2000  # Hz

# ============= PHYSICS PARAMETERS =============
# Inverted pendulum natural frequency
omega_0 = np.sqrt(g / L)  # ~9.4 rad/s
print(f"\nInverted Pendulum Parameters:")
print(f"Height (L): {L} m")
print(f"Natural frequency (ω₀): {omega_0:.2f} rad/s = {omega_0 / (2 * np.pi):.2f} Hz")

# For critical damping: Kp and Kd relationship
# Transfer function: θ(s) / U(s) = (g/L) / (s² - g/L)
# With PID: closed-loop should be approximately: ω₀² / (s² + 2*ζ*ω₀*s + ω₀²)
# For ζ ≈ 1 (critical damping), we want:
# Kp ≈ 2*ζ*ω₀ (makes system critically damped)
# Kd should be chosen to achieve desired bandwidth

# ============= PID TUNING =============
# Pre-calculated values based on physics:
zeta = 1.0  # Critical damping
Kp = zeta * g / L  # Proportional gain
Kd = 2 * zeta * np.sqrt(g / L)  # Derivative gain
Ki = 0.1 * Kp  # Small integral for steady-state

print(f"\nPID Gains (Physics-Based):")
print(f"Kp (proportional):  {Kp:.2f}")
print(f"Kd (derivative):    {Kd:.2f}")
print(f"Ki (integral):      {Ki:.4f}")

# For practical implementation, these often need reduction due to:
# - Motor response limits
# - Stepper discrete stepping
# - Sensor noise
# Suggested practical gains (reduced by 30-40%):
Kp_practical = Kp * 0.35
Kd_practical = Kd * 0.4
Ki_practical = Ki * 0.05

print(f"\nPID Gains (Practical - reduced 30-40%):")
print(f"Kp: {Kp_practical:.2f}")
print(f"Kd: {Kd_practical:.2f}")
print(f"Ki: {Ki_practical:.4f}")


# ============= SIMULATION =============
def inverted_pendulum(state, t, control_force):
    """
    Simulate inverted pendulum dynamics with wheel-based control
    state = [theta, theta_dot]
    theta: tilt angle from vertical (rad)
    theta_dot: angular velocity (rad/s)
    control_force: motor force in N at wheel contact point
    """
    theta, theta_dot = state

    # CORRECTED MODEL:
    # When robot tilts by angle θ:
    #   - Gravity creates restoring torque: τ_grav = -m*g*L*sin(θ)
    #   - Motor applies force F at wheel radius r: τ_motor = F * r
    #
    # Equation of motion (moment of inertia I ≈ m*L² for point mass):
    # I*θ_ddot = m*g*L*sin(θ) + F*r
    #
    # For small angles, sin(θ) ≈ θ:
    # θ_ddot = (g/L)*θ + (r/(m*L²))*F
    #
    # But control should OPPOSE the tilt:
    # If θ > 0 (forward tilt), we apply F > 0 (forward force)
    # which is NEGATIVE feedback: θ_ddot = (g/L)*θ - (gain)*F

    r_wheel = 0.03  # Wheel radius
    I = m * L * L  # Moment of inertia (approx for point mass at COM)

    # Gravity torque (destabilizing, pushes further from vertical)
    tau_grav = m * g * L * np.sin(theta)

    # Motor torque (control input, should stabilize)
    tau_motor = control_force * r_wheel

    # Net torque: gravity destabilizes, motor stabilizes
    tau_net = tau_grav - tau_motor

    # Angular acceleration
    theta_ddot = tau_net / I

    return [theta_dot, theta_ddot]


# ============= SIMULATE DIFFERENT PID VALUES =============
def simulate_balance(Kp_test, Kd_test, Ki_test, duration=5.0, dt=0.005):
    """Simulate balancing with given PID gains"""
    t = np.arange(0, duration, dt)
    states = np.zeros((len(t), 2))
    control = np.zeros(len(t))

    theta, theta_dot = 0.05, 0.0  # Start slightly tilted forward
    integral = 0.0

    for i, time in enumerate(t):
        # Current state
        states[i] = [theta, theta_dot]

        # PID control - stabilize by moving wheels in direction of tilt
        # If θ > 0 (tipped forward), we want u > 0 (move forward)
        # This creates negative feedback: wheel acceleration opposes tilt
        error = theta  # Error is positive when tilted forward

        p_term = Kp_test * error  # Proportional to error
        d_term = Kd_test * theta_dot  # Damping from angular velocity

        integral += error * dt
        integral = np.clip(integral, -0.5, 0.5)  # Anti-windup
        i_term = Ki_test * integral

        u = p_term + d_term + i_term  # Positive u when tilted forward
        control[i] = u

        # Limit control to realistic motor force
        u = np.clip(u, -30, 30)

        # Integrate dynamics over time step
        sol = odeint(inverted_pendulum, [theta, theta_dot], [0, dt], args=(u,))
        theta, theta_dot = sol[-1]

    return t, states, control


# ============= RUN SIMULATIONS =============
print("\n" + "=" * 60)
print("SIMULATING DIFFERENT PID CONFIGURATIONS")
print("=" * 60)

# Test configurations
configs = {
    "Theoretical (full)": (Kp, Kd, Ki),
    "Theoretical (ζ=0.7)": (0.7 * g / L, 2 * 0.7 * np.sqrt(g / L), 0.1 * g / L),
    "Practical (recommended)": (Kp_practical, Kd_practical, Ki_practical),
    "Tuned aggressive": (40, 8, 0.2),
    "Tuned conservative": (25, 5, 0.1),
}

results = {}
fig, axes = plt.subplots(2, len(configs), figsize=(16, 8))

for idx, (name, (kp, kd, ki)) in enumerate(configs.items()):
    print(f"\nSimulating: {name}")
    print(f"  Kp={kp:.2f}, Kd={kd:.2f}, Ki={ki:.4f}")

    t, states, control = simulate_balance(kp, kd, ki, duration=3.0)
    results[name] = (t, states, control)

    # Check stability
    final_angle = np.abs(states[-1, 0])
    max_angle = np.max(np.abs(states[:, 0]))
    settling_idx = np.where(np.abs(states[:, 0]) < 0.01)[0]
    settling_time = t[settling_idx[0]] if len(settling_idx) > 0 else 999

    print(f"  Final angle: {np.degrees(final_angle):.2f}°")
    print(f"  Max angle: {np.degrees(max_angle):.2f}°")
    print(f"  Settling time (<0.57°): {settling_time:.2f}s")

    if final_angle > 0.5:
        print(f"  ⚠️  UNSTABLE - Robot would fall!")
    elif settling_time > 2.0:
        print(f"  ✓ Stable but slow")
    else:
        print(f"  ✓ Good response")

    # Plot
    axes[0, idx].plot(t, np.degrees(states[:, 0]), "b-", linewidth=2)
    axes[0, idx].axhline(y=0, color="k", linestyle="--", alpha=0.3)
    axes[0, idx].set_ylabel("Angle (°)")
    axes[0, idx].set_title(name)
    axes[0, idx].grid(True, alpha=0.3)
    axes[0, idx].set_ylim(-30, 30)

    axes[1, idx].plot(t, control, "r-", linewidth=1.5)
    axes[1, idx].axhline(y=0, color="k", linestyle="--", alpha=0.3)
    axes[1, idx].set_xlabel("Time (s)")
    axes[1, idx].set_ylabel("Control (N)")
    axes[1, idx].grid(True, alpha=0.3)
    axes[1, idx].set_ylim(-35, 35)

plt.suptitle(
    "Inverted Pendulum Simulation - PID Tuning Comparison",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("pid_tuning_comparison.png", dpi=150)
print("\n✓ Saved plot to 'pid_tuning_comparison.png'")

# ============= MOTOR SPEED ANALYSIS =============
print("\n" + "=" * 60)
print("MOTOR SPEED REQUIREMENTS")
print("=" * 60)

t, states, control = results["Practical (recommended)"]
max_control = np.max(np.abs(control))
max_speed_rads = (max_control / 30.0) * MAX_STEP_FREQ  # Convert to rad/s

# Convert stepper speed to wheel speed
wheel_speed_ms = (max_speed_rads / 2 / np.pi) * 2 * np.pi * R_wheel
rpm_stepper = (max_speed_rads / 2 / np.pi) * 60

print(f"\nUsing recommended PID gains:")
print(f"Maximum control output: {max_control:.2f} N")
print(f"Required stepper speed: {max_speed_rads:.0f} rad/s")
print(f"Required stepper speed: {rpm_stepper:.0f} RPM")
print(f"Wheel linear speed: {wheel_speed_ms:.2f} m/s")
print(f"\nDRV8825 can handle up to ~2000 Hz step rate")
print(f"(Adjust MAX_STEP_FREQ in code if needed)")

# ============= PRINT RECOMMENDATIONS =============
print("\n" + "=" * 60)
print("RECOMMENDED IMPLEMENTATION")
print("=" * 60)
print(f"""
For your 11cm tall robot with 1.8° steppers:

1. Use PRACTICAL values in firmware:
   - Kp = {Kp_practical:.2f}
   - Kd = {Kd_practical:.2f}
   - Ki = {Ki_practical:.4f}

2. If robot is oscillating too much:
   - Reduce Kp and Kd by 20-30%
   - Example: Kp=28, Kd=3.2

3. If response is too slow:
   - Increase Kp and Kd by 10-20%
   - Example: Kp=38, Kd=4.8

4. Always start with small Ki (~0.01)
   and only increase if drifting

5. Test sequence:
   - Disable motors (hold robot manually)
   - Enable and gently perturb
   - Observe if it corrects smoothly
   - Adjust gains in small increments

6. Motor control is non-linear due to:
   - Stepper discrete steps (1.8° resolution)
   - Dead-band when speed is very low
   - Maximum step rate limitations
   
   Consider implementing:
   - Minimum step frequency threshold
   - Smooth acceleration/deceleration
   - Microstepping (1/4 or 1/8 step) if needed
""")

plt.show()
