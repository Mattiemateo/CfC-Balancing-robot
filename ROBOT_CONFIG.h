/*
 * BALANCING ROBOT - CONFIGURATION GUIDE
 * Customize these parameters for your specific robot
 */

// ============= PHYSICAL PARAMETERS =============
// CRITICAL: Measure or estimate these accurately!

// Center of mass height from ground to wheel contact
// Measure from wheel axle center to the highest point of your robot
// Example measurements:
//   - 11cm = reasonable estimate
//   - 9cm = shorter robot (stiffer, faster response)
//   - 13cm = taller robot (longer period, slower response)
#define ROBOT_HEIGHT_M 0.11

// Wheel radius - measure your actual wheel
// Affects how motor speed translates to linear movement
#define WHEEL_RADIUS_M 0.03

// Distance between wheel centers
#define WHEEL_BASE_M 0.07

// Robot mass estimate (with batteries)
// Used for torque calculations in simulation
#define ROBOT_MASS_KG 0.25

// ============= STEPPER MOTOR PARAMETERS =============
// NEMA17 specifications
#define STEPPER_ANGLE_DEG 1.8         // Holding angle per full step
#define STEPPER_MICROSTEP_MODE 1      // 1=full, 2=half, 4=1/4, 8=1/8 step
#define STEPPER_RATED_CURRENT_A 1.5   // A (for torque estimation)

// Effective steps per revolution at chosen microstep mode
#define STEPS_PER_REV (200 / STEPPER_MICROSTEP_MODE)

// Motor driver frequency limits
#define MIN_STEP_FREQ 50              // Hz - below this, motor won't turn
#define MAX_STEP_FREQ 2000            // Hz - DRV8825 max safe frequency

// ============= PID TUNING PARAMETERS =============
// These are derived from simulation for 11cm height
// START HERE when tuning your robot!

// Theoretical base values from inverted pendulum:
//   ω₀ = sqrt(g/L) = sqrt(9.81/0.11) = 9.4 rad/s
//   For critical damping: Kp ≈ g/L = 89, Kd ≈ 2*sqrt(g/L) = 19

// Practical tuning (reduced 30-40% for motor nonlinearity):
#define Kp_DEFAULT 35.0    // Proportional gain
#define Kd_DEFAULT 5.0     // Derivative gain
#define Ki_DEFAULT 0.1     // Integral gain (small!)

// For tuning: start conservative, increase Kp/Kd if too slow
#define Kp_AGGRESSIVE 40.0
#define Kd_AGGRESSIVE 8.0
#define Kp_CONSERVATIVE 25.0
#define Kd_CONSERVATIVE 3.5

// ============= FILTER PARAMETERS =============
// Complementary filter: combines fast gyro with stable accel
// Higher GYRO_WEIGHT = trust gyro more (faster response, more drift)
// Lower GYRO_WEIGHT = trust accel more (stable, more lag)
#define GYRO_WEIGHT 0.98      // 98% gyro, 2% accel (typical)
#define ACCEL_WEIGHT (1.0 - GYRO_WEIGHT)

// IMU low-pass filter mode
// Options: MPU6050_DLPF_0 (260Hz) to MPU6050_DLPF_6 (5Hz)
// DLPF_6 recommended (5Hz low-pass)
#define IMU_DLPF_MODE MPU6050_DLPF_6

// ============= CONTROL LOOP PARAMETERS =============
#define CONTROL_FREQ_HZ 200            // Must be 200+ Hz for stability
#define CONTROL_PERIOD_US (1000000 / CONTROL_FREQ_HZ)

// Integral error anti-windup limits
#define INTEGRAL_MAX 0.5
#define INTEGRAL_MIN -0.5

// Control output limits (Nm or equivalent force units)
#define CONTROL_OUTPUT_MAX 30.0
#define CONTROL_OUTPUT_MIN -30.0

// Dead-band: commands below this are ignored (prevents jitter)
#define MOTOR_DEADBAND_HZ 50

