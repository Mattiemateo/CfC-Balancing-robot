/*
 * ESP32 Two-Wheel Self-Balancing Robot Controller
 * 
 * Hardware:
 * - ESP32 DevKit
 * - MPU6050 IMU (I2C on GPIO21/SDA, GPIO22/SCL)
 * - 2x NEMA17 1.8° Stepper Motors
 * - 2x DRV8825 Motor Drivers
 * - Robot height: ~11cm (center of mass)
 * 
 * Motor Wiring (from schematic):
 * Motor A (Left):  STEP=GPIO16, DIR=GPIO5, EN=GPIO17
 * Motor B (Right): STEP=GPIO12, DIR=GPIO4, EN=GPIO13
 * uStep0/1/2 tied to GND for full-step operation
 */

#include <Wire.h>
#include <MPU6050.h>

// ============= PIN DEFINITIONS =============
// Motor A (Left wheel)
const int MOT_A_STEP = 16;
const int MOT_A_DIR = 5;
const int MOT_A_EN = 17;

// Motor B (Right wheel)
const int MOT_B_STEP = 12;
const int MOT_B_DIR = 4;
const int MOT_B_EN = 13;

// IMU (I2C)
const int IMU_SDA = 21;
const int IMU_SCL = 22;
const int IMU_INT = 15;

// ============= MOTOR PARAMETERS =============
const float STEP_ANGLE = 1.8;  // 1.8° per step (full-step mode)
const float WHEEL_RADIUS = 0.03;  // 3cm wheel radius (adjust to your robot)
const float ROBOT_HEIGHT = 0.11;  // 11cm center of mass height
const float WHEEL_BASE = 0.07;    // ~7cm distance between wheels (estimate)

// Stepper control
const int STEPS_PER_REV = 200;  // 360 / 1.8
const int MAX_STEP_FREQ = 2000; // Max Hz for stepper

// ============= TIMING =============
const unsigned long CONTROL_PERIOD = 5000;  // 5ms = 200Hz control loop
unsigned long lastControlTime = 0;

// ============= IMU DATA =============
MPU6050 mpu;
float accelX, accelY, accelZ;
float gyroX, gyroY, gyroZ;
float pitch = 0.0;        // Pitch angle in radians (0 = upright)
float pitch_rate = 0.0;   // Angular velocity in rad/s

// Complementary filter
const float GYRO_WEIGHT = 0.98;
const float ACCEL_WEIGHT = 0.02;

// ============= PID CONTROLLER =============
// Pre-simulated values for ~11cm balancing robot:
// Derived from inverted pendulum physics: g/L ≈ 9.81/0.11 ≈ 89 rad²/s²
// Critical damping: sqrt(4 * 89) ≈ 19 rad/s

float Kp = 35.0;   // Proportional gain (angle error)
float Kd = 5.0;    // Derivative gain (angular velocity)
float Ki = 0.5;    // Integral gain (small, for long-term balance)
float integral = 0.0;

// ============= MOTOR CONTROL STATE =============
volatile long motorA_steps = 0;
volatile long motorB_steps = 0;
float motorA_speed = 0;  // steps/sec
float motorB_speed = 0;

