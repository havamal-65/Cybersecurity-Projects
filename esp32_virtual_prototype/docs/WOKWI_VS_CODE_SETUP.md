# Wokwi VS Code Setup Guide

## Prerequisites

1. Install [Wokwi for VS Code extension](https://marketplace.visualstudio.com/items?itemName=wokwi.wokwi-vscode)
2. Install Arduino CLI or Arduino IDE
3. Request a free license from Wokwi (press F1 → "Wokwi: Request a new License")

## Step 1: Compile Your Arduino Code

Since Wokwi for VS Code needs compiled firmware (not .ino source), you must compile first:

### Using Arduino CLI:
```bash
# Install Arduino CLI (if not already installed)
# Windows (PowerShell):
Invoke-WebRequest -Uri https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip -OutFile arduino-cli.zip
Expand-Archive -Path arduino-cli.zip -DestinationPath .

# Install ESP32 board support
arduino-cli config init
arduino-cli core update-index
arduino-cli core install esp32:esp32

# Install required libraries
arduino-cli lib install "WiFi"
arduino-cli lib install "WebServer"
arduino-cli lib install "DNSServer"
arduino-cli lib install "LiquidCrystal I2C"

# Compile the firmware
arduino-cli compile --fqbn esp32:esp32:esp32 --output-dir ./build firmware/esp32_c6_security_device.ino
```

### Using Arduino IDE:
1. Open `firmware/esp32_c6_security_device.ino` in Arduino IDE
2. Select Tools → Board → ESP32 Arduino → ESP32 Dev Module
3. Select Sketch → Export Compiled Binary
4. The .bin and .elf files will be in the `firmware` folder

## Step 2: Update wokwi.toml

After compilation, update the firmware path in `wokwi.toml`:

```toml
[wokwi]
version = 1
firmware = 'build/esp32_c6_security_device.ino.bin'  # or wherever your compiled binary is
elf = 'build/esp32_c6_security_device.ino.elf'      # optional, for debugging
```

## Step 3: Run the Simulation

1. Press F1 in VS Code
2. Select "Wokwi: Start Simulator"
3. The simulation should start with your compiled firmware

## Alternative: Use Wokwi.com Instead

If compilation seems too complex, just use the online simulator:

1. Go to https://wokwi.com/projects/new/esp32
2. Replace the code with your `esp32_c6_security_device.ino`
3. Click the "diagram.json" tab and replace with your circuit
4. Click "Start Simulation"

The online version handles compilation automatically! 