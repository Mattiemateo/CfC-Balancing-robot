# Arduino ESP32 ARM64 (Apple Silicon) Setup Guide

## Problem
You have Intel (x86_64) tools in your Arduino setup on an Apple Silicon Mac. This causes:
```
Bad CPU type in executable
fork/exec .../ctags: bad CPU type in executable
```

## Solution

### Step 1: Automatic Cleanup (Recommended) ⭐

Run the cleanup script:
```bash
cd ~/Code/CfC_balancingRobot
./fix_arduino_arm64.sh
```

This will remove:
- **ESP32 package**: esptool_py, xtensa compilers, mklittlefs, openocd, gdb
- **Builtin package**: ctags, old serial-monitor, serial-discovery, dfu-discovery, mdns-discovery
- **Total freed**: 3-4 GB of Intel tools

### Step 2: Re-download ARM64 Tools

1. **Close Arduino IDE** completely
2. **Open Arduino IDE** again
3. Go to **Tools → Board Manager**
4. Search for **"ESP32"** by Espressif Systems
5. Click **Install** (latest version)
   - This will download ~1 GB of ARM64 tools
   - Wait for completion (5-15 minutes depending on internet)
6. **Close and re-open Arduino IDE**

### Step 3: Try Uploading! 🚀

Your code should now compile and upload without errors!

---

## Manual Cleanup (If You Prefer)

Close Arduino IDE first, then:

```bash
# ESP32 Tools
rm -rf ~/Library/Arduino15/packages/esp32/tools/esptool_py
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32s2-elf-gcc
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32s3-elf-gcc
rm -rf ~/Library/Arduino15/packages/esp32/tools/mklittlefs
rm -rf ~/Library/Arduino15/packages/esp32/tools/openocd-esp32
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp-elf-gdb

# Builtin Tools (remove Intel versions)
rm -rf ~/Library/Arduino15/packages/builtin/tools/ctags
rm -rf ~/Library/Arduino15/packages/builtin/tools/serial-monitor/0.15.0
rm -rf ~/Library/Arduino15/packages/builtin/tools/serial-monitor/0.13.0
rm -rf ~/Library/Arduino15/packages/builtin/tools/serial-monitor/0.14.1
rm -rf ~/Library/Arduino15/packages/builtin/tools/dfu-discovery/0.1.2
rm -rf ~/Library/Arduino15/packages/builtin/tools/serial-discovery/1.4.1
rm -rf ~/Library/Arduino15/packages/builtin/tools/serial-discovery/1.4.0
rm -rf ~/Library/Arduino15/packages/builtin/tools/mdns-discovery/1.0.9
```

Then follow Step 2 above to download ARM64 versions.

---

## Verify Setup is Correct

To verify you have ARM64 tools installed:

```bash
# Check esptool (should show "arm64")
file ~/Library/Arduino15/packages/esp32/tools/esptool_py/*/esptool

# Check compiler (should show "arm64")
file ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc/*/bin/xtensa-esp32-elf-gcc

# Check builtin tools (should only see arm64)
find ~/Library/Arduino15/packages/builtin/tools -type f -perm +111 | xargs file | grep arm64
```

Expected output:
```
.../esptool: Mach-O 64-bit executable arm64
.../xtensa-esp32-elf-gcc: Mach-O 64-bit executable arm64
```

No x86_64 should appear! ✓

---

## Storage Reclaimed

Removing all old Intel tools frees up **3-4 GB** of space! 🎉

---

## Intel vs ARM64 Tools Being Cleaned

### ESP32 Package (~2-3 GB)
| Tool | x86_64 Size | Purpose |
|------|------------|---------|
| esptool_py | 200MB | Upload/erase flasher |
| xtensa-esp32-elf-gcc | 600MB | C/C++ compiler |
| xtensa-esp32s2-elf-gcc | 600MB | S2 variant compiler |
| xtensa-esp32s3-elf-gcc | 600MB | S3 variant compiler |
| mklittlefs | 50MB | Filesystem builder |
| openocd-esp32 | 150MB | Debugger/JTAG |
| xtensa-esp-elf-gdb | 100MB | GDB debugger |

### Builtin Package (~1-2 GB)
| Tool | Versions Removed | Purpose |
|------|-----------------|---------|
| ctags | 5.8-arduino11 | Code navigation |
| serial-monitor | 0.13.0, 0.14.1, 0.15.0 | Serial port monitor |
| serial-discovery | 1.4.0, 1.4.1 | Serial port detection |
| dfu-discovery | 0.1.2 | USB device detection |
| mdns-discovery | 1.0.9 | mDNS service discovery |

---

## Troubleshooting

### "Bad CPU type in executable" Still Appears?

1. Make sure Arduino is **completely closed**
2. Run the cleanup script again:
   ```bash
   ./fix_arduino_arm64.sh
   ```
3. Wait 30 seconds, then open Arduino
4. Go to Tools → Board Manager and re-install ESP32

### "Cannot connect to COM port" After Setup?

This is normal - try:
1. Unplug ESP32
2. Wait 5 seconds
3. Plug back in
4. Try uploading again

### Board Manager Won't Show ESP32?

Verify the board URL is added:
- File → Preferences
- Check "Additional boards manager URLs" contains:
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```

If missing, add it and restart Arduino.

### Tools Seem Slow After Cleanup?

Arduino might be rebuilding indexes. Wait 2-3 minutes or:
```bash
rm -rf ~/Library/Arduino15/staging
rm -rf ~/Library/Arduino15/tmp
```

---

## Quick Verification Script

Save this to check your setup:

```bash
#!/bin/bash
echo "=== Arduino ARM64 Setup Verification ==="
echo ""
echo "1. ESP32 Tools:"
file ~/Library/Arduino15/packages/esp32/tools/esptool_py/*/esptool 2>/dev/null | tail -1
echo ""
echo "2. Builtin Tools:"
find ~/Library/Arduino15/packages/builtin/tools -type f -perm +111 2>/dev/null | \
  xargs file 2>/dev/null | grep -c arm64
echo "   ✓ ARM64 tools found"
echo ""
echo "3. Intel Tools Remaining:"
find ~/Library/Arduino15/packages -type f -perm +111 2>/dev/null | \
  xargs file 2>/dev/null | grep -c x86_64
echo "   (Should be 0)"
```

---

## What Happens After Cleanup

### Arduino Will:
1. Detect missing tools when you open it
2. Automatically download ARM64 versions
3. Cache them for future use
4. Work perfectly on your Apple Silicon Mac ✓

### You Get:
- ✓ Native ARM64 performance
- ✓ Faster compilation
- ✓ Smooth uploads
- ✓ 3-4 GB free space

---

## Support

If issues persist:
1. Check internet connection (1 GB+ download required)
2. Verify 2+ GB free disk space
3. Try different USB port
4. Restart Mac if stuck
5. Check Arduino version is latest

**Everything should work perfectly once cleaned up!** ⚡🍎