// ============= SETUP =============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== ESP32 Balancing Robot Controller ===");
  Serial.printf("Control freq: %.1f Hz\n", 1000000.0 / CONTROL_PERIOD);
  Serial.printf("Robot height: %.2f m\n", ROBOT_HEIGHT);
  Serial.printf("Wheel radius: %.3f m\n", WHEEL_RADIUS);
  
  // ---- Motor Setup ----
  pinMode(MOT_A_STEP, OUTPUT);
  pinMode(MOT_A_DIR, OUTPUT);
  pinMode(MOT_A_EN, OUTPUT);
  pinMode(MOT_B_STEP, OUTPUT);
  pinMode(MOT_B_DIR, OUTPUT);
  pinMode(MOT_B_EN, OUTPUT);
  
  // Start with motors disabled
  digitalWrite(MOT_A_EN, LOW);
  digitalWrite(MOT_B_EN, LOW);
  
  // ---- I2C Setup ----
  Wire.begin(IMU_SDA, IMU_SCL);
  Wire.setClock(400000);
  
  // ---- MPU6050 Setup ----
  Serial.print("Initializing MPU6050... ");
  if (!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_16G)) {
    Serial.println("FAILED!");
    while (1) delay(1000);
  }
  Serial.println("OK");
  
  mpu.setDLPFMode(MPU6050_DLPF_6);  // 5Hz low-pass filter
  delay(100);
  
  // ---- Calibrate Gyro ----
  Serial.print("Calibrating gyro (keep still)...");
  calibrateGyro();
  Serial.println(" OK");
  
  Serial.println("\n=== PID Parameters ===");
  Serial.printf("Kp=%.2f, Kd=%.2f, Ki=%.2f\n", Kp, Kd, Ki);
  Serial.println("\n=== Ready to balance! ===\n");
  
  // Give operator time to place robot
  delay(2000);
}

// ============= MAIN LOOP =============
void loop() {
  unsigned long now = micros();
  
  // Update IMU at full rate (non-blocking)
  if (mpu.dataReady()) {
    updateIMU();
  }
  
  // Control loop at fixed period
  if (now - lastControlTime >= CONTROL_PERIOD) {
    lastControlTime = now;
    
    // Calculate control output
    float control_output = calculatePIDControl();
    
    // Convert control output to motor commands
    setMotorSpeeds(control_output);
    
    // Debug output every 50 loops (~250ms)
    static int loop_count = 0;
    if (++loop_count >= 50) {
      loop_count = 0;
      printDebug(control_output);
    }
  }
}

// ============= IMU UPDATE =============
void updateIMU() {
  // Read raw values
  Vector accel = mpu.readRawAccel();
  Vector gyro = mpu.readRawGyro();
  
  // Convert to normalized values
  accelX = accel.XAxis / 2048.0;  // 16G range
  accelY = accel.YAxis / 2048.0;
  accelZ = accel.ZAxis / 2048.0;
  
  gyroX = gyro.XAxis / 65.5;  // 2000°/s range → rad/s
  gyroY = gyro.YAxis / 65.5;
  gyroZ = gyro.ZAxis / 65.5;
  
  // Accel-based pitch (assuming robot tilts forward/backward around X axis)
  // pitch = atan2(accelY, accelZ)
  float accel_pitch = atan2(accelY, sqrt(accelX*accelX + accelZ*accelZ));
  
  // Gyro-based pitch (integrate angular velocity)
  // For Y-axis gyro: positive = nose up
  float dt = CONTROL_PERIOD / 1000000.0;
  float gyro_pitch = pitch + (gyroY * dt);
  
  // Complementary filter
  pitch = GYRO_WEIGHT * gyro_pitch + ACCEL_WEIGHT * accel_pitch;
  pitch_rate = gyroY;
  
  // Constrain pitch to prevent overflow
  if (pitch > M_PI) pitch -= 2*M_PI;
  if (pitch < -M_PI) pitch += 2*M_PI;
}

// ============= PID CONTROLLER =============
float calculatePIDControl() {
  // Error: how far from vertical (0 rad)
  float error = pitch;
  
  // Proportional term
  float p_term = Kp * error;
  
  // Derivative term (damping with gyro rate)
  float d_term = Kd * pitch_rate;
  
  // Integral term (compensate for small constant disturbances)
  integral += error * (CONTROL_PERIOD / 1000000.0);
  integral = constrain(integral, -0.1, 0.1);  // Anti-windup
  float i_term = Ki * integral;
  
  // Total control signal
  float output = p_term + d_term + i_term;
  
  // Limit control output
  output = constrain(output, -30.0, 30.0);
  
  return output;
}

