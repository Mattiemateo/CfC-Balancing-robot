#!/usr/bin/env python3
"""
Fast Balancing Robot PID Calculator
For 11cm tall robot with 75mm wheels
"""

import numpy as np
from scipy.integrate import odeint

# ============= ROBOT PARAMETERS =============
L = 0.11  # COM height (meters)
m = 0.25  # Mass estimate (kg)
g = 9.81  # Gravity
r_wheel = 0.075  # Wheel radius = 75mm (ACTUAL!)

print("╔════════════════════════════════════════════════════════╗")
print("║     Balancing Robot PID Calculator                      ║")
print("╚════════════════════════════════════════════════════════╝\n")

print(f"Robot Parameters:")
print(f"  Height (L):         {L * 100:.0f} cm")
print(f"  Wheel radius (r):   {r_wheel * 1000:.0f} mm")
print(f"  Mass (m):           {m * 1000:.0f} g")
print(f"  Height/Radius:      {L / r_wheel:.2f}x")

# ============= PHYSICS ANALYSIS =============
omega_0 = np.sqrt(g / L)
print(f"\nInverted Pendulum Physics:")
print(
    f"  Natural frequency ω₀ = √(g/L) = {omega_0:.2f} rad/s ({omega_0 / (2 * np.pi):.2f} Hz)"
)

# Key insight: larger wheels mean LARGER control authority
# With 75mm wheels, we have 2.5x more mechanical advantage than 30mm wheels
control_authority = r_wheel / 0.03
print(f"  Wheel leverage:     {control_authority:.1f}x (vs 30mm baseline)")


# ============= INVERTED PENDULUM DYNAMICS =============
def sim_step(state, control_force, dt=0.005):
    """Single simulation step"""
    theta, theta_dot = state

    # Torques:
    # - Gravity: τ_grav = m*g*L*sin(θ)  [destabilizing]
    # - Motor: τ_motor = control_force * r_wheel  [stabilizing]
    # - Inertia: I = m*L²

    tau_grav = m * g * L * np.sin(theta)
    tau_motor = control_force * r_wheel
    tau_net = tau_grav - tau_motor

    I = m * L * L
    theta_ddot = tau_net / I

    # Integrate
    theta_new = theta + theta_dot * dt
    theta_dot_new = theta_dot + theta_ddot * dt

    return np.array([theta_new, theta_dot_new])


# ============= TEST PID GAINS =============
def test_pid(Kp, Kd, Ki, duration=3.0, dt=0.005):
    """Simulate with given PID gains"""
    t = np.arange(0, duration, dt)
    theta = 0.05  # Start 5° tilted
    theta_dot = 0.0
    integral = 0.0

    angles = []
    controls = []

    for time in t:
        angles.append(theta)

        # PID
        error = theta
        p = Kp * error
        d = Kd * theta_dot
        integral += error * dt
        integral = np.clip(integral, -0.1, 0.1)
        i = Ki * integral

        u = p + d + i
        u = np.clip(u, -30, 30)
        controls.append(u)

        # Simulate
        state = sim_step(np.array([theta, theta_dot]), u, dt)
        theta, theta_dot = state

    angles = np.array(angles)
    max_angle = np.max(np.abs(angles))
    final_angle = np.abs(angles[-1])
    settling_idx = np.where(np.abs(angles) < 0.01)[0]
    settling_time = t[settling_idx[0]] if len(settling_idx) > 0 else 999

    stable = final_angle < 0.05  # < 3°

    return {
        "stable": stable,
        "max_angle": max_angle,
        "final_angle": final_angle,
        "settling_time": settling_time,
        "max_control": np.max(np.abs(controls)),
    }


# ============= TUNING CONFIGURATIONS =============
configs = {
    "Light (Kp=20, Kd=3)": (20, 3, 0.05),
    "Moderate (Kp=30, Kd=5)": (30, 5, 0.1),
    "Aggressive (Kp=40, Kd=7)": (40, 7, 0.15),
    "Very Aggressive (Kp=50, Kd=9)": (50, 9, 0.2),
}

print("\n" + "=" * 60)
print("TESTING PID CONFIGURATIONS")
print("=" * 60)

best_config = None
best_score = 999

for name, (kp, kd, ki) in configs.items():
    result = test_pid(kp, kd, ki)

    score = result["settling_time"] + (result["max_angle"] * 5)
    if score < best_score and result["stable"]:
        best_score = score
        best_config = (name, kp, kd, ki)

    status = "✓ STABLE" if result["stable"] else "✗ UNSTABLE"

    print(f"\n{name}")
    print(f"  Status:        {status}")
    print(f"  Max angle:     {np.degrees(result['max_angle']):.1f}°")
    print(f"  Final angle:   {np.degrees(result['final_angle']):.1f}°")
    print(f"  Settling time: {result['settling_time']:.2f}s")
    print(f"  Max control:   {result['max_control']:.1f} N")

# ============= RECOMMENDATION =============
print("\n" + "=" * 60)
print("RECOMMENDED CONFIGURATION")
print("=" * 60)

if best_config:
    name, kp, kd, ki = best_config
    print(f"\n✓ Best tuning: {name}")
    print(f"  Kp = {kp}")
    print(f"  Kd = {kd}")
    print(f"  Ki = {ki}")
    print("\nUse these values in esp32_balancer_v2.ino")
else:
    print("\n⚠ No stable configuration found!")
    print("Try the most aggressive settings and adjust from there")

# ============= UPLOAD INSTRUCTIONS =============
print("\n" + "=" * 60)
print("UPLOAD INSTRUCTIONS")
print("=" * 60)
print(
    """
1. Open esp32_balancer_v2.ino in Arduino IDE

2. Find these lines (around line 40):
   #define Kp 35.0
   #define Kd 5.0
   #define Ki 0.1

3. Replace with your tuned values:
   #define Kp {}
   #define Kd {}
   #define Ki {}

4. Tools → Board → ESP32 Dev Module
5. Tools → Port → Select your COM port
6. Upload

7. Open Serial Monitor (115200 baud)
8. Place robot on ground and wait for "System Ready" message
9. Gently release and observe behavior

TUNING SEQUENCE:
- If oscillating → reduce Kp and Kd by 20%
- If too slow → increase Kp and Kd by 15%
- If drifting → increase Ki (start at 0.05)
""".format(
        best_config[1] if best_config else "30",
        best_config[2] if best_config else "5",
        best_config[3] if best_config else "0.1",
    )
)

print("Good luck! 🤖⚡\n")
