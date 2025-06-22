# ESP32 Virtual Prototype - Feature Specifications

## 🛡️ Core Security Features

### 1. MAC Address Randomization

#### Purpose
Prevent device tracking across different WiFi networks by regularly changing the device's MAC address.

#### Specifications
- **Default Interval:** 10 minutes
- **Configurable Range:** 30 seconds to 24 hours
- **Change Triggers:**
  - Time-based (configurable intervals)
  - Network disconnection
  - Manual trigger via web interface
  - Security profile switching

#### Implementation Details
```cpp
struct MACConfig {
    bool enabled;                    // Enable/disable MAC randomization
    unsigned long changeInterval;    // Interval in milliseconds
    bool changeOnDisconnect;        // Change MAC when disconnecting from WiFi
    bool preserveOUI;               // Keep manufacturer prefix (first 3 bytes)
    uint8_t currentMAC[6];          // Currently active MAC address
    unsigned long lastChange;        // Timestamp of last MAC change
};
```

#### User Interface
- **Dashboard Display:** Current MAC address with time until next change
- **Configuration Options:**
  - Enable/disable randomization
  - Set change interval (slider: 30sec - 24hr)
  - Manual "Change Now" button
  - Option to preserve manufacturer OUI

#### Security Benefits
- Prevents location tracking by retail stores
- Stops network correlation across different locations  
- Protects privacy from WiFi analytics systems
- Reduces digital fingerprinting effectiveness

---

### 2. Advanced Firewall Engine

#### Purpose
Provide configurable packet filtering with protocol, port, and IP-based rules.

#### Specifications
- **Maximum Rules:** 50 configurable rules
- **Rule Types:** Allow, Block, Log-only
- **Protocols Supported:** TCP, UDP, ICMP
- **Default Profiles:** Basic, Strict, Custom

#### Rule Structure
```cpp
struct FirewallRule {
    bool enabled;                   // Rule active/inactive
    uint8_t protocol;              // TCP=6, UDP=17, ICMP=1, ANY=0
    uint32_t srcIP;                // Source IP (0 = any)
    uint32_t srcMask;              // Source netmask
    uint32_t dstIP;                // Destination IP (0 = any)
    uint32_t dstMask;              // Destination netmask
    uint16_t srcPortStart;         // Source port range start
    uint16_t srcPortEnd;           // Source port range end
    uint16_t dstPortStart;         // Destination port range start
    uint16_t dstPortEnd;           // Destination port range end
    uint8_t action;                // ALLOW=0, BLOCK=1, LOG=2
    uint8_t priority;              // Rule priority (1-10)
    char description[64];          // Human-readable description
    unsigned long hitCount;        // Number of times rule matched
};
```

#### Default Rules
**Basic Profile:**
- Allow HTTP (80) and HTTPS (443) outbound
- Allow DNS (53) outbound
- Block all inbound connections
- Allow established connections

**Strict Profile:**
- Allow only HTTPS (443) outbound
- Allow DNS (53) to specific servers only
- Block all other traffic
- Enhanced logging

#### User Interface
- **Rule Management:** Add/edit/delete rules via web interface
- **Quick Profiles:** Pre-configured security profiles
- **Real-time Monitoring:** Live traffic matching rules
- **Statistics:** Rule hit counts and effectiveness

---

### 3. DNS Filtering & Protection

#### Purpose
Block access to malicious domains and prevent DNS-based attacks.

#### Specifications
- **Blocked Domain Lists:** Malware, phishing, tracking, adult content
- **Custom Domains:** User-configurable block/allow lists
- **DNS Servers:** Configurable secure DNS providers
- **Response Types:** Block (NXDOMAIN) or redirect to warning page

#### Implementation
```cpp
struct DNSFilter {
    bool enabled;                   // DNS filtering active
    uint8_t blocklistSources;      // Bitmask of enabled blocklists
    uint8_t blockAction;           // NXDOMAIN=0, REDIRECT=1, LOG=2
    IPAddress primaryDNS;          // Primary DNS server
    IPAddress secondaryDNS;        // Secondary DNS server
    bool logQueries;               // Log all DNS queries
    bool blockTelemetry;           // Block OS/app telemetry
    char customBlockDomains[10][64]; // Custom blocked domains
    char customAllowDomains[10][64]; // Custom allowed domains
};
```

