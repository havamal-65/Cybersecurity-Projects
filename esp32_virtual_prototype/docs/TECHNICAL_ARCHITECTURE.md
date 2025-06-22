# ESP32 Virtual Prototype - Technical Architecture

## 🏗️ System Architecture Overview

### High-Level Design
```
┌─────────────────┐    USB    ┌─────────────────┐    WiFi    ┌─────────────────┐
│                 │◄────────► │                 │◄────────► │                 │
│   Host PC       │           │  ESP32 Security │           │  Public WiFi    │
│                 │           │     Device      │           │    Network      │
│  - Sees USB     │           │  - MAC Hopping  │           │                 │
│    Network      │           │  - VPN Tunnel   │           │                 │
│    Adapter      │           │  - Firewall     │           │                 │
│                 │           │  - IDS/IPS      │           │                 │
└─────────────────┘           └─────────────────┘           └─────────────────┘
```

## 🔧 ESP32 Component Architecture

### Core Modules
```
┌─────────────────────────────────────────────────────────────┐
│                    ESP32 Security Device                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ USB         │  │ WiFi        │  │ Web         │        │
│  │ Interface   │  │ Manager     │  │ Server      │        │
│  │ Module      │  │ Module      │  │ Module      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Packet      │  │ Security    │  │ Firewall    │        │
│  │ Processing  │  │ Engine      │  │ Engine      │        │
│  │ Engine      │  │ Module      │  │ Module      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ MAC         │  │ VPN         │  │ DNS         │        │
│  │ Randomizer  │  │ Tunnel      │  │ Filter      │        │
│  │ Module      │  │ Module      │  │ Module      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Architecture

### Packet Processing Pipeline
```
1. PC sends packet
   ↓
2. USB Interface receives packet
   ↓
3. Packet Processing Engine analyzes packet
   ↓
4. Security Engine checks against rules
   ├─ ALLOW → Continue
   └─ BLOCK → Drop packet & log
   ↓
5. VPN Tunnel encrypts packet (if enabled)
   ↓
6. MAC Randomizer applies current MAC
   ↓
7. WiFi Manager sends via WiFi
   ↓
8. Response follows reverse path
```

## 🛡️ Security Module Specifications

### 1. MAC Address Randomization Module
```cpp
class MACRandomizer {
private:
    uint8_t currentMAC[6];
    unsigned long lastChange;
    unsigned long changeInterval;
    
public:
    void generateRandomMAC();
    void scheduleChange(unsigned long interval);
    bool shouldChangeMAC();
    uint8_t* getCurrentMAC();
};
```

### 2. Firewall Engine Module
```cpp
struct FirewallRule {
    bool enabled;
    uint8_t protocol;        // TCP, UDP, ICMP
    uint32_t srcIP;
    uint32_t dstIP;
    uint16_t srcPort;
    uint16_t dstPort;
    uint8_t action;          // ALLOW, BLOCK, LOG
    char description[64];
};

class FirewallEngine {
private:
    FirewallRule rules[MAX_RULES];
    int ruleCount;
    
public:
    bool processPacket(Packet& packet);
    void addRule(FirewallRule rule);
    void removeRule(int index);
};
```

### 3. Intrusion Detection System
```cpp
struct ThreatSignature {
    char pattern[128];
    uint8_t severity;        // 1-10
    char description[64];
    bool enabled;
};

class IntrusionDetection {
private:
    ThreatSignature signatures[MAX_SIGNATURES];
    int detectionCount;
    
public:
    bool analyzePacket(Packet& packet);
    void addSignature(ThreatSignature sig);
    void logThreat(const char* threat);
};
```

### 4. DNS Filtering Module
```cpp
struct BlockedDomain {
    char domain[128];
    uint8_t category;        // MALWARE, PHISHING, ADS
    bool enabled;
};

class DNSFilter {
private:
    BlockedDomain blockedDomains[MAX_DOMAINS];
    int domainCount;
    
public:
    bool isDomainBlocked(const char* domain);
    void addBlockedDomain(const char* domain, uint8_t category);
    void updateBlocklist();
};
```

## 🌐 Web Interface Architecture

### Configuration Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│                    Web Dashboard                             │
├─────────────────────────────────────────────────────────────┤
│  Dashboard    │  Security     │  Network      │  Settings   │
│  - Status     │  - Firewall   │  - WiFi       │  - Profiles │
│  - Stats      │  - VPN        │  - Connection │  - Advanced │
│  - Logs       │  - DNS Filter │  - MAC Status │  - About    │
│  - Alerts     │  - IDS        │  - Bandwidth  │  - Update   │
└─────────────────────────────────────────────────────────────┘
```

