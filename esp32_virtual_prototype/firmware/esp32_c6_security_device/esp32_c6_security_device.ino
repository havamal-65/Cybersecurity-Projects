// ESP32 WiFi Security Device - Combined Implementation
// Merges working network code with security device features

#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <esp_wifi.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// --- Pin Configuration ---
#define LED_STATUS 2      // Matches wokwi diagram
#define LED_ACTIVITY 4    
#define LED_ALERT 5       
#define BTN_CONFIG 18     
#define BTN_RESET 19
#define BTN_MODE 16       // New mode button
#define BTN_SELECT 17     // New select button      

// --- Network Configuration ---
#define DEVICE_NAME "SecureShield"
#define AP_SSID "SecureShield-Config"
#define AP_PASS "configure123"

// --- Security Configuration ---
#define MAC_RANDOM_INTERVAL 600000    // 10 minutes default (configurable)
#define DNS_BLOCK_LIST_SIZE 10
#define PACKET_BUFFER_SIZE 1500
#define UDP_RX_PACKET_MAX_SIZE 512

// --- Global Objects ---
WebServer server(80);
DNSServer dnsServer;
WiFiUDP udp;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // 16x2 LCD at I2C address 0x27

// --- Device State ---
enum DeviceMode {
  MODE_CONFIG,      // AP mode for configuration
  MODE_PROTECTING,  // STA mode, actively filtering
  MODE_LEARNING     // STA mode, learning network patterns
};

// --- Menu System ---
enum MenuScreen {
  MENU_STATUS,      // Show current status
  MENU_FEATURES,    // Toggle features on/off
  MENU_NETWORK,     // Network settings
  MENU_STATS,       // Statistics
  MENU_MAX
};

struct MenuState {
  MenuScreen currentScreen;
  int selectedItem;
  int maxItems[MENU_MAX];
} menu;

struct SecurityState {
  DeviceMode mode;
  bool macRandomEnabled;
  bool dnsFilterEnabled;
  bool firewallEnabled;
  bool udpMonitorEnabled;
  uint32_t packetsProcessed;
  uint32_t threatsBlocked;
  uint32_t dnsQueriesBlocked;
  uint8_t currentMac[6];
  uint8_t originalMac[6];
  unsigned long lastMacChange;
  unsigned long lastPacketTime;
  // Network settings
  char upstream_ssid[32];
  char upstream_pass[64];
  bool hasUpstreamConfig;
} state;

// --- Timing Variables ---
unsigned long lastStatsUpdate = 0;
unsigned long lastLedUpdate = 0;
unsigned long lastNetworkCheck = 0;

// --- Network Monitoring ---
const int localUdpPort = 4210;
char packetBuffer[UDP_RX_PACKET_MAX_SIZE + 1];
bool promiscuousEnabled = false;

// --- DNS Block List ---
const char* blockedDomains[DNS_BLOCK_LIST_SIZE] = {
  "malicious.com",
  "phishing.net",
  "tracker.com",
  "ads.doubleclick.net",
  "malware.bad",
  "", "", "", "", ""  // Empty slots
};

// --- Function Prototypes ---
void initializeDevice();
void generateRandomMac(uint8_t *mac);
bool applyMacAddress(const uint8_t *mac);
void startConfigMode();
void startProtectionMode();
void connectToUpstream();
void handleButtons();
void updateLEDs();
void printStats();
void processNetworkTraffic();
void handleUDPMonitoring();
bool isDomainBlocked(const char* domain);
void performMacRandomization();
void simulatePacketProcessing();
void updateDisplay();
void handleMenuNavigation();

// --- Web Handlers ---
void handleRoot();
void handleStatus();
void handleConfig();
void handleSave();
void handleStart();
void handleStop();

