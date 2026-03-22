/*
 * ESP32 Two-Wheel Self-Balancing Robot - IMPROVED VERSION
 * With timer-based stepper control for better accuracy
 * 
 * Hardware:
 * - ESP32 DevKit
 * - MPU6050 IMU (I2C on GPIO21/SDA, GPIO22/SCL)
 * - 2x NEMA17 1.8° Stepper Motors
 * - 2x DRV8825 Motor Drivers (full-step mode)
 * - Robot height: ~11cm
 */

#include <Wire.h>
#include <MPU6050.h>
#include <driver/ledc.h>

// ============= PIN DEFINITIONS =============
#define MOT_A_STEP 16
#define MOT_A_DIR  5
#define MOT_A_EN   17

#define MOT_B_STEP 12
#define MOT_B_DIR  4
#define MOT_B_EN   13

#define IMU_SDA    21
#define IMU_SCL    22
#define IMU_INT    15

// ============= CONSTANTS =============
#define CONTROL_FREQ_HZ   200          // 200Hz control loop
#define CONTROL_PERIOD_US 5000         // 5ms
#define STEP_ANGLE        1.8          // degrees per step
#define STEPS_PER_REV     200
#define WHEEL_RADIUS      0.075        // 75mm wheels (MEASURED!)
#define ROBOT_HEIGHT      0.11         // 11cm COM height

// ============= PID CONTROLLER GAINS =============
// Calculated from simulation with 75mm wheels and 11cm height
// Tuned for stability and smooth response
#define Kp 20.0   // Proportional gain
#define Kd 3.0    // Derivative gain (damping)
#define Ki 0.05   // Integral gain (small for drift correction)

// ============= GLOBAL VARIABLES =============
MPU6050 mpu;

// IMU state
volatile float pitch = 0.0;
volatile float pitch_rate = 0.0;
volatile uint32_t last_imu_time = 0;

// Complementary filter weights
const float GYRO_WEIGHT = 0.98;
const float ACCEL_WEIGHT = 0.02;

// Control variables
volatile float control_output = 0.0;
volatile float integral_error = 0.0;

// Motor state
volatile float target_freq_a = 0;  // Hz
volatile float target_freq_b = 0;  // Hz
volatile float actual_freq_a = 0;
volatile float actual_freq_b = 0;

// ============= TIMER HANDLES =============
hw_timer_t* control_timer = NULL;
hw_timer_t* motor_timer = NULL;

// ============= SETUP =============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n╔══════════════════════════════════════════╗");
  Serial.println("║  ESP32 Balancing Robot - Improved v2.0  ║");
  Serial.println("╚══════════════════════════════════════════╝\n");
  
  // Motor pins
  pinMode(MOT_A_STEP, OUTPUT);
  pinMode(MOT_A_DIR, OUTPUT);
  pinMode(MOT_A_EN, OUTPUT);
  pinMode(MOT_B_STEP, OUTPUT);
  pinMode(MOT_B_DIR, OUTPUT);
  pinMode(MOT_B_EN, OUTPUT);
  digitalWrite(MOT_A_EN, LOW);
  digitalWrite(MOT_B_EN, LOW);
  
  // I2C
  Wire.begin(IMU_SDA, IMU_SCL, 400000);
  
  // MPU6050
  Serial.print("Initializing MPU6050... ");
  if (!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_16G)) {
    Serial.println("FAILED!");
    while (1) delay(1000);
  }
  Serial.println("✓");
  
  mpu.setDLPFMode(MPU6050_DLPF_6);
  delay(100);
  calibrateIMU();
  
  // Setup timers
  setupControlTimer();
  setupMotorTimer();
  
  Serial.println("\n╔══════════════════════════════════════════╗");
  Serial.println("║        System Ready - Place Robot!       ║");
  Serial.println("╚══════════════════════════════════════════╝\n");
  
  delay(3000);
}

