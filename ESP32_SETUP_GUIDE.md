# ESP32 Balancing Robot - Setup Guide

## Quick Start

### Hardware Requirements
- ESP32 DevKit (or compatible board)
- MPU6050 6-axis IMU
- 2× NEMA17 1.8° stepper motors
- 2× DRV8825 stepper driver modules
- 24V power supply (rated for motor current)
- Wheels and mechanical assembly (~11cm COM height)

### Wiring (from your schematic)

**Motor A (Left wheel):**
- STEP → GPIO16
- DIR → GPIO5
- EN → GPIO17

**Motor B (Right wheel):**
- STEP → GPIO12
- DIR → GPIO4
- EN → GPIO13

**MPU6050 IMU:**
- SDA → GPIO21 (I2C data)
- SCL → GPIO22 (I2C clock)
- INT → GPIO15
- VCC → 3.3V
- GND → GND

**DRV8825 Drivers:**
- Both uStep0/1/2 → GND (full-step mode = 1.8°/step)
- Motor connents: A±, B±
- Power: +24V, GND

### Arduino IDE Setup

1. **Install ESP32 Board**
   - File → Preferences
   - Add board manager URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board Manager → Search "esp32" → Install

2. **Install Required Libraries**
   - Tools → Manage Libraries
   - Search and install:
     - `MPU6050` by Jarzebski
     - `Wire` (usually built-in)

3. **Select Board**
   - Tools → Board → ESP32 Dev Module
   - Port → Select your COM port
   - Upload Speed → 921600

### Files Included

- **esp32_balancer.ino** - Initial version with basic stepper control
- **esp32_balancer_v2.ino** - **RECOMMENDED** - Timer-based interrupts for smoother control
- **simulate_pid_values.py** - Inverted pendulum simulation to estimate PID gains
- **ROBOT_CONFIG.h** - Configuration constants and tuning guide

### First Steps

1. **Run the Simulation**
   ```bash
   python3 simulate_pid_values.py
   ```
   This will:
   - Calculate optimal PID gains for your robot height
   - Simulate different tuning configurations
   - Output settling times and stability metrics
   - Show which gains to try first

2. **Upload Firmware**
   - Open `esp32_balancer_v2.ino` in Arduino IDE
   - Click Upload
   - Open Serial Monitor (115200 baud)

3. **Calibration**
   - Robot will calibrate IMU at startup
   - Wait for "System Ready - Place Robot!" message
   - Place robot on level surface in starting position

4. **Testing Phase** (SAFETY FIRST!)
   - Have a catch net or soft landing zone
   - Start with very gentle perturbations
   - Gradually increase challenge as confidence grows
   - Keep one hand ready to catch

### Tuning Your Robot

**Start with default values:**
```cpp
Kp = 35.0   // Proportional
Kd = 5.0    // Derivative
Ki = 0.1    // Integral (small!)
```

**If oscillating too much:**
```cpp
Kp = 28.0
Kd = 4.0
```

**If response too slow:**
```cpp
Kp = 42.0
Kd = 6.5
```

**Detailed tuning procedure in ROBOT_CONFIG.h**

### Serial Monitor Output

```
┌─ BALANCE STATE ─────────────────────┐
│ Pitch: -2.34°  Rate: -45.62°/s   │
│ Control: 15.32 N (Kp,Kd=35,5) │
│ Motors:  1250 Hz   1250 Hz       │
│ Status: ✓ BALANCED                  │
└─────────────────────────────────────┘
```

### Motor Control Logic

- **Positive control output** → Both wheels rotate forward
- **Negative control output** → Both wheels rotate backward
- **Magnitude** → How fast the wheels turn

The robot uses "inverted pendulum" dynamics:
- When tipped forward → wheels move forward
- This shifts center of mass forward → restores balance

### Troubleshooting

**Motor not spinning:**
- Check DRV8825 power (24V on motor side)
- Verify GPIO pins match your wiring
- Try `motorTest()` function in debugging section

**Unrealistic pitch angles:**
- MPU6050 mounted upside down?
- Accelerometer drifting at startup?
- Check sensor values in Serial Monitor

**Unstable/oscillating:**
- Reduce Kp and Kd by 20%
- Check mechanical alignment (wheels parallel?)
- Verify control loop frequency is 200Hz

**Too slow to respond:**
- Increase Kp and Kd by 15%
- Check for deadband affecting low speeds
- Verify motor directions (wrong direction = instability)

### Physics Background

For a balancing robot:
- Height L = 0.11m
- Natural frequency = √(g/L) ≈ 9.4 rad/s
- Critical damping coefficient = 2√(g/L) ≈ 19 rad/s
- Recommended Kd ≈ 2.5-5× critical damping for practical motors

The PID values in the code are derived from inverted pendulum theory and reduced by 30-40% to account for:
- Discrete stepper steps (1.8° quantization)
- Motor response nonlinearity
- Sensor noise and delays
- Mechanical friction

### Next Steps for Improvement

1. **Sensor Fusion**
   - Add wheel encoders for speed control
   - Use Kalman filter for better angle estimation

2. **Learning Control**
   - Log sensor data during balancing
   - Train a neural network (like your CfC model!)
   - Use learned model for more robust control

3. **Advanced Features**
   - Remote control (Bluetooth/WiFi)
   - Multi-robot synchronization
   - Obstacle avoidance with ultrasonic sensors

### References

- ESP32 Datasheet: https://www.espressif.com/
- MPU6050 Datasheet: https://invensense.tdk.com/
- DRV8825 Driver: https://www.pololu.com/product/2753
- Inverted Pendulum Theory: "Control Systems Engineering" - Norman S. Nise

### Support

If you have issues:
1. Check the troubleshooting section above
2. Review ROBOT_CONFIG.h detailed comments
3. Run simulation to verify expected behavior
4. Post your serial monitor output and describe the behavior

Good luck! 🤖⚡