// --- Packet Processing Callback ---
// WOKWI: Modified for simulator - simulates packet processing
void simulatePacketProcessing() {
  if (state.mode != MODE_PROTECTING) return;
  
  // Simulate packet arrival
  if (random(10) < 3) {  // 30% chance per loop
    state.packetsProcessed++;
    state.lastPacketTime = millis();
    
    // Quick activity indication
    digitalWrite(LED_ACTIVITY, !digitalRead(LED_ACTIVITY));
    
    // Simulate threat detection
    if (random(100) < 5) {  // 5% chance
      state.threatsBlocked++;
      digitalWrite(LED_ALERT, HIGH);
    }
  }
}

// --- SETUP ---
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize random seed
  randomSeed(analogRead(0));
  
  Serial.println("\n=====================================");
  Serial.println("   ESP32-C6 Security Device v2.0");
  Serial.println("   WiFi 6 + Thread/Zigbee Support");
  Serial.println("=====================================\n");
  
  initializeDevice();
  
  // Start in config mode
  startConfigMode();
  
  Serial.println("\nDevice ready!");
  Serial.println("Connect to WiFi: " + String(AP_SSID));
  Serial.println("Password: " + String(AP_PASS));
  Serial.println("Browse to: 192.168.4.1");
}

// --- MAIN LOOP ---
void loop() {
  // Handle web server and DNS
  server.handleClient();
  if (state.mode == MODE_CONFIG) {
    dnsServer.processNextRequest();
  }
  
  // Check buttons
  handleButtons();
  handleMenuNavigation();
  
  // Mode-specific operations
  switch (state.mode) {
    case MODE_CONFIG:
      // Just serve web interface
      break;
      
    case MODE_PROTECTING:
      // Check if we need to randomize MAC
      if (state.macRandomEnabled && 
          (millis() - state.lastMacChange > MAC_RANDOM_INTERVAL)) {
        performMacRandomization();
      }
      
      // Monitor network
      processNetworkTraffic();
      
      // WOKWI: Simulate packet processing
      simulatePacketProcessing();
      
      // Check connection health
      if (millis() - lastNetworkCheck > 5000) {
        if (WiFi.status() != WL_CONNECTED) {
          Serial.println("WiFi disconnected! Reconnecting...");
          connectToUpstream();
        }
        lastNetworkCheck = millis();
      }
      break;
      
    case MODE_LEARNING:
      // TODO: Implement learning mode
      break;
  }
  
  // Update UI elements
  updateLEDs();
  
  // Print statistics
  if (millis() - lastStatsUpdate > 5000) {
    printStats();
    updateDisplay();
    lastStatsUpdate = millis();
  }
}

// --- INITIALIZATION ---
void initializeDevice() {
  // Initialize pins
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_ACTIVITY, OUTPUT);
  pinMode(LED_ALERT, OUTPUT);
  pinMode(BTN_CONFIG, INPUT_PULLUP);
  pinMode(BTN_RESET, INPUT_PULLUP);
  pinMode(BTN_MODE, INPUT_PULLUP);
  pinMode(BTN_SELECT, INPUT_PULLUP);
  
  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("SecureShield");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  // Initialize state
  state.mode = MODE_CONFIG;
  state.macRandomEnabled = true;
  state.dnsFilterEnabled = true;
  state.firewallEnabled = true;
  state.udpMonitorEnabled = true;
  state.packetsProcessed = 0;
  state.threatsBlocked = 0;
  state.dnsQueriesBlocked = 0;
  state.lastMacChange = millis();
  state.hasUpstreamConfig = false;
  
  // Get original MAC
  WiFi.mode(WIFI_AP_STA);
  esp_wifi_get_mac(WIFI_IF_STA, state.originalMac);
  memcpy(state.currentMac, state.originalMac, 6);
  
  // Startup LED sequence
  for(int i = 0; i < 3; i++) {
    digitalWrite(LED_STATUS, HIGH);
    digitalWrite(LED_ACTIVITY, HIGH);
    digitalWrite(LED_ALERT, HIGH);
    delay(200);
    digitalWrite(LED_STATUS, LOW);
    digitalWrite(LED_ACTIVITY, LOW);
    digitalWrite(LED_ALERT, LOW);
    delay(200);
  }
}

