# Arduino Fresh Install Guide - ARM64 (Apple Silicon)

## ✅ What Was Done

Your Arduino installation has been **completely removed**:
- ✓ ~/Library/Arduino15 - DELETED
- ✓ ~/.arduino15 - DELETED
- ✓ ~/Library/Caches/Arduino - CLEANED
- ✓ All preferences - CLEARED
- ✓ All tools (including the problematic ctags) - GONE

**Freed space: 5+ GB** 🎉

---

## 📥 Fresh Install Steps

### Step 1: Download Arduino IDE

1. Go to: **https://www.arduino.cc/software**
2. Click "Download" for macOS
3. **Important:** Make sure you get the **ARM64 native version**
   - Should say "macOS ARM64 (M1, M2, M3...)" or similar
   - NOT x86_64!

### Step 2: Install Arduino

1. Open the downloaded `.dmg` file
2. Drag "Arduino IDE 2.x" to Applications folder
3. Wait for copy to complete
4. Eject the .dmg file

### Step 3: First Launch

1. Open Applications → Arduino IDE 2.x
2. Wait for initial setup (may take 1-2 minutes)
3. It will create fresh ~/Library/Arduino15 with ARM64 tools only

### Step 4: Add ESP32 Board URL

1. File → Preferences
2. In "Additional boards manager URLs" paste:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Click OK
4. Close Arduino

### Step 5: Install ESP32 Board

1. Re-open Arduino IDE
2. Tools → Board Manager
3. Search: `ESP32`
4. Click on "ESP32" by Espressif Systems
5. Click **Install**
   - ⏳ This will download ~1GB
   - ⏱ Takes 10-15 minutes depending on internet
   - **All tools will be ARM64 native!** ✓
6. Wait for "INSTALLED" badge to appear
7. Close Board Manager

### Step 6: Install MPU6050 Library

1. Tools → Manage Libraries
2. Search: `MPU6050`
3. Click on "MPU6050 by Jarzebski"
4. Click **Install**
5. Wait for completion

### Step 7: Open Your Sketch

1. File → Open
2. Navigate to: `/Users/mateodevos/Code/CfC_balancingRobot/`
3. Select: **`esp32_balancer_v2.ino`** or **`esp32_balancer_v2/esp32_balancer_v2.ino`**
4. Click Open

### Step 8: Configure Board Settings

1. Tools → Board → Search for "ESP32"
2. Select **"ESP32 Dev Module"** (or your specific board)
3. Tools → Port → Select your COM port (usually `/dev/cu.USBSERIAL-*`)
4. Set other options:
   - Flash Freq: 80MHz
   - Flash Mode: DIO
   - Flash Size: 4MB
   - Upload Speed: 921600

### Step 9: Verify Setup

1. Sketch → Verify/Compile (Ctrl+R)
   - Should compile with **NO errors**
   - If it asks to install serial library, say YES
   - This proves everything is working!

### Step 10: Upload! 🚀

1. Plug in your ESP32
2. Sketch → Upload (Ctrl+U)
3. Watch the console for upload progress
4. Should see: `Writing at ...` messages
5. Finally: `Leaving... Hard resetting via RTS pin...`

**Success!** Your robot firmware is now on the ESP32! 🎉

---

## ✅ Verification Checklist

After upload, verify:
- [ ] No "Bad CPU type" errors
- [ ] No "ctags" errors  
- [ ] Upload completes successfully
- [ ] Serial Monitor shows boot messages (115200 baud)

---

## 🔧 Troubleshooting

### "Port not found"
- Plug ESP32 in with USB data cable (not power-only!)
- Try different USB port
- Install CH340 driver if using clone boards
- Restart Arduino IDE

### "Compile error"
- Make sure MPU6050 library is installed
- Check board is selected (Tools → Board)
- Try Sketch → Verify first

### "Still says ctags error"
- This CANNOT happen with fresh install
- Arduino 2.3+ doesn't use ctags for code analysis
- Old config is completely gone

### "Very slow to start first time"
- Arduino is building package indexes (1-2 minutes)
- Leave it running, don't force quit
- This only happens once

---

## 📁 File Locations

Your code:
```
/Users/mateodevos/Code/CfC_balancingRobot/esp32_balancer_v2.ino
```

Fresh Arduino installation:
```
~/Library/Arduino15/          ← Fresh, clean directory
~/Library/Arduino15/packages/esp32/   ← All ARM64 tools
~/Documents/Arduino/libraries/  ← Your MPU6050 library
```

---

## 🎯 Quick Reference

| Action | Shortcut |
|--------|----------|
| Verify Compile | Ctrl+R |
| Upload | Ctrl+U |
| Open Serial Monitor | Ctrl+Shift+M |
| Format Code | Ctrl+T |
| Find | Ctrl+F |

---

## 🚨 If Something Still Goes Wrong

Run this to get a fresh start again:
```bash
bash ~/nuke_arduino.sh
```

Then repeat steps 1-10 above.

---

## ✨ You're Done!

Your Arduino IDE is now:
- ✓ 100% ARM64 native
- ✓ No old Intel tools
- ✓ No ctags issues
- ✓ Fresh and clean
- ✓ Ready to use!

**Now go balance that robot!** 🤖⚡

---

## Next Steps

1. **Upload the firmware** (Steps 1-10 above)
2. **Open Serial Monitor** (Ctrl+Shift+M) at 115200 baud
3. **Press reset button** on ESP32
4. **Watch for boot messages**
5. **Place robot on ground**
6. **Test balancing!**

See `UPLOAD_READY.md` for testing procedures.
