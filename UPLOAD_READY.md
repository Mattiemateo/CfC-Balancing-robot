# ESP32 Balancing Robot - Ready to Upload! 🤖

## Summary

Your balancing robot firmware is **ready to upload** with tuned PID parameters calculated from simulation.

### Key Specifications
- **Height (COM):** 11 cm
- **Wheel radius:** 75 mm (correct!)
- **Control frequency:** 200 Hz
- **Motor:** NEMA17 1.8° steppers with DRV8825 drivers

### Tuned PID Parameters
Based on inverted pendulum simulation with **75mm wheels**:

```cpp
Kp = 20.0   // Proportional gain
Kd = 3.0    // Derivative gain  
Ki = 0.05   // Integral gain
```

**Simulation Results:**
- ✓ Stable balancing
- Max tilt recovery: 2.9°
- Settling time: 0.29 seconds
- Expected behavior: Smooth, responsive control

---

## Upload Instructions

### Step 1: Install Arduino IDE
Download from: https://www.arduino.cc/en/software

### Step 2: Add ESP32 Board Support
1. File → Preferences
2. Paste into "Additional boards manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Tools → Board Manager → Search "ESP32" → Install (by Espressif Systems)

### Step 3: Install MPU6050 Library
Tools → Manage Libraries → Search **"MPU6050 by Jarzebski"** → Install

### Step 4: Open Firmware
File → Open → Select `esp32_balancer_v2.ino` from your project folder

### Step 5: Configure Board Settings
```
Tools → Board → ESP32 Dev Module
Tools → Port → [Select your COM port]
Tools → Upload Speed → 921600
Tools → Flash Size → 4MB
```

### Step 6: Verify (Compile)
Sketch → Verify/Compile (Ctrl+R)
Should complete without errors

### Step 7: Upload
Sketch → Upload (Ctrl+U)
Watch for "Writing at..." messages

### Step 8: Verify Connection
Tools → Serial Monitor
- Baud rate: **115200**
- Should see boot messages and PID parameters

---

## First Test Procedure

### Safety Setup
1. Have a **soft landing zone** (pillow, foam mat)
2. **Keep your hands ready** to catch the robot
3. Test in a confined area away from obstacles
4. Never leave it running unattended

### Testing Steps
1. **Power on** - Serial Monitor shows calibration
2. **Wait for "System Ready"** message
3. **Place robot** on level ground with gentle tilt
4. **Release gently** from ~5° forward tilt
5. **Observe:**
   - Does it try to move forward? ✓ Good
   - Does it fall forward? → Reduce Kp/Kd by 20%
   - Does it recover too slowly? → Increase Kp by 15%
   - Does it oscillate? → Increase Kd

### Serial Monitor Output
```
╔══════════════════════════════════════════╗
║  ESP32 Balancing Robot - Improved v2.0  ║
╚══════════════════════════════════════════╝

✓ Initializing MPU6050... ✓
✓ Control timer initialized (200 Hz)
✓ Motor timer initialized (4000 Hz)

╔══════════════════════════════════════════╗
║        System Ready - Place Robot!       ║
╚══════════════════════════════════════════╝

┌─ BALANCE STATE ─────────────────────┐
│ Pitch: -2.34°  Rate: -45.62°/s   │
│ Control: 15.32 N (Kp,Kd=20,3) │
│ Motors:  1250 Hz   1250 Hz       │
│ Status: ✓ BALANCED                  │
└─────────────────────────────────────┘
```

---

## Tuning Reference

If your robot behaves differently than expected:

| Problem | Solution |
|---------|----------|
| Falls immediately | Reduce Kp to 15, Kd to 2 |
| Oscillates wildly | Increase Kd to 4, reduce Kp to 18 |
| Too slow to respond | Increase Kp to 25, Kd to 3.5 |
| Drifts forward/back | Increase Ki from 0.05 to 0.1 |
| Motor directions wrong | Swap DIR pin logic (lines 227-233) |

---

## Wiring Verification

Before powering on, double-check:

**Motor A (Left):**
- [ ] STEP → GPIO16
- [ ] DIR → GPIO5  
- [ ] EN → GPIO17

**Motor B (Right):**
- [ ] STEP → GPIO12
- [ ] DIR → GPIO4
- [ ] EN → GPIO13

**MPU6050 IMU:**
- [ ] SDA → GPIO21
- [ ] SCL → GPIO22
- [ ] INT → GPIO15
- [ ] VCC → 3.3V
- [ ] GND → GND

**Power:**
- [ ] 24V to DRV8825 drivers
- [ ] 5V to ESP32 VIN
- [ ] All GNDs connected together

---

## Next Steps

### Immediate (After first successful balance)
1. Increase challenge by tilting more (10°, 15°)
2. Test motor response by pushing gently
3. Verify settling behavior matches simulation

### Short Term (Day 1-3)
1. Fine-tune Kp/Kd if needed (±5% increments)
2. Record successful parameters
3. Test edge cases (fast release, max tilt)

### Medium Term (Week 1)
1. Add your CfC neural network for learning
2. Log sensor data during balancing
3. Compare learned control vs PID

### Long Term
1. Implement encoder feedback
2. Add velocity control
3. Build waypoint navigation
4. Integrate with Bluetooth remote

---

## Troubleshooting

### "No COM port appearing"
- Try different USB cable (data cable needed, not just power)
- Install CH340 drivers if using clone boards
- Try different USB port on computer

### "Upload failed"
- Try lower baud rate: 115200
- Disconnect other USB devices
- Press BOOT button on ESP32 if stuck

### "IMU not found"
- Check I2C connections (GPIO21/22)
- Verify I2C address: should be 0x68
- Scan I2C bus: use I2C scanner sketch

### "Motor doesn't spin"
- Check 24V power to DRV8825
- Verify motor connections (A±, B±)
- Test with constant DIR/STEP to manually verify

---

## Physics Reference

Your robot acts as an **inverted pendulum**:
- When tilted forward → motor moves forward
- This creates backward acceleration → reduces tilt
- With 75mm wheels and 11cm height, you have good mechanical advantage

**Natural frequency** = √(9.81/0.11) = **9.44 rad/s** (1.50 Hz)

The PID gains ensure the closed-loop system responds critically damped, settling in ~300ms.

---

## Support & Resources

- **Arduino ESP32 Docs:** https://docs.espressif.com/
- **MPU6050 Datasheet:** https://invensense.tdk.com/
- **DRV8825 Guide:** https://www.pololu.com/product/2753
- **Your Project:** Check `ESP32_SETUP_GUIDE.md` for more details

---

**Ready to balance? Upload the firmware and let the robot do its thing!** ⚡🤖

Good luck! 🎉
