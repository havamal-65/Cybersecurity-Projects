# ESP32 WiFi Security Adapter Simulation

A comprehensive software simulation of an ESP32-based WiFi security adapter, demonstrating practical implementation of network security concepts and features. This project serves as a portfolio piece showcasing cybersecurity skills and network security knowledge.

## Overview

This simulation emulates the behavior of a secure WiFi adapter based on ESP32 hardware, featuring:

- Network traffic simulation with realistic packet generation
- Security features including MAC address randomization and firewall
- Encryption simulation with key rotation and performance metrics
- Intrusion detection system with signature and anomaly detection
- Web dashboard for visualization of security events and device status

The project demonstrates how software can be used to prototype and test security hardware designs before physical implementation. It provides a realistic simulation of how an ESP32-based security device would function in real-world scenarios.

## Features

### Core Security Features

1. **MAC Address Randomization**
   - Periodic MAC address changing to prevent device tracking
   - Configurable randomization intervals
   - Immediate manual rotation capability
   
2. **Advanced Firewall**
   - Rule-based packet filtering
   - Stateful packet inspection
   - Rate limiting to prevent DoS attacks
   - Support for protocol, IP, and port-based rules
   
3. **Secure Encryption**
   - AES-256 encryption for data protection
   - Automatic key rotation
   - Hardware acceleration simulation
   - Performance metrics tracking

4. **Intrusion Detection System**
   - Signature-based detection for known threats
   - Anomaly-based detection for unusual patterns
   - Multiple attack type detection (port scanning, DoS, ARP spoofing, etc.)
   - Configurable alert thresholds

### Simulation Features

1. **Realistic Network Simulation**
   - Generation of common protocols (TCP, UDP, ICMP)
   - Simulation of normal traffic patterns
   - Automatic attack simulation
   - Support for common attack types
   
2. **Interactive Dashboard**
   - Real-time traffic visualization
   - Alert monitoring and management
   - Device status overview
   - Configuration management

3. **Modular Architecture**
   - Component-based design
   - Extensible framework for adding new features
   - Clean separation of concerns
   - Well-documented code

## Components

This simulation consists of several key components:

1. **Core Engine**: Coordinates the simulation and manages component lifecycles
2. **Network Simulator**: Generates realistic network packets and simulates attacks
3. **Security Components**:
   - MAC Randomization: Periodically changes the device MAC address
   - Firewall: Filters network traffic based on configurable rules
   - Encryption: Simulates data encryption with key management
4. **Intrusion Detection**: Identifies suspicious activity and generates alerts
5. **Web Dashboard**: Visualizes security events and device status

## Technical Implementation

The simulation uses:
- Python for core simulation logic
- Scapy for network packet generation
- Cryptography for encryption simulation
- Flask for the web dashboard

All components are designed with a modular architecture to allow for easy extension and modification.

## Running the Simulation

### Requirements

```
pip install -r requirements.txt
```

### Platform-Specific Installation Instructions