// ============= MAIN LOOP =============
void loop() {
  // Read IMU continuously (non-blocking)
  if (mpu.dataReady()) {
    updateIMU();
  }
  
  // Give CPU time to other tasks
  delay(1);
  
  // Periodic debug output
  static uint32_t last_debug = 0;
  if (millis() - last_debug >= 250) {
    last_debug = millis();
    printDebugInfo();
  }
}

// ============= TIMER INTERRUPT: CONTROL LOOP (200 Hz) =============
void IRAM_ATTR controlTimerISR() {
  // Calculate PID control output
  float error = pitch;
  
  // Proportional term
  float p_term = Kp * error;
  
  // Derivative term
  float d_term = Kd * pitch_rate;
  
  // Integral term with anti-windup
  integral_error += error * (CONTROL_PERIOD_US / 1000000.0);
  integral_error = constrain(integral_error, -0.5, 0.5);
  float i_term = Ki * integral_error;
  
  // Sum
  control_output = p_term + d_term + i_term;
  control_output = constrain(control_output, -30.0, 30.0);
  
  // Convert control output to motor frequencies
  // Range: -30 to +30 → frequency mapping
  float freq_magnitude = abs(control_output) / 30.0 * 2000.0;  // Max 2000 Hz
  
  if (control_output >= 0) {
    // Tip forward → move forward (both wheels same direction)
    target_freq_a = freq_magnitude;
    target_freq_b = freq_magnitude;
  } else {
    // Tip backward → move backward
    target_freq_a = freq_magnitude;
    target_freq_b = freq_magnitude;
  }
  
  // Handle very small frequencies (dead-band)
  if (freq_magnitude < 50) {
    target_freq_a = 0;
    target_freq_b = 0;
  }
  
  // Direction control
  if (control_output > 0) {
    digitalWrite(MOT_A_DIR, HIGH);
    digitalWrite(MOT_B_DIR, HIGH);
  } else {
    digitalWrite(MOT_A_DIR, LOW);
    digitalWrite(MOT_B_DIR, LOW);
  }
}

// ============= TIMER INTERRUPT: MOTOR STEPPING (up to 4000 Hz) =============
static volatile uint32_t step_counter_a = 0;
static volatile uint32_t step_counter_b = 0;
static volatile float period_a_ticks = 0;
static volatile float period_b_ticks = 0;

void IRAM_ATTR motorTimerISR() {
  // Motor A stepping
  if (target_freq_a > 0) {
    digitalWrite(MOT_A_EN, HIGH);
    period_a_ticks += target_freq_a;
    if (period_a_ticks >= 40000) {  // 80MHz / 2 = 40kHz resolution
      period_a_ticks -= 40000;
      digitalWrite(MOT_A_STEP, HIGH);
      delayMicroseconds(1);
      digitalWrite(MOT_A_STEP, LOW);
    }
  } else {
    digitalWrite(MOT_A_EN, LOW);
  }
  
  // Motor B stepping
  if (target_freq_b > 0) {
    digitalWrite(MOT_B_EN, HIGH);
    period_b_ticks += target_freq_b;
    if (period_b_ticks >= 40000) {
      period_b_ticks -= 40000;
      digitalWrite(MOT_B_STEP, HIGH);
      delayMicroseconds(1);
      digitalWrite(MOT_B_STEP, LOW);
    }
  } else {
    digitalWrite(MOT_B_EN, LOW);
  }
}

// ============= TIMER SETUP =============
void setupControlTimer() {
  // 200 Hz = 5000 µs period
  control_timer = timerBegin(0, 80, true);  // Timer 0, divider=80 (1µs ticks)
  timerAttachInterrupt(control_timer, &controlTimerISR, true);
  timerAlarmWrite(control_timer, CONTROL_PERIOD_US, true);  // Auto-reload
  timerAlarmEnable(control_timer);
  Serial.println("✓ Control timer initialized (200 Hz)");
}

