# 🔐 Bright Data Security MCP Server

A cybersecurity research platform combining **Bright Data MCP Server** with **Cloud AI Security Researcher** capabilities for comprehensive threat intelligence gathering.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Bright Data account (optional for testing)

### Installation
```bash
# Install dependencies
npm install

# Build the project
npm run build

# Test the server
npm test
```

## 🔧 Configuration

### 1. Get Bright Data API (Optional)
- Sign up at [brightdata.com](https://brightdata.com)
- Get your API token and Zone ID from the dashboard

### 2. Set Environment Variables
```bash
# Copy example
cp .env.example .env

# Edit with your credentials
BRIGHT_DATA_API_TOKEN=your_token_here
BRIGHT_DATA_ZONE_ID=your_zone_id_here
```

### 3. Start the MCP Server
```bash
npm start
```

## 🛡️ Security Tools Available

### 1. **Search Security Threats**
```javascript
{
  "name": "search_security_threats",
  "arguments": {
    "query": "APT29 latest campaign",
    "timeframe": "7d"
  }
}
```

### 2. **Analyze Threat Indicators**
```javascript
{
  "name": "analyze_threat_indicators", 
  "arguments": {
    "indicators": ["192.168.1.100", "evil.com"],
    "analysis_depth": "detailed"
  }
}
```

### 3. **Monitor Security Feeds**
```javascript
{
  "name": "monitor_security_feeds",
  "arguments": {
    "keywords": ["ransomware", "zero-day"],
    "feed_types": ["news", "threat_intel"]
  }
}
```

### 4. **Research Vulnerabilities**
```javascript
{
  "name": "research_vulnerabilities",
  "arguments": {
    "cve_ids": ["CVE-2024-1234"],
    "severity": "critical"
  }
}
```

### 5. **Scan Web Security**
```javascript
{
  "name": "scan_web_security",
  "arguments": {
    "urls": ["https://example.com"],
    "scan_types": ["headers", "ssl"]
  }
}
```

## 🔗 Claude Desktop Integration

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "brightdata-security": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "/path/to/Bright_Data_Cloud_AI_Security_Researcher"
    }
  }
}
```

## 📊 Features

### ✅ **Working Now (No API Keys Required)**
- Complete MCP server implementation
- 5 cybersecurity research tools
- Mock threat intelligence with realistic data
- Full protocol compliance

### 🚀 **With Bright Data API**
- Real-time web scraping
- Live security feed monitoring  
- Actual threat intelligence gathering
- Unblocked access to security sources

## 🎯 Use Cases

### For Security Professionals
- Threat hunting and research
- Incident response investigation  
- Vulnerability management
- Security news monitoring

### For Researchers
- Academic cybersecurity research
- Trend analysis and reporting
- IoC validation and enrichment
- Automated intelligence gathering

### For Organizations
- Brand monitoring
- Threat landscape analysis
- Competitor security assessment
- Compliance reporting

## 📁 Project Structure

```
src/
├── index.ts              # Main MCP server
├── brightdata-client.ts  # Bright Data integration
└── security-researcher.ts # Security analysis logic

test.js                   # Test suite
.env.example             # Configuration template
```

## 🔒 Security & Ethics

**This tool is designed for DEFENSIVE security research only.**

### ✅ Approved Uses
- Threat intelligence gathering
- Defensive security research
- Vulnerability assessment (authorized)
- Security awareness and education

### ❌ Prohibited Uses
- Unauthorized system access
- Malicious activity
- Privacy violations
- Illegal surveillance

## 🛠️ Development

### Run in Development Mode
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Run Tests
```bash
npm test
```

## 📦 Dependencies

- **@modelcontextprotocol/sdk**: MCP protocol implementation
- **axios**: HTTP client for API requests
- **cheerio**: HTML parsing for content analysis
- **dotenv**: Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the existing documentation
2. Review the test examples
3. Open an issue on GitHub

## 🔗 Related Projects

- [Bright Data MCP](https://github.com/luminati-io/brightdata-mcp)
- [MCP ADK](https://github.com/MeirKaD/MCP_ADK)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Built with Bright Data + MCP + Cloud AI for comprehensive cybersecurity research** 🔐