// --- MAC ADDRESS FUNCTIONS ---
void generateRandomMac(uint8_t *mac) {
  for (int i = 0; i < 6; ++i) {
    mac[i] = random(256);
  }
  // Set locally administered bit, clear multicast bit
  mac[0] = (mac[0] | 0x02) & 0xFE;
}

bool applyMacAddress(const uint8_t *mac) {
  esp_err_t result = esp_wifi_set_mac(WIFI_IF_STA, mac);
  if (result == ESP_OK) {
    memcpy(state.currentMac, mac, 6);
    Serial.print("MAC Address changed to: ");
    for(int i = 0; i < 6; i++) {
      if(i > 0) Serial.print(":");
      Serial.printf("%02X", mac[i]);
    }
    Serial.println();
    return true;
  } else {
    Serial.printf("Failed to set MAC. Error: %d\n", result);
    return false;
  }
}

void performMacRandomization() {
  Serial.println("\n[MAC] Randomization time reached");
  
  // Generate new MAC
  uint8_t newMac[6];
  generateRandomMac(newMac);
  
  // Must disconnect to change MAC
  WiFi.disconnect();
  delay(100);
  
  // Apply new MAC
  if (applyMacAddress(newMac)) {
    state.lastMacChange = millis();
    
    // Reconnect with new MAC
    connectToUpstream();
  } else {
    Serial.println("[MAC] Randomization failed, keeping current MAC");
  }
}

// --- NETWORK MODES ---
void startConfigMode() {
  Serial.println("\n[MODE] Starting Configuration Mode");
  state.mode = MODE_CONFIG;
  
  // Setup Access Point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);
  
  // Start DNS server (captive portal)
  dnsServer.start(53, "*", IP);
  
  // Setup web routes
  server.on("/", handleRoot);
  server.on("/status", handleStatus);
  server.on("/config", handleConfig);
  server.on("/save", handleSave);
  server.on("/start", handleStart);
  server.on("/stop", handleStop);
  server.begin();
  
  digitalWrite(LED_STATUS, HIGH);  // Solid = Config mode
}

void startProtectionMode() {
  if (!state.hasUpstreamConfig) {
    Serial.println("[ERROR] No upstream network configured!");
    return;
  }
  
  Serial.println("\n[MODE] Starting Protection Mode");
  state.mode = MODE_PROTECTING;
  
  // Switch to Station mode
  WiFi.mode(WIFI_STA);
  
  // Connect to upstream network
  connectToUpstream();
  
  // Start UDP monitoring if enabled
  if (state.udpMonitorEnabled) {
    if (udp.begin(localUdpPort)) {
      Serial.printf("[UDP] Monitoring on port %d\n", localUdpPort);
    }
  }
  
  // Enable promiscuous mode for packet capture
  // Note: This may impact performance
  // WOKWI: Promiscuous mode disabled for simulator compatibility
  /*
  if (state.firewallEnabled) {
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_promiscuous_rx_cb(&wifi_promiscuous_cb);
    promiscuousEnabled = true;
    Serial.println("[FIREWALL] Promiscuous mode enabled");
  }
  */
  Serial.println("[FIREWALL] Simulated mode enabled (Wokwi compatible)");
}

void connectToUpstream() {
  Serial.printf("\n[WIFI] Connecting to %s", state.upstream_ssid);
  
  WiFi.begin(state.upstream_ssid, state.upstream_pass);
  
  int retries = 20;
  while (WiFi.status() != WL_CONNECTED && retries > 0) {
    Serial.print(".");
    delay(500);
    retries--;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
  } else {
    Serial.println("\n[WIFI] Connection failed!");
    // Return to config mode
    startConfigMode();
  }
}

// --- NETWORK MONITORING ---
void processNetworkTraffic() {
  // Handle UDP monitoring
  if (state.udpMonitorEnabled) {
    handleUDPMonitoring();
  }
  
  // DNS filtering would go here
  // Firewall rules would be applied in the promiscuous callback
}