#### Blocklist Categories
- **Malware Domains:** Known malware C&C servers
- **Phishing Sites:** Fraudulent login/banking sites
- **Tracking Networks:** Advertising and analytics trackers
- **Adult Content:** Adult websites (optional)
- **Social Media:** Social platforms (optional for focus)
- **Gambling Sites:** Online gambling platforms (optional)

#### User Interface
- **Category Toggles:** Enable/disable blocklist categories
- **Custom Lists:** Add custom domains to block/allow
- **DNS Settings:** Choose DNS providers (Cloudflare, Quad9, etc.)
- **Query Log:** Recent DNS queries with block/allow status

---

### 4. Intrusion Detection System (IDS)

#### Purpose
Detect and alert on suspicious network activity and potential attacks.

#### Specifications
- **Detection Methods:** Signature-based pattern matching
- **Attack Types:** Port scans, brute force, injection attempts
- **Alert Levels:** Info, Warning, Critical
- **Response Actions:** Log, block IP, send alert

#### Threat Signatures
```cpp
struct ThreatSignature {
    char name[32];                 // Threat name
    char pattern[128];             // Detection pattern/regex
    uint8_t protocol;              // TCP/UDP/ICMP/ANY
    uint16_t port;                 // Target port (0 = any)
    uint8_t severity;              // 1=Info, 5=Warning, 10=Critical
    uint16_t threshold;            // Hits before triggering
    unsigned long timeWindow;      // Time window for threshold
    uint8_t action;                // LOG=0, BLOCK=1, ALERT=2
    bool enabled;                  // Signature active
    unsigned long hitCount;        // Detection counter
};
```

#### Built-in Detection Patterns
**Port Scanning:**
- Rapid connections to multiple ports
- SYN flood patterns
- Stealth scan techniques

**Brute Force Attacks:**
- Multiple login failures
- Dictionary attack patterns
- Credential stuffing attempts

**Injection Attacks:**
- SQL injection patterns in HTTP traffic
- XSS attack signatures
- Command injection attempts

**Network Reconnaissance:**
- OS fingerprinting attempts
- Service enumeration
- Vulnerability scanning

#### Alert System
- **Real-time Notifications:** Immediate alerts for critical threats
- **Threat Dashboard:** Visual threat timeline and severity indicators
- **Alert Actions:** Block source IP, increase security level, notify user
- **False Positive Management:** Whitelist legitimate traffic patterns

---

### 5. VPN Tunnel Simulation

#### Purpose
Simulate VPN functionality for demonstration and provide encrypted tunnel indicators.

#### Specifications
- **Tunnel Protocols:** OpenVPN simulation, WireGuard simulation
- **Encryption Indicators:** Visual confirmation of encrypted traffic
- **Connection Health:** Monitor tunnel stability and performance
- **Kill Switch:** Block traffic if tunnel fails

#### Implementation
```cpp
struct VPNTunnel {
    bool enabled;                  // VPN tunnel active
    uint8_t protocol;              // OPENVPN=0, WIREGUARD=1
    char serverEndpoint[64];       // VPN server address
    uint16_t serverPort;           // VPN server port
    bool killSwitch;               // Block traffic if VPN fails
    bool dnsLeakProtection;        // Force DNS through tunnel
    uint8_t encryptionLevel;       // AES128=0, AES256=1
    unsigned long bytesEncrypted;  // Traffic processed through tunnel
    bool connected;                // Tunnel connection status
    uint16_t latency;              // Tunnel latency in ms
    float throughput;              // Tunnel throughput in Mbps
};
```

#### Simulation Features
- **Packet Marking:** Mark packets as "encrypted" for demonstration
- **Latency Simulation:** Add realistic VPN latency to connections
- **Throughput Throttling:** Simulate VPN bandwidth limitations
- **Connection Health:** Monitor and display tunnel statistics

#### User Interface
- **Connection Status:** Visual indicator of VPN tunnel status
- **Server Selection:** Choose simulated VPN server locations
- **Performance Metrics:** Display latency, throughput, uptime
- **Kill Switch Toggle:** Enable/disable traffic blocking on disconnect

