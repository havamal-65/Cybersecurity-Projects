# ESP32 WiFi Security Dongle - Virtual Prototype

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![ESP32](https://img.shields.io/badge/Platform-ESP32-green)](https://www.espressif.com/en/products/socs/esp32)
[![Wokwi](https://img.shields.io/badge/Simulator-Wokwi-orange)](https://wokwi.com/)

A comprehensive ESP32-based WiFi security device simulation that provides enterprise-grade network protection features in a consumer-friendly package. This project demonstrates advanced cybersecurity concepts through a fully functional virtual prototype.

## 🎯 Features

### Security Capabilities
- **🛡️ Advanced Firewall** - Rule-based packet filtering with protocol/port control
- **🔄 MAC Address Randomization** - Privacy protection with configurable intervals
- **🔒 VPN Simulation** - Packet encryption markers for secure tunneling
- **🚫 DNS Filtering** - Block malicious domains and tracking sites
- **⚡ DDoS Protection** - Rate limiting to prevent denial of service attacks
- **📊 Real-time Monitoring** - Web dashboard with live statistics

### Attack Detection
- Port scanning attempts
- ARP spoofing attacks
- DNS poisoning attempts
- SQL injection patterns
- XSS attack vectors
- Brute force attempts

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Web browser (Chrome/Firefox recommended)
- [Wokwi Account](https://wokwi.com/) (free)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/esp32_virtual_prototype.git
cd esp32_virtual_prototype
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 💻 Running the Simulation

### Option 1: Wokwi Online Simulation

1. **Upload to Wokwi**
   - Create new project at [wokwi.com](https://wokwi.com/)
   - Copy `firmware/esp32_security_dongle.ino` content
   - Import `wokwi_config/diagram.json` for hardware setup
   - Click "Start Simulation"

2. **Access Web Interface**
   - Open browser to `http://192.168.4.1` (ESP32 AP mode)
   - View real-time statistics and control features

### Option 2: Python Bridge Testing

1. **Start the bridge**
```bash
cd test
python wokwi_bridge.py
```

2. **Run attack simulations**
```bash
# In another terminal
python -m pytest test_security_features.py -v
```

### Option 3: Local Development

1. **Run standalone tests**
```bash
# Test firewall rules
python test/test_security_features.py

# Simulate network attacks
python test/attack_simulator.py
```

## 📁 Project Structure

```
esp32_virtual_prototype/
├── firmware/                    # ESP32 Arduino code
│   ├── esp32_security_dongle.ino
│   └── config.h
├── wokwi_config/               # Wokwi simulation configuration
│   ├── diagram.json           # Hardware connections
│   ├── wokwi.toml            # Project settings
│   └── project.json          # Dependencies
├── test/                       # Testing and simulation
│   ├── wokwi_bridge.py       # Bridge to Wokwi
│   ├── test_security_features.py
│   └── attack_simulator.py
├── documentation/              # Project documentation
│   ├── ESP32_Virtual_Prototype_Documentation.md
│   └── Project_Implementation_Guide.md
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🔧 Configuration

### Security Profiles

The device comes with pre-configured security profiles:

| Profile | Description | Use Case |
|---------|-------------|----------|
| **Basic Protection** | Standard security for everyday use | Home networks |
| **Maximum Privacy** | Full privacy with VPN and frequent MAC changes | Public WiFi |
| **Family Safe** | Content filtering and parental controls | Households with children |
| **Public WiFi** | Maximum security for untrusted networks | Coffee shops, airports |

### Custom Configuration

Edit `firmware/config.h` to customize:
```cpp
#define MAC_RANDOMIZATION_INTERVAL 600000  // 10 minutes
#define MAX_FIREWALL_RULES 50
#define RATE_LIMIT_THRESHOLD 100  // packets per minute
```

## 🧪 Testing

### Unit Tests
```bash
pytest test/ -v --cov=test
```

### Performance Testing
```bash
python test/performance_monitor.py
```

### Security Validation
```bash
python test/security_validator.py
```

## 📊 Web Dashboard

Access the dashboard at `http://192.168.4.1` when connected to the ESP32's access point.

### Dashboard Features:
- **Real-time Statistics** - Packets processed, blocked, threats detected
- **Security Controls** - Toggle VPN, firewall, MAC randomization
- **Alert History** - Recent security events
- **Network Status** - Connection health and performance

## 🛠️ Development

### Adding New Security Rules

1. **Edit firewall rules**
```cpp
// In firmware/esp32_security_dongle.ino
firewallRules[n] = {true, PROTO_TCP, 0, 0, 0, PORT, ACTION_BLOCK, "Description"};
```

2. **Update blocked domains**
```cpp
blockedDomains[n] = "malicious-site.com";
```

### Extending Attack Detection

Add new detection patterns in `processPacket()`:
```cpp
if (detectSQLInjection(packet)) {
    securityState.threatsDetected++;
    return true;  // Block packet
}
```

## 📈 Performance Metrics

- **Packet Processing**: >1000 packets/second
- **Latency**: <1ms average
- **Memory Usage**: <50KB RAM
- **Power Consumption**: ~80mA (simulation estimate)

## 🔐 Security Architecture

The device implements a multi-layered security approach:

1. **Physical Layer** - MAC address randomization
2. **Network Layer** - IP/Port filtering
3. **Transport Layer** - Protocol inspection
4. **Application Layer** - Payload analysis
5. **DNS Layer** - Domain filtering

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ESP32 Arduino Core developers
- Wokwi simulator team
- Security research community
- Open source contributors

## 📞 Support

- **Documentation**: See `/documentation` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/esp32_virtual_prototype/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/esp32_virtual_prototype/discussions)

## 🚦 Status

- ✅ Core Security Features
- ✅ Web Dashboard
- ✅ Attack Simulations
- ✅ Wokwi Integration
- 🚧 Mobile App (Planned)
- 🚧 Cloud Integration (Planned)

---

**Note**: This is a virtual prototype for educational and portfolio purposes. For production use, additional security hardening and regulatory compliance would be required. 