void handleUDPMonitoring() {
  int packetSize = udp.parsePacket();
  if (packetSize > 0) {
    int len = udp.read(packetBuffer, UDP_RX_PACKET_MAX_SIZE);
    if (len > 0) {
      packetBuffer[len] = 0;
      
      // Log packet
      Serial.printf("\n[UDP] Packet from %s:%d (%d bytes)\n", 
                    udp.remoteIP().toString().c_str(),
                    udp.remotePort(),
                    packetSize);
      
      // Check for suspicious patterns
      // This is where you'd implement actual security checks
      if (strstr(packetBuffer, "malicious") != NULL) {
        state.threatsBlocked++;
        Serial.println("[THREAT] Blocked malicious UDP packet!");
        digitalWrite(LED_ALERT, HIGH);
      }
    }
  }
}

// --- USER INTERFACE ---
void handleButtons() {
  static unsigned long lastConfigPress = 0;
  static unsigned long lastResetPress = 0;
  
  // Config button - quick press toggles protection
  if (digitalRead(BTN_CONFIG) == LOW && millis() - lastConfigPress > 500) {
    if (state.mode == MODE_CONFIG) {
      startProtectionMode();
    } else {
      Serial.println("[BUTTON] Returning to config mode");
      WiFi.disconnect();
      // WOKWI: Promiscuous mode handling disabled
      /*
      if (promiscuousEnabled) {
        esp_wifi_set_promiscuous(false);
        promiscuousEnabled = false;
      }
      */
      startConfigMode();
    }
    lastConfigPress = millis();
  }
  
  // Reset button - hold 3 seconds for factory reset
  if (digitalRead(BTN_RESET) == LOW) {
    if (millis() - lastResetPress > 3000) {
      Serial.println("\n[RESET] Factory reset!");
      // TODO: Clear stored settings
      ESP.restart();
    }
  } else {
    lastResetPress = millis();
  }
}

void updateLEDs() {
  // Status LED
  switch (state.mode) {
    case MODE_CONFIG:
      digitalWrite(LED_STATUS, HIGH);  // Solid in config
      break;
    case MODE_PROTECTING:
      // Blink while protecting
      digitalWrite(LED_STATUS, (millis() / 1000) % 2);
      break;
    case MODE_LEARNING:
      // Fast blink in learning mode
      digitalWrite(LED_STATUS, (millis() / 250) % 2);
      break;
  }
  
  // Activity LED - controlled by packet handler
  
  // Alert LED - clear after 1 second
  static unsigned long alertTime = 0;
  if (digitalRead(LED_ALERT) == HIGH) {
    if (alertTime == 0) {
      alertTime = millis();
    } else if (millis() - alertTime > 1000) {
      digitalWrite(LED_ALERT, LOW);
      alertTime = 0;
    }
  }
}

void printStats() {
  if (state.mode != MODE_PROTECTING) return;
  
  Serial.println("\n========== Security Stats ==========");
  Serial.printf("Packets Processed: %u\n", state.packetsProcessed);
  Serial.printf("Threats Blocked: %u\n", state.threatsBlocked);
  Serial.printf("DNS Queries Blocked: %u\n", state.dnsQueriesBlocked);
  Serial.printf("Current MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
                state.currentMac[0], state.currentMac[1], state.currentMac[2],
                state.currentMac[3], state.currentMac[4], state.currentMac[5]);
  Serial.printf("Uptime: %lu seconds\n", millis() / 1000);
  Serial.println("===================================\n");
}