// ============= MOTOR SPEED CONTROL =============
void setMotorSpeeds(float control_output) {
  // control_output in range [-30, 30]
  // Positive = tip forward = move forward
  
  // For differential drive balancing:
  // Both wheels rotate in SAME direction to move forward/backward
  // to counteract tilting
  
  // Convert to motor speed (steps/sec)
  float motor_speed = (control_output / 30.0) * MAX_STEP_FREQ;
  
  // Set both motors (symmetric movement)
  motorA_speed = motor_speed;
  motorB_speed = motor_speed;
  
  // Motor A (left wheel)
  if (motorA_speed > 0) {
    digitalWrite(MOT_A_DIR, HIGH);  // Forward
  } else {
    digitalWrite(MOT_A_DIR, LOW);   // Backward
  }
  
  // Motor B (right wheel)
  if (motorB_speed > 0) {
    digitalWrite(MOT_B_DIR, HIGH);  // Forward
  } else {
    digitalWrite(MOT_B_DIR, LOW);   // Backward
  }
  
  // Generate step pulses (simplified - uses delay)
  // For real implementation, use PWM or interrupt-driven stepping
  enableMotors();
  stepMotors(abs(motorA_speed), abs(motorB_speed));
}

// ============= STEPPER PULSE GENERATION =============
void stepMotors(float freq_a, float freq_b) {
  // This is a simplified implementation
  // For production, use hardware PWM or interrupt-driven stepping
  
  if (freq_a < 1 && freq_b < 1) {
    disableMotors();
    return;
  }
  
  enableMotors();
  
  // Calculate pulse delays (this runs once per control period)
  unsigned long delay_a = (freq_a > 0) ? (1000000 / (2 * freq_a)) : 0;
  unsigned long delay_b = (freq_b > 0) ? (1000000 / (2 * freq_b)) : 0;
  
  // Simple pulse generation
  if (delay_a > 0) {
    digitalWrite(MOT_A_STEP, HIGH);
    delayMicroseconds(1);
    digitalWrite(MOT_A_STEP, LOW);
  }
  
  if (delay_b > 0) {
    digitalWrite(MOT_B_STEP, HIGH);
    delayMicroseconds(1);
    digitalWrite(MOT_B_STEP, LOW);
  }
}

void enableMotors() {
  digitalWrite(MOT_A_EN, HIGH);
  digitalWrite(MOT_B_EN, HIGH);
}

void disableMotors() {
  digitalWrite(MOT_A_EN, LOW);
  digitalWrite(MOT_B_EN, LOW);
}

// ============= CALIBRATION =============
void calibrateGyro() {
  // Take 100 samples and average gyro offset
  const int CALIB_SAMPLES = 100;
  Vector sum = {0, 0, 0};
  
  for (int i = 0; i < CALIB_SAMPLES; i++) {
    if (mpu.dataReady()) {
      Vector gyro = mpu.readRawGyro();
      sum.XAxis += gyro.XAxis;
      sum.YAxis += gyro.YAxis;
      sum.ZAxis += gyro.ZAxis;
      delay(10);
    }
  }
  
  // Store offsets (could be subtracted from gyro readings)
  Serial.printf("\nGyro offsets: X=%.1f Y=%.1f Z=%.1f\n",
    sum.XAxis/CALIB_SAMPLES, sum.YAxis/CALIB_SAMPLES, sum.ZAxis/CALIB_SAMPLES);
}

// ============= DEBUG OUTPUT =============
void printDebug(float control_output) {
  Serial.printf("Pitch: %6.2f° | Rate: %6.2f°/s | Ctrl: %6.1f | ",
    degrees(pitch), degrees(pitch_rate), control_output);
  Serial.printf("MotorA: %6.0f Hz | MotorB: %6.0f Hz\n",
    motorA_speed, motorB_speed);
}
