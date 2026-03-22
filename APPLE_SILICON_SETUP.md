# Arduino ESP32 ARM64 (Apple Silicon) Setup Guide

## Problem
You have Intel (x86_64) tools in your Arduino setup on an Apple Silicon Mac. This causes:
```
bash: /Users/mateodevos/Library/Arduino15/packages/esp32/tools/esptool_py/5.1.0/esptool: Bad CPU type in executable
exit status 126
```

## Solution

### Option 1: Automatic Cleanup (Recommended)

Run the cleanup script:
```bash
cd ~/Code/CfC_balancingRobot
./fix_arduino_arm64.sh
```

This will:
- ✓ Remove all Intel x86_64 tools
- ✓ Clear space on your Mac
- ✓ Prepare Arduino to re-download ARM64 versions

### Option 2: Manual Steps

If you prefer to do it manually:

```bash
# Close Arduino IDE first!

# Remove Intel tools
rm -rf ~/Library/Arduino15/packages/esp32/tools/esptool_py
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32s2-elf-gcc
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32s3-elf-gcc
rm -rf ~/Library/Arduino15/packages/esp32/tools/mklittlefs
rm -rf ~/Library/Arduino15/packages/esp32/tools/openocd-esp32
rm -rf ~/Library/Arduino15/packages/esp32/tools/xtensa-esp-elf-gdb
```

## After Cleanup

1. **Close Arduino IDE** if it's open
2. **Open Arduino IDE**
3. Go to **Tools → Board Manager**
4. Search for **"ESP32"** by Espressif Systems
5. Click **Install** (will download ~800MB)
   - This time it will download ARM64 versions automatically
6. Wait for completion
7. **Close Arduino IDE** completely
8. **Re-open Arduino IDE**
9. **Try uploading again** - should work!

## Verify Setup is Correct

To verify you have ARM64 tools installed:

```bash
# Check esptool architecture (should show "arm64")
file ~/Library/Arduino15/packages/esp32/tools/esptool_py/*/esptool

# Check compiler (should show "arm64")
file ~/Library/Arduino15/packages/esp32/tools/xtensa-esp32-elf-gcc/*/bin/xtensa-esp32-elf-gcc
```

Expected output:
```
.../esptool: Mach-O 64-bit executable arm64
```

## Storage Reclaimed

Removing old Intel tools frees up ~2-3 GB of space on your Mac! 🎉

## If Issues Persist

### Still getting "Bad CPU type" error?

1. Completely remove Arduino:
   ```bash
   rm -rf ~/Library/Arduino15
   rm -rf ~/.arduino15
   ```
2. Close Arduino IDE
3. Download latest Arduino IDE for Mac (ARM64)
4. Re-install ESP32 board via Board Manager

### Board Manager won't show ESP32?

Make sure you added the URL in Preferences:
- File → Preferences
- Add to "Additional boards manager URLs":
  ```
  https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
  ```

## Troubleshooting Upload Issues

After fixing tools, if upload still fails:

| Error | Solution |
|-------|----------|
| `Bad CPU type` | You still have Intel tools - run cleanup again |
| `Permission denied` | Try `chmod 755 ~/Library/Arduino15/packages/esp32/tools/*/bin/*` |
| `Port not found` | Install CH340 driver or use USB hub |
| `Device is read-only` | Restart Arduino IDE and try again |

## Quick Commands for ESP32 Setup

```bash
# List all ESP32 tools and their architecture
ls -la ~/Library/Arduino15/packages/esp32/tools/
for dir in ~/Library/Arduino15/packages/esp32/tools/*/; do
    echo "=== $(basename "$dir") ==="
    file "$dir"bin/* 2>/dev/null | head -2
done

# Clean all Arduino caches
rm -rf ~/Library/Arduino15/staging
rm -rf ~/Library/Arduino15/tmp
```

## What's Being Cleaned

These are Intel (x86_64) tools that won't run on ARM64:

| Tool | Size | Purpose |
|------|------|---------|
| esptool_py | 200MB | Upload/erase flasher |
| xtensa-esp32-elf-gcc | 600MB | C/C++ compiler |
| xtensa-esp32s2-elf-gcc | 600MB | S2 variant compiler |
| xtensa-esp32s3-elf-gcc | 600MB | S3 variant compiler |
| mklittlefs | 50MB | Filesystem builder |
| openocd-esp32 | 150MB | Debugger/JTAG |
| xtensa-esp-elf-gdb | 100MB | GDB debugger |

**Total freed: ~2-3 GB** ✓

## Apple Silicon Native Tools

Arduino will automatically download these native ARM64 versions:
- ✓ esptool_py (native ARM64)
- ✓ xtensa-esp32-elf-gcc (native ARM64)
- ✓ Full toolchain optimized for Apple Silicon

## Support

If you still have issues:
1. Check your internet connection (tools are ~800MB)
2. Verify you have 2GB+ free disk space
3. Try downloading at different time (Espressif mirrors sometimes slow)
4. Check Arduino IDE version (use latest)

---

**Everything should work smoothly once ARM64 tools are installed!** ⚡