---

### 6. Traffic Analysis & Monitoring

#### Purpose
Provide real-time visibility into network traffic patterns and security events.

#### Specifications
- **Real-time Monitoring:** Live traffic statistics and flow analysis
- **Protocol Analysis:** Breakdown of traffic by protocol and application
- **Bandwidth Monitoring:** Upload/download speeds and data usage
- **Security Events:** Timeline of security-related activities

#### Monitoring Capabilities
```cpp
struct TrafficStats {
    unsigned long totalPackets;    // Total packets processed
    unsigned long allowedPackets;  // Packets allowed through
    unsigned long blockedPackets;  // Packets blocked by firewall
    unsigned long encryptedBytes;  // Bytes sent through VPN
    unsigned long maliciousDomains; // Blocked DNS requests
    unsigned long securityEvents;   // IDS detections
    float currentThroughput;       // Current network speed
    float peakThroughput;          // Peak speed this session
    unsigned long sessionDuration; // Current session length
};
```

#### Dashboard Visualizations
- **Real-time Graphs:** Traffic volume over time
- **Protocol Pie Chart:** Traffic breakdown by protocol
- **Security Timeline:** Chronological security events
- **Geographic Map:** Connection origins (simulated)
- **Threat Heatmap:** Attack intensity visualization

---

### 7. Security Profiles System

#### Purpose
Provide one-click security configurations for different use scenarios.

#### Built-in Profiles
**Home Network Profile:**
- Basic firewall rules
- Light DNS filtering (malware only)
- MAC randomization every 2 hours
- VPN optional

**Public WiFi Profile:**
- Strict firewall (block all inbound)
- Aggressive DNS filtering
- MAC randomization every 5 minutes
- VPN mandatory
- Enhanced IDS sensitivity

**Enterprise Profile:**
- Corporate-friendly rules
- Moderate DNS filtering
- MAC randomization every 30 minutes
- Logging emphasis
- Compliance features

**Gaming Profile:**
- Gaming-optimized firewall rules
- Minimal latency VPN
- Reduced security for performance
- Game server whitelist

**Privacy Profile:**
- Maximum anonymization
- Aggressive tracker blocking
- Frequent MAC changes (30 seconds)
- Multiple VPN hops simulation
- Enhanced encryption

#### Custom Profile Creation
- **Profile Editor:** Web interface for creating custom profiles
- **Setting Import/Export:** Share profiles via configuration files
- **Profile Scheduling:** Automatic profile switching based on time/location
- **Profile Inheritance:** Base profiles with custom modifications

---

## 🔧 Configuration & Management

### Web Interface Requirements
- **Responsive Design:** Works on desktop, tablet, and mobile
- **Real-time Updates:** Live status updates without page refresh
- **Intuitive Navigation:** Clear menu structure and breadcrumbs
- **Visual Feedback:** Progress indicators and status animations
- **Help System:** Contextual help and tooltips

### API Endpoints
```
GET  /api/status              - Overall device status
GET  /api/stats               - Traffic and security statistics
GET  /api/firewall/rules      - Firewall rule configuration
POST /api/firewall/rules      - Add/modify firewall rules
GET  /api/dns/settings        - DNS filtering configuration
POST /api/dns/settings        - Update DNS settings
GET  /api/vpn/status          - VPN tunnel status
POST /api/vpn/connect         - Connect/disconnect VPN
GET  /api/ids/alerts          - IDS alerts and detections
GET  /api/mac/current         - Current MAC address
POST /api/mac/randomize       - Trigger MAC randomization
GET  /api/profiles            - Available security profiles
POST /api/profiles/activate   - Switch security profile
```

### Configuration Storage
- **EEPROM Usage:** Store persistent settings in ESP32 EEPROM
- **JSON Format:** Human-readable configuration format
- **Backup/Restore:** Export/import complete device configuration
- **Factory Reset:** Restore to default settings

---

**Document Status:** Feature specifications complete - ready for implementation  
**Last Updated:** [Current Date]  
**Dependencies:** PROJECT_REQUIREMENTS.md, TECHNICAL_ARCHITECTURE.md 