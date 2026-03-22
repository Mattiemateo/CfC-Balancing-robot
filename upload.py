#!/usr/bin/env python3
"""Upload MicroPython code to ESP32"""

import sys
import time
import serial
from pathlib import Path


def upload_to_esp32(port, filename):
    """Upload MicroPython file to ESP32"""
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(2)

        # Read file
        with open(filename, "r") as f:
            code = f.read()

        # Send Ctrl+C to stop any running code
        ser.write(b"\x03")
        time.sleep(0.5)

        # Enter REPL
        ser.write(b"\x01")
        time.sleep(0.5)

        # Paste mode
        ser.write(b"\x05")
        time.sleep(0.5)

        # Send code
        ser.write(code.encode())
        time.sleep(0.5)

        # Exit paste mode (Ctrl+D)
        ser.write(b"\x04")
        time.sleep(1)

        print(f"✓ Uploaded {filename} to {port}")

        # Show output
        while ser.in_waiting:
            print(ser.read().decode("utf-8", errors="ignore"), end="")

        ser.close()

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 upload.py <port> [filename]")
        print("Example: python3 upload.py /dev/cu.USBSERIAL-1410 balancer.py")
        sys.exit(1)

    port = sys.argv[1]
    filename = sys.argv[2] if len(sys.argv) > 2 else "balancer.py"

    upload_to_esp32(port, filename)
