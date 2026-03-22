#!/bin/bash
# Fix Arduino ESP32 tools for Apple Silicon (ARM64)

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Arduino ESP32 Setup Fixer for Apple Silicon (ARM64)   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "✗ This script requires Apple Silicon (ARM64)"
    echo "  Current architecture: $ARCH"
    exit 1
fi
echo "✓ Running on Apple Silicon (ARM64)"
echo ""

# Arduino library path
ARDUINO_PATH="$HOME/Library/Arduino15"

# Check if Arduino is open - if so, warn user
if pgrep -x "Arduino" > /dev/null; then
    echo "⚠ Arduino IDE is currently running!"
    echo "  Please close it before continuing."
    echo ""
    read -p "Press Enter once Arduino is closed... "
fi

echo "Cleaning up Intel (x86_64) tools..."
echo ""

# Remove old Intel tools
TOOLS_TO_REMOVE=(
    "esptool_py"
    "xtensa-esp32-elf-gcc"
    "xtensa-esp32s2-elf-gcc"
    "xtensa-esp32s3-elf-gcc"
    "mklittlefs"
    "openocd-esp32"
    "xtensa-esp-elf-gdb"
)

for tool in "${TOOLS_TO_REMOVE[@]}"; do
    if [ -d "$ARDUINO_PATH/packages/esp32/tools/$tool" ]; then
        echo "  Removing: $tool"
        rm -rf "$ARDUINO_PATH/packages/esp32/tools/$tool"
    fi
done

echo ""
echo "✓ Cleaned up Intel tools"
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Next Steps:                                           ║"
echo "║  1. Open Arduino IDE                                   ║"
echo "║  2. Tools → Board Manager                              ║"
echo "║  3. Search for 'ESP32' by Espressif Systems            ║"
echo "║  4. Click Install (latest version)                     ║"
echo "║  5. Wait for download to complete                      ║"
echo "║  6. Close and re-open Arduino                          ║"
echo "║  7. Try uploading your sketch again                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "✓ Cleanup complete! Arduino will download ARM64 tools."