// ============= GAIN TUNING STRATEGY =============
/*
 * STEP-BY-STEP TUNING PROCEDURE:
 * 
 * 1. INITIAL SETUP
 *    - Use Kp=35, Kd=5, Ki=0.1
 *    - Verify IMU is reading reasonable values
 *    - Check motors spin correctly
 * 
 * 2. MANUAL HOLDING TEST
 *    - Power on with robot in hand
 *    - Don't release yet
 *    - You should feel gentle corrections trying to level
 *    - If strong jerking → Kp/Kd too high, reduce by 30%
 *    - If barely reacts → Kp/Kd too low, increase by 20%
 * 
 * 3. RELEASE TEST
 *    - On a soft surface or with safety setup
 *    - Gently release from slightly tilted position
 *    - Observe reaction:
 * 
 *    A) Robot oscillates wildly or falls immediately
 *       → Reduce Kp and Kd by 20-30%
 *       → Check motor directions (might be reversed)
 * 
 *    B) Robot recovers but very slowly (>2 seconds)
 *       → Increase Kp by 10-20%
 *       → May need to increase Kd slightly too
 * 
 *    C) Robot balances but drifts forward/backward
 *       → Increase Ki gradually (start at 0.05, go to 0.2)
 *       → Check wheel friction and motor alignment
 * 
 *    D) Perfect balance (rare on first try!)
 *       → You've found the sweet spot
 *       → Write down your values
 * 
 * 4. FINE TUNING (if needed)
 *    - Make small changes: ±5% at a time
 *    - Test several times to confirm stability
 *    - If still oscillating: increase Kd more than Kp
 *    - If response too sluggish: increase Kp more than Kd
 * 
 * TIPS:
 * - Always have a catch mechanism (net, cushion)
 * - Never leave running unattended
 * - Shorter test runs at first
 * - Take video to analyze movement afterward
 */

// ============= MOTOR DIRECTION CONFIGURATION =============
// If robot tips the WRONG way after release:
// 1. Check MOT_A_DIR and MOT_B_DIR pin logic
// 2. May need to flip both directions
// 3. Or swap A and B motor assignments

// ============= SENSOR CALIBRATION =============
// MPU6050 offset values (calibrated at startup)
// These are printed to serial during boot
// You can optionally hard-code them if needed:
// #define GYRO_OFFSET_X 10.5
// #define GYRO_OFFSET_Y -3.2
// #define GYRO_OFFSET_Z 1.8

// ============= DEBUGGING HELP =============
/*
 * COMMON PROBLEMS:
 * 
 * Problem: "Robot falls immediately"
 * - Check: Motor directions (should move forward when tilted forward)
 * - Check: Sensor orientation (make sure MPU6050 is mounted correctly)
 * - Solution: Reduce Kp from 35 to 20
 * 
 * Problem: "Oscillates around balance point"
 * - Check: Is Kd too low?
 * - Solution: Increase Kd from 5 to 8
 * - Solution: Reduce Kp slightly (from 35 to 30)
 * 
 * Problem: "Drifts slowly in one direction"
 * - Check: Motor alignment (both wheels parallel?)
 * - Check: Wheel slippage or friction
 * - Solution: Increase Ki from 0.1 to 0.3
 * 
 * Problem: "Jerky, not smooth"
 * - Check: Are motors getting enough power?
 * - Check: Stepper frequency too low (reduce CONTROL_FREQ_HZ?)
 * - Solution: Increase MIN_STEP_FREQ threshold
 * 
 * Problem: "IMU values seem wrong"
 * - Check: I2C connections (SDA/SCL)
 * - Check: MPU6050 address (default 0x68)
 * - Check: Power supply stable?
 * - Solution: Run i2c scanner to verify address
 * 
 * Problem: "Compiles but won't upload"
 * - Check: Board selected = "ESP32 Dev Module"
 * - Check: COM port correct
 * - Check: MPU6050 library installed
 * - Solution: Install Jarzebski's MPU6050 library via Arduino IDE
 */

// ============= SIMULATION RESULTS REFERENCE =============
/*
 * Based on simulate_pid_values.py results:
 * 
 * For ROBOT_HEIGHT = 0.11m:
 *   Natural frequency ω₀ ≈ 9.4 rad/s
 *   Settling time with Kp=35, Kd=5: ~0.5s
 *   Max overshoot: ~12° with this tuning
 * 
 * Expected behavior:
 *   - Release from 15° tilt
 *   - Robot should stabilize within 1 second
 *   - Small oscillations should damp out quickly
 *   - Steady-state error < 1° without disturbance
 * 
 * If real robot doesn't match simulation:
 *   - Motor response may be nonlinear
 *   - Sensor noise higher than assumed
 *   - Mechanical friction not modeled
 *   - Center of mass location different
 * 
 * To improve matching:
 *   1. Remeasure ROBOT_HEIGHT precisely
 *   2. Use video analysis of tilt angle (measure pixel movement)
 *   3. Adjust simulation friction/damping parameters
 *   4. Re-run simulation with new robot model
 */