// --- WEB INTERFACE ---
void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <title>SecureShield Configuration</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <style>
    body { 
      font-family: -apple-system, Arial, sans-serif; 
      background: #1a1a1a; 
      color: #e0e0e0;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
    }
    h1 { 
      color: #4CAF50;
      text-align: center;
    }
    .card {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 10px;
      margin: 20px 0;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .status {
      padding: 15px;
      margin: 10px 0;
      border-radius: 5px;
      font-weight: bold;
      text-align: center;
    }
    .protecting { 
      background: #4CAF50; 
      color: white; 
    }
    .config { 
      background: #ff9800; 
      color: white; 
    }
    .stat {
      display: flex;
      justify-content: space-between;
      padding: 10px;
      border-bottom: 1px solid #444;
    }
    .stat:last-child {
      border-bottom: none;
    }
    input[type="text"], input[type="password"] {
      width: 100%;
      padding: 10px;
      margin: 5px 0;
      border: 1px solid #444;
      border-radius: 5px;
      background: #333;
      color: white;
      box-sizing: border-box;
    }
    button {
      background: #4CAF50;
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 16px;
      border-radius: 5px;
      cursor: pointer;
      margin: 5px;
      width: 100%;
    }
    button:hover {
      background: #45a049;
    }
    .stop {
      background: #f44336;
    }
    .stop:hover {
      background: #da190b;
    }
    .toggle {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
    }
    .switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 24px;
    }
    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: .4s;
      border-radius: 24px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
    input:checked + .slider {
      background-color: #4CAF50;
    }
    input:checked + .slider:before {
      transform: translateX(26px);
    }
  </style>
  <script>
    function updateStatus() {
      fetch('/status')
        .then(response => response.json())
        .then(data => {
          document.getElementById('status').innerHTML = data.mode == 'protecting' ? 
            '<div class="status protecting">✓ PROTECTING</div>' : 
            '<div class="status config">⚙ CONFIGURATION MODE</div>';
          document.getElementById('packets').textContent = data.packets;
          document.getElementById('threats').textContent = data.threats;
          document.getElementById('dns').textContent = data.dns_blocked;
          document.getElementById('mac').textContent = data.mac;
          document.getElementById('uptime').textContent = data.uptime + 's';
        });
    }
    setInterval(updateStatus, 2000);
    window.onload = updateStatus;
  </script>
</head>
<body>
  <div class='container'>
    <h1>🛡️ SecureShield</h1>
    <div id='status'></div>
    
    <div class='card'>
      <h2>📊 Statistics</h2>
      <div class='stat'>
        <span>Packets Processed:</span>
        <span id='packets'>0</span>
      </div>
      <div class='stat'>
        <span>Threats Blocked:</span>
        <span id='threats'>0</span>
      </div>
      <div class='stat'>
        <span>DNS Blocked:</span>
        <span id='dns'>0</span>
      </div>
      <div class='stat'>
        <span>Current MAC:</span>
        <span id='mac' style='font-family: monospace'>--:--:--:--:--:--</span>
      </div>
      <div class='stat'>
        <span>Uptime:</span>
        <span id='uptime'>0s</span>
      </div>
    </div>
    
    <div class='card'>
      <h2>🔧 Configuration</h2>
      <form action='/config' method='get'>
        <button type='submit'>Network Settings</button>
      </form>
      <button onclick=\"fetch('/start')\">Start Protection</button>
      <button class='stop' onclick=\"fetch('/stop')\">Stop Protection</button>
    </div>
  </div>
</body>
</html>
  )";
  server.send(200, "text/html", html);
}

void handleConfig() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
  <title>Network Configuration</title>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <style>
    body { 
      font-family: -apple-system, Arial, sans-serif; 
      background: #1a1a1a; 
      color: #e0e0e0;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 500px;
      margin: 0 auto;
    }
    h1 { 
      color: #4CAF50;
      text-align: center;
    }
    .card {
      background: #2a2a2a;
      padding: 20px;
      border-radius: 10px;
      margin: 20px 0;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    input[type="text"], input[type="password"] {
      width: 100%;
      padding: 10px;
      margin: 5px 0 15px 0;
      border: 1px solid #444;
      border-radius: 5px;
      background: #333;
      color: white;
      box-sizing: border-box;
    }
    label {
      display: block;
      margin-top: 10px;
      color: #ccc;
    }
    button {
      background: #4CAF50;
      color: white;
      border: none;
      padding: 12px 24px;
      font-size: 16px;
      border-radius: 5px;
      cursor: pointer;
      width: 100%;
      margin-top: 10px;
    }
    button:hover {
      background: #45a049;
    }
    .back {
      background: #666;
    }
    .back:hover {
      background: #555;
    }
    .toggle {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
    }
    .switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 24px;
    }
    .switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #666;
      transition: .4s;
      border-radius: 24px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
    input:checked + .slider {
      background-color: #4CAF50;
    }
    input:checked + .slider:before {
      transform: translateX(26px);
    }
  </style>