#### Docker (Recommended for All Platforms)
1. **Install Docker**:
   - Windows: Install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - macOS: Install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Linux: Install [Docker Engine](https://docs.docker.com/engine/install/)

2. **Using Helper Scripts** (easiest method):
   - Windows: Double-click `docker-run.bat` or run from command prompt
     ```cmd
     docker-run.bat
     ```
   
   - Linux/macOS: Make the script executable and run it
     ```bash
     chmod +x docker-run.sh
     ./docker-run.sh
     ```
   
   - With custom options:
     ```bash
     ./docker-run.sh --debug --duration 300
     ```

3. **Run with Docker Compose** (alternative method):
   ```bash
   # Build and start the simulation
   docker-compose up
   
   # Or run in detached mode
   docker-compose up -d
   
   # Stop the simulation
   docker-compose down
   ```

4. **Run with Docker** (advanced method):
   ```bash
   # Build the image
   docker build -t esp32-security-sim .
   
   # Run the container with default options
   docker run -p 5000:5000 esp32-security-sim
   
   # Run with custom command-line options
   docker run -p 5000:5000 esp32-security-sim --debug --duration 300
   ```

5. **Access the Dashboard**:
   - Open your browser and navigate to http://localhost:5000/

#### Windows
1. **Install Python**:
   - Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/windows/)
   - Ensure you check "Add Python to PATH" during installation

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Install Npcap for Scapy** (optional - for real packet capture):
   - Download and install Npcap from [npcap.com](https://npcap.com/#download)
   - Ensure you select "Install Npcap in WinPcap API-compatible Mode" during installation

4. **Run the Simulation**:
   ```
   python main.py
   ```
   - If using PowerShell, you can also use:
   ```
   python .\main.py
   ```

5. **Access the Dashboard**:
   - A browser window should automatically open to http://localhost:5000/
   - If it doesn't open automatically, navigate to this URL manually

#### Linux
1. **Install Python and Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Clone Repository** (if not already done):
   ```bash
   git clone https://github.com/havamal65/Cybersecurity_Portfolio.git
   cd Cybersecurity_Portfolio/Cybersecurity/esp32_security_sim
   ```

3. **Create and Activate Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Requirements**:
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Install Scapy Dependencies** (for real packet capture):
   ```bash
   sudo apt install tcpdump
   ```

6. **Run Simulation**:
   - Regular mode:
   ```bash
   python3 main.py
   ```
   - With elevated privileges (if using real network interfaces):
   ```bash
   sudo python3 main.py
   ```

7. **Access the Dashboard**:
   - A browser window should automatically open to http://localhost:5000/
   - If it doesn't open automatically, navigate to this URL manually

#### macOS
1. **Install Python**:
   - Using Homebrew:
   ```bash
   brew install python
   ```
   - Or download from [python.org](https://www.python.org/downloads/macos/)

2. **Install Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Install Scapy Dependencies** (for real packet capture):
   ```bash
   brew install libdnet
   brew install tcpdump
   ```

4. **Run Simulation**:
   ```bash
   python3 main.py
   ```

5. **Access the Dashboard**:
   - A browser window should automatically open to http://localhost:5000/
   - If it doesn't open automatically, navigate to this URL manually

### Basic Usage

```
python main.py
```

This will start the simulation with default settings. Once running, access the dashboard at http://localhost:5000/

### Command-line Options

- `--debug`: Enable debug logging
- `--no-dashboard`: Disable the web dashboard
- `--no-network`: Disable network simulation
- `--no-ids`: Disable intrusion detection
- `--config PATH`: Specify a configuration file
- `--duration SECONDS`: Set simulation duration (0 for unlimited)
- `--no-browser`: Disable automatic opening of the dashboard in browser

### Configuration

Create a JSON configuration file to customize the simulation:

```json
{
  "engine": {
    "simulation_speed": 1.0
  },
  "network": {
    "normal_traffic_rate": 20,
    "attack_probability": 0.1
  },
  "firewall": {
    "default_policy": "allow",
    "rules": [
      {"protocol": "tcp", "dst_port": 22, "src_ip": "external", "action": "block"},
      {"protocol": "tcp", "dst_port": 23, "action": "block"}
    ]
  },
  "mac_randomizer": {
    "randomization_interval": 300
  },
  "ids": {
    "alert_threshold": 0.7
  },
  "dashboard": {
    "port": 5000
  }
}
```

Run with the configuration:

```
python main.py --config config.json
```

## Testing

Run the test suite to verify the functionality:

```
python -m pytest tests/
```

## Simulated Attacks

The simulation can detect and respond to various attacks:

1. **Port Scanning**: Detection of systematic probing of ports
2. **Denial of Service**: Recognition of high-volume traffic patterns
3. **ARP Spoofing**: Identification of ARP poisoning attempts
4. **Brute Force**: Detection of repeated authentication attempts
5. **Data Exfiltration**: Identification of suspicious outbound data transfers

## Project Structure

```
esp32_security_sim/
├── core/                # Core simulation engine
├── network/             # Network traffic simulation
├── security/            # Security features implementation
│   ├── firewall.py      # Packet filtering functionality
│   ├── mac_randomization.py  # MAC address changing
│   └── encryption.py    # Data encryption simulation
├── detection/           # Intrusion detection system
├── dashboard/           # Web interface
│   ├── app.py           # Flask application
│   └── templates/       # HTML templates
├── tests/               # Test suite
├── main.py              # Main entry point
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

## Portfolio Context

This project demonstrates the following cybersecurity skills:

- Network security principles and implementation
- Intrusion detection and prevention techniques
- Secure coding practices
- Security visualization and monitoring
- Understanding of common attack vectors and mitigations
- Practical application of encryption and cryptography

## Future Enhancements

Potential areas for expansion:

1. VPN integration simulation
2. DNS filtering capabilities
3. Machine learning-based threat detection
4. Honeypot functionality
5. Integration with threat intelligence feeds

## Hardware Implementation Path

This simulation serves as a proof-of-concept for an actual ESP32-based security device. The path to hardware implementation would include:

1. **Component Selection**:
   - ESP32-S3 microcontroller with dual-core processor
   - ATECC608B secure element for cryptographic operations
   - External flash for firmware and configuration storage

2. **Hardware Design**:
   - PCB design with proper RF considerations
   - USB interface for power and data
   - Status LEDs for visual feedback
   - Optional battery backup

3. **Firmware Development**:
   - Port simulation components to ESP-IDF framework
   - Optimize for resource-constrained environment
   - Implement hardware-specific security features

4. **Production Considerations**:
   - Supply chain security
   - Secure manufacturing process
   - Tamper-resistant packaging

## From Simulation to Physical Device

The simulation is designed to mirror the functionality of a physical ESP32 security device while allowing for easier development, testing, and demonstration. Key differences between the simulation and a physical implementation would include:

- **Performance**: The simulation runs at a higher abstraction level, while a physical device would need to process packets in real-time with limited resources.
- **Integration**: A physical device would need to integrate with actual network hardware, while the simulation uses software-generated packets.
- **Security Boundaries**: The simulation runs in a trusted environment, while a physical device would need to protect against physical attacks and tampering.

## Security Advisories

While this project demonstrates security principles, it is intended for educational purposes. If implemented as a real device, consider the following security advisories:

- Regular firmware updates would be essential
- Secure boot and encrypted firmware would be required
- Hardware-based random number generation should be used for cryptographic operations
- Thorough security auditing would be necessary before deployment

## License

This project is provided for educational and portfolio purposes under the MIT License.

## Acknowledgments

This project draws inspiration from various open-source security tools and resources:

- The ESP-IDF framework by Espressif
- The Scapy network manipulation library
- Security research by organizations like MITRE and OWASP
- Academic research on IoT security

## Contact

For questions or collaboration on this portfolio project, please contact:

[Your Contact Information]

---

*This simulation was developed as part of a cybersecurity portfolio to demonstrate security design principles and implementation skills.*

## Archive Directory

This project includes an `archive` directory that contains development history files and redundant code versions. These files are preserved for reference and to document the development process, including:

- Various setup scripts used during development
- Fix scripts for addressing dependency and environmental issues
- Fixed versions of key components that show the evolution of the codebase

The main codebase contains only the most current and optimized versions of each component. The archived files show the journey of building this simulation and may be useful for understanding the development approach taken.
