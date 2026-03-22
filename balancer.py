"""
ESP32 Balancing Robot - MicroPython Version
PID Controller with MPU6050 IMU and stepper motors
"""

import machine
import math
import time
from machine import I2C, Pin, PWM, Timer

# ============= PIN DEFINITIONS =============
MOT_A_STEP = Pin(16, Pin.OUT)
MOT_A_DIR = Pin(5, Pin.OUT)
MOT_A_EN = Pin(17, Pin.OUT)

MOT_B_STEP = Pin(12, Pin.OUT)
MOT_B_DIR = Pin(4, Pin.OUT)
MOT_B_EN = Pin(13, Pin.OUT)

# I2C
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# ============= CONSTANTS =============
WHEEL_RADIUS = 0.075  # 75mm wheels
ROBOT_HEIGHT = 0.11  # 11cm COM height
CONTROL_FREQ = 200  # 200Hz

# PID gains
Kp = 20.0
Kd = 3.0
Ki = 0.05


# ============= MPU6050 =============
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.init_device()

    def init_device(self):
        # Wake up MPU6050
        self.i2c.writeto(self.addr, bytes([0x6B, 0x00]))
        time.sleep(0.1)
        # Set DLPF to 5Hz low-pass
        self.i2c.writeto(self.addr, bytes([0x1A, 0x06]))

    def read_accel(self):
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
        ax = (data[0] << 8 | data[1]) / 2048.0
        ay = (data[2] << 8 | data[3]) / 2048.0
        az = (data[4] << 8 | data[5]) / 2048.0
        return ax, ay, az

    def read_gyro(self):
        data = self.i2c.readfrom_mem(self.addr, 0x43, 6)
        gx = (data[0] << 8 | data[1]) / 65.5 * math.pi / 180.0
        gy = (data[2] << 8 | data[3]) / 65.5 * math.pi / 180.0
        gz = (data[4] << 8 | data[5]) / 65.5 * math.pi / 180.0
        return gx, gy, gz


# ============= STEPPER CONTROL =============
class StepperMotor:
    def __init__(self, step_pin, dir_pin, en_pin):
        self.step = step_pin
        self.dir = dir_pin
        self.en = en_pin
        self.en.off()

    def set_speed(self, speed):
        """speed in steps/sec, positive=forward"""
        if speed > 0:
            self.dir.on()
        else:
            self.dir.off()

        if speed != 0:
            self.en.on()
            freq = int(abs(speed))
            if freq > 0:
                # Simple pulse generation
                period = 1000000 // freq // 2
                for _ in range(1):
                    self.step.on()
                    machine.lightsleep(1)
                    self.step.off()
        else:
            self.en.off()

    def disable(self):
        self.en.off()


# ============= BALANCING CONTROLLER =============
class BalancingRobot:
    def __init__(self):
        self.mpu = MPU6050(i2c)
        self.motor_a = StepperMotor(MOT_A_STEP, MOT_A_DIR, MOT_A_EN)
        self.motor_b = StepperMotor(MOT_B_STEP, MOT_B_DIR, MOT_B_EN)

        self.pitch = 0.0
        self.pitch_rate = 0.0
        self.integral = 0.0
        self.last_time = time.time()

        # Complementary filter
        self.GYRO_WEIGHT = 0.98
        self.ACCEL_WEIGHT = 0.02

        print("Balancing Robot initialized")

    def update_imu(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if dt < 0.001 or dt > 0.1:
            return

        try:
            ax, ay, az = self.mpu.read_accel()
            gx, gy, gz = self.mpu.read_gyro()

            # Pitch from accel
            accel_pitch = math.atan2(ay, math.sqrt(ax * ax + az * az))

            # Pitch from gyro integration
            gyro_pitch = self.pitch + gy * dt

            # Complementary filter
            self.pitch = self.GYRO_WEIGHT * gyro_pitch + self.ACCEL_WEIGHT * accel_pitch
            self.pitch_rate = gy

            # Constrain
            if self.pitch > math.pi:
                self.pitch -= 2 * math.pi
            if self.pitch < -math.pi:
                self.pitch += 2 * math.pi

        except Exception as e:
            print(f"IMU error: {e}")

    def calculate_control(self):
        error = self.pitch
        p = Kp * error
        d = Kd * self.pitch_rate

        self.integral += error * 0.005
        self.integral = max(-0.1, min(0.1, self.integral))
        i = Ki * self.integral

        u = p + d + i
        u = max(-30, min(30, u))

        return u

    def set_motor_speeds(self, control):
        freq = abs(control) / 30.0 * 2000.0

        if control > 0:
            self.motor_a.set_speed(freq)
            self.motor_b.set_speed(freq)
        else:
            self.motor_a.set_speed(-freq)
            self.motor_b.set_speed(-freq)

    def run(self):
        print("Starting balance control...")
        control_period = 1.0 / CONTROL_FREQ
        last_print = time.time()

        try:
            while True:
                self.update_imu()
                control = self.calculate_control()
                self.set_motor_speeds(control)

                # Debug output every 250ms
                now = time.time()
                if now - last_print > 0.25:
                    last_print = now
                    pitch_deg = math.degrees(self.pitch)
                    rate_deg = math.degrees(self.pitch_rate)
                    print(
                        f"Pitch: {pitch_deg:6.2f}° | Rate: {rate_deg:6.2f}°/s | Ctrl: {control:6.1f}N"
                    )

                time.sleep(control_period)

        except KeyboardInterrupt:
            print("Stopped")
            self.motor_a.disable()
            self.motor_b.disable()


# ============= MAIN =============
if __name__ == "__main__":
    robot = BalancingRobot()
    robot.run()
