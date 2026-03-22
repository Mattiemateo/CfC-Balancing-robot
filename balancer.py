"""
ESP32 Balancing Robot - MicroPython Version
PID Controller with MPU6050 IMU and stepper motors
"""
ESP32 Balancing Robot - MicroPython Version
"""

import machine
import time
from machine import I2C, Pin

print("Starting...")

try:
    # Initialize pins
    MOT_A_STEP = Pin(16, Pin.OUT)
    MOT_A_DIR = Pin(5, Pin.OUT)
    MOT_A_EN = Pin(17, Pin.OUT)
    
    MOT_B_STEP = Pin(12, Pin.OUT)
    MOT_B_DIR = Pin(4, Pin.OUT)
    MOT_B_EN = Pin(13, Pin.OUT)
    
    print("Pins initialized")
    
    # Initialize I2C
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    print("I2C initialized")
    
    # Try to detect MPU6050
    devices = i2c.scan()
    print(f"I2C devices found: {devices}")
    
    if 0x68 in devices:
        print("MPU6050 found at 0x68")
        # Wake up MPU6050
        i2c.writeto(0x68, bytes([0x6B, 0x00]))
        time.sleep(0.1)
        print("MPU6050 initialized")
    else:
        print("MPU6050 not found! Check wiring.")
    
    print("All systems initialized successfully")
    print("Ready for balancing")
    
except Exception as e:
    print(f"Error during initialization: {e}")
    import traceback
    traceback.print_exc()