### API Endpoints
```
GET  /api/status           - Device status and statistics
GET  /api/security/rules   - Firewall rules
POST /api/security/rules   - Add firewall rule
GET  /api/network/wifi     - WiFi connection status
POST /api/network/wifi     - Configure WiFi
GET  /api/logs             - Security event logs
POST /api/settings         - Update configuration
```

## 💾 Data Storage Architecture

### Configuration Storage (EEPROM/Flash)
```cpp
struct DeviceConfig {
    // WiFi Settings
    char wifiSSID[32];
    char wifiPassword[64];
    
    // Security Settings
    bool vpnEnabled;
    bool macRandomizationEnabled;
    unsigned long macChangeInterval;
    bool dnsFilterEnabled;
    bool firewallEnabled;
    
    // Advanced Settings
    uint8_t securityProfile;
    bool loggingEnabled;
    uint16_t webServerPort;
};
```

### Runtime Data Structures
```cpp
struct SecurityStats {
    unsigned long packetsProcessed;
    unsigned long packetsBlocked;
    unsigned long threatsDetected;
    unsigned long macChanges;
    unsigned long uptime;
    float throughput;
};

struct NetworkStatus {
    bool wifiConnected;
    char connectedSSID[32];
    int signalStrength;
    IPAddress localIP;
    IPAddress gatewayIP;
    bool internetConnected;
};
```

## 🔌 Hardware Interface Design

### Pin Assignments (ESP32)
```cpp
// Status LEDs
#define STATUS_LED_PIN     2    // Green: Device ready
#define ACTIVITY_LED_PIN   4    // Blue: Network activity
#define ALERT_LED_PIN      5    // Red: Security alert

// Control Buttons
#define MODE_BUTTON_PIN    12   // Cycle security profiles
#define RESET_BUTTON_PIN   13   // Factory reset

// Expansion Pins (for future use)
#define EXPANSION_1        25
#define EXPANSION_2        26
#define EXPANSION_3        27
```

### LED Status Indicators
```
Status LED (Green):
- Solid: Device ready, no internet
- Slow blink: Connecting to WiFi
- Fast blink: Configuration mode
- Off: Device error

Activity LED (Blue):
- Blinks with network traffic
- Brightness indicates throughput

Alert LED (Red):
- Solid: Critical security threat
- Slow blink: Warning level threat
- Fast blink: Configuration error
```

## 🧪 Testing Architecture

### Unit Testing Framework
```cpp
// Test modules for each component
class TestSuite {
public:
    void testMACRandomization();
    void testFirewallRules();
    void testDNSFiltering();
    void testVPNTunnel();
    void testPacketProcessing();
    void testWebInterface();
};
```

### Simulation Testing
```python
# Python bridge for virtual testing
class WokwiBridge:
    def simulate_packet_flow(self):
        # Send test packets through virtual device
        pass
        
    def validate_security_rules(self):
        # Verify security processing
        pass
        
    def performance_benchmark(self):
        # Measure processing speed
        pass
```

## 🚀 Performance Specifications

### Target Performance Metrics
```
Throughput: > 10 Mbps (realistic for public WiFi)
Latency: < 10ms additional delay
Memory Usage: < 200KB RAM
Flash Usage: < 1MB program space
Power Consumption: < 500mA @ 5V USB
MAC Change Time: < 2 seconds
Boot Time: < 30 seconds
```

## 🔒 Security Considerations

### Threat Model
```
Threats We Protect Against:
✅ Man-in-the-middle attacks
✅ Packet sniffing
✅ Malicious hotspots
✅ DNS poisoning
✅ Port scanning
✅ Device tracking
✅ Malware communication

Threats Outside Scope:
❌ Physical device tampering
❌ USB host malware
❌ Compromised firmware
❌ Advanced persistent threats
```

## 📋 Implementation Priorities

### Phase 1: Core Infrastructure
1. Basic WiFi connection and USB interface
2. Web server and configuration interface
3. Packet forwarding functionality
4. Basic firewall rules

### Phase 2: Security Features
1. MAC address randomization
2. DNS filtering
3. Intrusion detection signatures
4. VPN tunnel implementation

### Phase 3: Advanced Features
1. Security profiles
2. Attack pattern learning
3. Performance optimization
4. Advanced logging and analytics

---
**Document Status:** Technical specification - ready for implementation  
**Last Updated:** [Current Date]  
**Dependencies:** PROJECT_REQUIREMENTS.md 