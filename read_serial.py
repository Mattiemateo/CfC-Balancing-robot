#!/usr/bin/env python3
"""Read serial output from ESP32"""

import serial
import sys
import time


def read_serial(port, baud=115200):
    try:
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2)
        print(f"Connected to {port} at {baud} baud\nCtrl+C to exit\n")

        while True:
            if ser.in_waiting:
                print(ser.read().decode("utf-8", errors="ignore"), end="", flush=True)
    except KeyboardInterrupt:
        print("\nDisconnected")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            ser.close()
        except:
            pass


if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbserial-11230"
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    read_serial(port, baud)
