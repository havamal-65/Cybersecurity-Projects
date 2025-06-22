#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <EEPROM.h>

// Pin definitions
#define STATUS_LED 2    // Red LED
#define ACTIVITY_LED 4  // Green LED
#define ALERT_LED 5     // Blue LED
#define CONFIG_BTN 12   // Configuration button
#define RESET_BTN 13    // Reset button

// WiFi settings
const char* AP_SSID = "SecureShield";
const char* AP_PASSWORD = "12345678";
IPAddress AP_IP(192, 168, 4, 1);
IPAddress AP_SUBNET(255, 255, 255, 0);

// Web server and DNS server
WebServer server(80);
DNSServer dnsServer;

// MAC address for randomization
uint8_t mac[6];

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(STATUS_LED, OUTPUT);
  pinMode(ACTIVITY_LED, OUTPUT);
  pinMode(ALERT_LED, OUTPUT);
  pinMode(CONFIG_BTN, INPUT_PULLUP);
  pinMode(RESET_BTN, INPUT_PULLUP);
  
  // Initialize EEPROM
  EEPROM.begin(512);
  
  // Generate random MAC address
  randomMAC();
  
  // Setup WiFi AP
  setupWiFiAP();
  
  // Setup web server
  setupWebServer();
  
  // Setup DNS server
  dnsServer.start(53, "*", AP_IP);
  
  // Initial LED status
  digitalWrite(STATUS_LED, HIGH);
  digitalWrite(ACTIVITY_LED, LOW);
  digitalWrite(ALERT_LED, LOW);
}

void loop() {
  // Handle DNS requests
  dnsServer.processNextRequest();
  
  // Handle web server requests
  server.handleClient();
  
  // Check buttons
  checkButtons();
  
  // Simulate network activity
  simulatePacketProcessing();
  
  // Small delay to prevent CPU hogging
  delay(10);
}

void randomMAC() {
  for(int i = 0; i < 6; i++) {
    mac[i] = random(256);
  }
  // Set locally administered bit
  mac[0] |= 0x02;
  // Clear multicast bit
  mac[0] &= 0xFE;
}

void setupWiFiAP() {
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_IP, AP_SUBNET);
  WiFi.softAP(AP_SSID, AP_PASSWORD);
  
  Serial.println("WiFi AP Started");
  Serial.print("SSID: ");
  Serial.println(AP_SSID);
  Serial.print("IP Address: ");
  Serial.println(AP_IP);
}

void setupWebServer() {
  // Root page
  server.on("/", HTTP_GET, []() {
    String html = "<html><body>";
    html += "<h1>SecureShield Control Panel</h1>";
    html += "<p>Status: Active</p>";
    html += "<p>MAC Address: ";
    for(int i = 0; i < 6; i++) {
      if(mac[i] < 16) html += "0";
      html += String(mac[i], HEX);
      if(i < 5) html += ":";
    }
    html += "</p>";
    html += "</body></html>";
    server.send(200, "text/html", html);
  });
  
  server.begin();
}

void checkButtons() {
  static bool lastConfigState = HIGH;
  static bool lastResetState = HIGH;
  
  bool currentConfigState = digitalRead(CONFIG_BTN);
  bool currentResetState = digitalRead(RESET_BTN);
  
  // Config button pressed
  if(currentConfigState == LOW && lastConfigState == HIGH) {
    digitalWrite(ACTIVITY_LED, !digitalRead(ACTIVITY_LED));
    delay(50); // Debounce
  }
  
  // Reset button pressed
  if(currentResetState == LOW && lastResetState == HIGH) {
    digitalWrite(ALERT_LED, !digitalRead(ALERT_LED));
    delay(50); // Debounce
  }
  
  lastConfigState = currentConfigState;
  lastResetState = currentResetState;
}

void simulatePacketProcessing() {
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  
  if(millis() - lastBlink > 1000) {
    ledState = !ledState;
    digitalWrite(STATUS_LED, ledState);
    lastBlink = millis();
  }
} 