</head>
<body>
  <div class='container'>
    <h1>⚙️ Network Configuration</h1>
    
    <div class='card'>
      <h2>WiFi Settings</h2>
      <form action='/save' method='post'>
        <label for='ssid'>Network Name (SSID):</label>
        <input type='text' id='ssid' name='ssid' placeholder='Your WiFi network name' required>
        
        <label for='pass'>Password:</label>
        <input type='password' id='pass' name='pass' placeholder='WiFi password'>
        
        <h3>Security Features</h3>
        
        <div class='toggle'>
          <span>MAC Randomization</span>
          <label class='switch'>
            <input type='checkbox' name='mac' checked>
            <span class='slider'></span>
          </label>
        </div>
        
        <div class='toggle'>
          <span>DNS Filtering</span>
          <label class='switch'>
            <input type='checkbox' name='dns' checked>
            <span class='slider'></span>
          </label>
        </div>
        
        <div class='toggle'>
          <span>Firewall</span>
          <label class='switch'>
            <input type='checkbox' name='firewall' checked>
            <span class='slider'></span>
          </label>
        </div>
        
        <div class='toggle'>
          <span>UDP Monitoring</span>
          <label class='switch'>
            <input type='checkbox' name='udp' checked>
            <span class='slider'></span>
          </label>
        </div>
        
        <button type='submit'>Save Configuration</button>
      </form>
      <button class='back' onclick=\"window.location='/'\">Back</button>
    </div>
  </div>
</body>
</html>
  )";
  server.send(200, "text/html", html);
}

void handleSave() {
  // Save network credentials
  String ssid = server.arg("ssid");
  String pass = server.arg("pass");
  
  if (ssid.length() > 0) {
    ssid.toCharArray(state.upstream_ssid, 32);
    pass.toCharArray(state.upstream_pass, 64);
    state.hasUpstreamConfig = true;
    
    // Save feature toggles
    state.macRandomEnabled = server.hasArg("mac");
    state.dnsFilterEnabled = server.hasArg("dns");
    state.firewallEnabled = server.hasArg("firewall");
    state.udpMonitorEnabled = server.hasArg("udp");
    
    Serial.println("\n[CONFIG] Settings saved:");
    Serial.printf("SSID: %s\n", state.upstream_ssid);
    Serial.printf("MAC Random: %s\n", state.macRandomEnabled ? "ON" : "OFF");
    Serial.printf("DNS Filter: %s\n", state.dnsFilterEnabled ? "ON" : "OFF");
    Serial.printf("Firewall: %s\n", state.firewallEnabled ? "ON" : "OFF");
    Serial.printf("UDP Monitor: %s\n", state.udpMonitorEnabled ? "ON" : "OFF");
    
    server.send(200, "text/html", "<html><body><h1>Settings Saved!</h1><p>Redirecting...</p><script>setTimeout(function(){window.location='/';},2000);</script></body></html>");
  } else {
    server.send(400, "text/html", "<html><body><h1>Error: SSID required</h1></body></html>");
  }
}

void handleStart() {
  if (state.mode != MODE_PROTECTING) {
    startProtectionMode();
  }
  server.send(200, "text/plain", "Protection started");
}

void handleStop() {
  if (state.mode == MODE_PROTECTING) {
    Serial.println("[STOP] Stopping protection mode");
    WiFi.disconnect();
    if (promiscuousEnabled) {
      esp_wifi_set_promiscuous(false);
      promiscuousEnabled = false;
    }
    startConfigMode();
  }
  server.send(200, "text/plain", "Protection stopped");
}