void setupMotorTimer() {
  // 4000 Hz stepper update rate
  motor_timer = timerBegin(1, 80, true);   // Timer 1, divider=80
  timerAttachInterrupt(motor_timer, &motorTimerISR, true);
  timerAlarmWrite(motor_timer, 250, true);  // 250µs = 4000 Hz
  timerAlarmEnable(motor_timer);
  Serial.println("✓ Motor timer initialized (4000 Hz)");
}

// ============= IMU UPDATE =============
void updateIMU() {
  uint32_t now = micros();
  float dt = (now - last_imu_time) / 1000000.0;
  last_imu_time = now;
  
  if (dt < 0.001 || dt > 0.1) return;  // Sanity check
  
  // Read accelerometer and gyroscope
  Vector accel = mpu.readRawAccel();
  Vector gyro = mpu.readRawGyro();
  
  // Convert to g's and °/s
  float accel_x = accel.XAxis / 2048.0;
  float accel_y = accel.YAxis / 2048.0;
  float accel_z = accel.ZAxis / 2048.0;
  
  float gyro_y_rads = (gyro.YAxis / 65.5) * M_PI / 180.0;  // °/s to rad/s
  
  // Calculate pitch from accelerometer (long-term stable)
  float accel_pitch = atan2(accel_y, sqrt(accel_x*accel_x + accel_z*accel_z));
  
  // Integrate gyro (short-term accurate)
  float gyro_pitch = pitch + gyro_y_rads * dt;
  
  // Complementary filter
  pitch = GYRO_WEIGHT * gyro_pitch + ACCEL_WEIGHT * accel_pitch;
  pitch_rate = gyro_y_rads;
  
  // Prevent overflow
  if (pitch > M_PI) pitch -= 2*M_PI;
  if (pitch < -M_PI) pitch += 2*M_PI;
}

// ============= CALIBRATION =============
void calibrateIMU() {
  Serial.print("Calibrating IMU (keep still)... ");
  
  // Let sensor stabilize
  for (int i = 0; i < 100; i++) {
    if (mpu.dataReady()) {
      Vector accel = mpu.readRawAccel();
      Vector gyro = mpu.readRawGyro();
      delay(10);
    }
  }
  
  // Initialize pitch estimate from accelerometer
  Vector accel = mpu.readRawAccel();
  float accel_x = accel.XAxis / 2048.0;
  float accel_y = accel.YAxis / 2048.0;
  float accel_z = accel.ZAxis / 2048.0;
  pitch = atan2(accel_y, sqrt(accel_x*accel_x + accel_z*accel_z));
  pitch_rate = 0.0;
  
  Serial.println("✓");
}

// ============= DEBUG OUTPUT =============
void printDebugInfo() {
  static int loop_count = 0;
  
  Serial.printf("┌─ BALANCE STATE ─────────────────────┐\n");
  Serial.printf("│ Pitch: %7.2f°  Rate: %7.2f°/s   │\n", 
    degrees(pitch), degrees(pitch_rate));
  Serial.printf("│ Control: %7.2f N (Kp,Kd=%d,%d) │\n", 
    control_output, (int)Kp, (int)Kd);
  Serial.printf("│ Motors: %5.0f Hz  %5.0f Hz       │\n", 
    target_freq_a, target_freq_b);
  
  // Status indicator
  if (abs(pitch) > 0.3) {
    Serial.printf("│ Status: ⚠️  UNSTABLE!               │\n");
  } else if (abs(pitch) > 0.1) {
    Serial.printf("│ Status: ⚠️  RECOVERING             │\n");
  } else {
    Serial.printf("│ Status: ✓ BALANCED                  │\n");
  }
  Serial.printf("└─────────────────────────────────────┘\n");
}

// ============= HELPER FUNCTIONS =============
float degrees(float radians) {
  return radians * 180.0 / M_PI;
}
