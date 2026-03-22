"""
ESP32 Balancing Robot - MicroPython Version
PID Controller with MPU6050 IMU and stepper motors
"""
ESP32 Balancing Robot - MicroPython Version
PID Controller with MPU6050 IMU and stepper motors
"""

import machine
import math
import time
from machine import I2C, Pin

# ============= PIN DEFINITIONS =============
MOT_A_STEP = Pin(16, Pin.OUT)
MOT_A_DIR = Pin(5, Pin.OUT)
MOT_A_EN = Pin(17, Pin.OUT)

MOT_B_STEP = Pin(12, Pin.OUT)
MOT_B_DIR = Pin(4, Pin.OUT)
MOT_B_EN = Pin(13, Pin.OUT)

# I2C
try:
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    print("I2C initialized")
except Exception as e:
    print(f"I2C error: {e}")
    i2c = None

# ============= CONSTANTS =============
WHEEL_RADIUS = 0.075
ROBOT_HEIGHT = 0.11
CONTROL_FREQ = 200

# PID gains
Kp = 20.0
Kd = 3.0
Ki = 0.05

# ============= MPU6050 =============
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.gyro_offset = [0, 0, 0]
        
        try:
            self.init_device()
            print("MPU6050 initialized")
        except Exception as e:
            print(f"MPU6050 init error: {e}")
    
    def init_device(self):
        # Wake up
        self.i2c.writeto(self.addr, bytes([0x6B, 0x00]))
        time.sleep(0.1)
        # DLPF
        self.i2c.writeto(self.addr, bytes([0x1A, 0x06]))
        time.sleep(0.1)
    
    def read_accel(self):
        try:
            data = self.i2c.readfrom_mem(self.addr, 0x3B, 6)
            ax = ((data[0] << 8) | data[1]) / 2048.0
            ay = ((data[2] << 8) | data[3]) / 2048.0
            az = ((data[4] << 8) | data[5]) / 2048.0
            return ax, ay, az
        except:
            return 0, 0, 1
    
    def read_gyro(self):
        try:
            data = self.i2c.readfrom_mem(self.addr, 0x43, 6)
            gx = ((data[0] << 8) | data[1]) / 65.5 * 3.14159 / 180.0
            gy = ((data[2] << 8) | data[3]) / 65.5 * 3.14159 / 180.0
            gz = ((data[4] << 8) | data[5]) / 65.5 * 3.14159 / 180.0
            return gx, gy, gz
        except:
            return 0, 0, 0

# ============= STEPPER CONTROL =============
class StepperMotor:
    def __init__(self, step_pin, dir_pin, en_pin):
        self.step = step_pin
        self.dir = dir_pin
        self.en = en_pin
        self.en.off()
    
    def set_speed(self, speed):
        """speed in steps/sec, positive=forward"""
        try:
            if speed > 0:
                self.dir.on()
            else:
                self.dir.off()
            
            if abs(speed) > 50:
                self.en.on()
            else:
                self.en.off()
        except:
            pass
    
    def disable(self):
        self.en.off()

# ============= BALANCING CONTROLLER =============
class BalancingRobot:
    def __init__(self):
        self.mpu = MPU6050(i2c) if i2c else None
        self.motor_a = StepperMotor(MOT_A_STEP, MOT_A_DIR, MOT_A_EN)
        self.motor_b = StepperMotor(MOT_B_STEP, MOT_B_DIR, MOT_B_EN)
        
        self.pitch = 0.0
        self.pitch_rate = 0.0
        self.integral = 0.0
        self.last_time = time.time()
        
        self.GYRO_WEIGHT = 0.98
        self.ACCEL_WEIGHT = 0.02
        
        print("Robot initialized")
    
    def update_imu(self):
        if not self.mpu:
            return
        
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        
        if dt < 0.001 or dt > 0.1:
            return
        
        try:
            ax, ay, az = self.mpu.read_accel()
            gx, gy, gz = self.mpu.read_gyro()
            
            # Pitch from accel
            accel_pitch = math.atan2(ay, math.sqrt(ax*ax + az*az))
            
            # Pitch from gyro
            gyro_pitch = self.pitch + gy * dt
            
            # Complementary filter
            self.pitch = self.GYRO_WEIGHT * gyro_pitch + self.ACCEL_WEIGHT * accel_pitch
            self.pitch_rate = gy
            
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
                
                now = time.time()
                if now - last_print > 0.5:
                    last_print = now
                    pitch_deg = self.pitch * 180 / 3.14159
                    rate_deg = self.pitch_rate * 180 / 3.14159
                    print(f"Pitch: {pitch_deg:6.1f}° | Rate: {rate_deg:6.1f}°/s | Ctrl: {control:6.1f}")
                
                time.sleep(control_period)
        
        except KeyboardInterrupt:
            print("Stopped")
            self.motor_a.disable()
            self.motor_b.disable()
        except Exception as e:
            print(f"Error: {e}")
            self.motor_a.disable()
            self.motor_b.disable()

# ============= MAIN =============
if __name__ == "__main__":
    robot = BalancingRobot()
    robot.run()