void handleStatus() {
  String json = "{";
  json += "\"mode\":\"" + String(state.mode == MODE_PROTECTING ? "protecting" : "config") + "\",";
  json += "\"packets\":" + String(state.packetsProcessed) + ",";
  json += "\"threats\":" + String(state.threatsBlocked) + ",";
  json += "\"dns_blocked\":" + String(state.dnsQueriesBlocked) + ",";
  json += "\"uptime\":" + String(millis() / 1000) + ",";
  json += "\"mac\":\"";
  for(int i = 0; i < 6; i++) {
    if(i > 0) json += ":";
    char hex[3];
    sprintf(hex, "%02X", state.currentMac[i]);
    json += hex;
  }
  json += "\"}";
  
  server.send(200, "application/json", json);
}

// --- DISPLAY FUNCTIONS ---
void updateDisplay() {
  lcd.clear();
  
  switch (menu.currentScreen) {
    case MENU_STATUS:
      lcd.setCursor(0, 0);
      lcd.print(state.mode == MODE_PROTECTING ? "PROTECTING" : "CONFIG MODE");
      lcd.setCursor(0, 1);
      lcd.print("Threats: ");
      lcd.print(state.threatsBlocked);
      break;
      
    case MENU_FEATURES:
      lcd.setCursor(0, 0);
      lcd.print("Features:");
      lcd.setCursor(0, 1);
      switch (menu.selectedItem) {
        case 0: lcd.print("MAC Rand: "); lcd.print(state.macRandomEnabled ? "ON" : "OFF"); break;
        case 1: lcd.print("DNS Filt: "); lcd.print(state.dnsFilterEnabled ? "ON" : "OFF"); break;
        case 2: lcd.print("Firewall: "); lcd.print(state.firewallEnabled ? "ON" : "OFF"); break;
        case 3: lcd.print("UDP Mon: "); lcd.print(state.udpMonitorEnabled ? "ON" : "OFF"); break;
      }
      break;
      
    case MENU_NETWORK:
      lcd.setCursor(0, 0);
      lcd.print("WiFi Network:");
      lcd.setCursor(0, 1);
      if (state.hasUpstreamConfig) {
        lcd.print(state.upstream_ssid);
      } else {
        lcd.print("Not configured");
      }
      break;
      
    case MENU_STATS:
      lcd.setCursor(0, 0);
      lcd.print("Packets: ");
      lcd.print(state.packetsProcessed);
      lcd.setCursor(0, 1);
      lcd.print("Blocked: ");
      lcd.print(state.threatsBlocked);
      break;
  }
}

void handleMenuNavigation() {
  static unsigned long lastModePress = 0;
  static unsigned long lastSelectPress = 0;
  
  // Mode button - cycle through menu screens
  if (digitalRead(BTN_MODE) == LOW && millis() - lastModePress > 300) {
    menu.currentScreen = (MenuScreen)((menu.currentScreen + 1) % MENU_MAX);
    menu.selectedItem = 0;
    updateDisplay();
    lastModePress = millis();
  }
  
  // Select button - interact with current screen
  if (digitalRead(BTN_SELECT) == LOW && millis() - lastSelectPress > 300) {
    switch (menu.currentScreen) {
      case MENU_FEATURES:
        // Toggle the selected feature
        switch (menu.selectedItem) {
          case 0: state.macRandomEnabled = !state.macRandomEnabled; break;
          case 1: state.dnsFilterEnabled = !state.dnsFilterEnabled; break;
          case 2: state.firewallEnabled = !state.firewallEnabled; break;
          case 3: state.udpMonitorEnabled = !state.udpMonitorEnabled; break;
        }
        menu.selectedItem = (menu.selectedItem + 1) % 4;
        updateDisplay();
        break;
        
      case MENU_STATUS:
        // Config button function - toggle protection mode
        if (state.mode == MODE_CONFIG) {
          startProtectionMode();
        } else {
          WiFi.disconnect();
          startConfigMode();
        }
        break;
    }
    lastSelectPress = millis();
  }
}