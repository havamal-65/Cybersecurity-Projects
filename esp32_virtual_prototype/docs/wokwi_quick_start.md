# Wokwi Quick Start Guide

## Option 1: Create New Project

1. Go to: https://wokwi.com/projects/new/esp32
2. Replace the code with your firmware
3. Replace diagram.json with your hardware config
4. Click the green Start button

## Option 2: Use This Template Link

Click here to open a working template:
https://wokwi.com/projects/new/esp32

Then:
1. Copy your code from `firmware/esp32_security_device_wokwi.ino`
2. Paste it in the editor
3. Click "diagram.json" tab
4. Paste your diagram.json content
5. Click Start

## What Success Looks Like

When working correctly, you'll see:
- Green "Start" button changes to red "Stop"
- Serial Monitor shows boot messages
- Status LED (green) turns on
- Buttons are clickable
- Statistics update every 5 seconds

## Virtual WiFi Testing

Wokwi simulates WiFi networks. To test:
1. The ESP32 creates an AP automatically
2. In the simulation, you can "connect" to it
3. The web interface at 192.168.4.1 is accessible through Wokwi's network simulation 