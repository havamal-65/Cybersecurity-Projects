# ESP32 Security Device - Wokwi Instructions

## Required Modifications

The firmware needs these changes for Wokwi compatibility:
- Replace `esp_random()` with `random()`
- Disable promiscuous mode (not supported in simulator)
- Use pin 8 for LED_STATUS on ESP32-C6

## How to Run

1. Go to https://wokwi.com/projects/new/esp32
2. Copy firmware from `firmware/esp32_c6_security_device.ino`
3. Click "diagram.json" tab
4. Replace with content from `wokwi/diagram.json`
5. Click the green "Start" button

## What to Expect

- **Serial Monitor**: Shows boot messages and statistics
- **Green LED**: Status (solid = config mode, blinking = protecting)
- **Blue LED**: Activity indicator
- **Red LED**: Alert indicator
- **Config Button**: Toggle protection mode
- **Reset Button**: Hold 3 seconds for factory reset

## Features in Wokwi

✅ WiFi Access Point  
✅ Web dashboard at 192.168.4.1  
✅ LED indicators  
✅ Button controls  
✅ Simulated packet processing  
✅ Statistics display 