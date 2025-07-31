#!/usr/bin/env node

const { spawn } = require('child_process');

console.log('🚀 BRIGHT DATA SECURITY MCP DEMO\n');

const server = spawn('node', ['dist/index.js'], { 
  stdio: ['pipe', 'pipe', 'pipe'],
  env: { ...process.env, NODE_ENV: 'demo' }
});

let messageId = 1;

function sendMessage(message) {
  server.stdin.write(JSON.stringify(message) + '\n');
}

// Initialize
setTimeout(() => {
  console.log('🔧 Initializing MCP connection...');
  sendMessage({
    jsonrpc: "2.0",
    id: messageId++,
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "demo-client", version: "1.0.0" }
    }
  });
}, 100);

// Demo 1: Search for threats
setTimeout(() => {
  console.log('🔍 DEMO 1: Searching for recent ransomware threats...');
  sendMessage({
    jsonrpc: "2.0",
    id: messageId++,
    method: "tools/call",
    params: {
      name: "search_security_threats",
      arguments: {
        query: "ransomware attack 2024",
        timeframe: "7d"
      }
    }
  });
}, 500);

// Demo 2: Analyze threat indicators
setTimeout(() => {
  console.log('🛡️ DEMO 2: Analyzing suspicious indicators...');
  sendMessage({
    jsonrpc: "2.0",
    id: messageId++,
    method: "tools/call",
    params: {
      name: "analyze_threat_indicators",
      arguments: {
        indicators: ["192.168.1.100", "malicious-site.com", "d41d8cd98f00b204e9800998ecf8427e"],
        analysis_depth: "detailed"
      }
    }
  });
}, 1000);

// Demo 3: Monitor security feeds
setTimeout(() => {
  console.log('📡 DEMO 3: Monitoring security feeds...');
  sendMessage({
    jsonrpc: "2.0",
    id: messageId++,
    method: "tools/call",
    params: {
      name: "monitor_security_feeds",
      arguments: {
        keywords: ["zero-day", "vulnerability", "breach"],
        feed_types: ["news", "threat_intel"]
      }
    }
  });
}, 1500);

// Handle responses
server.stdout.on('data', (data) => {
  const lines = data.toString().split('\n').filter(line => line.trim());
  
  lines.forEach(line => {
    try {
      const response = JSON.parse(line);
      if (response.result && response.result.content) {
        const content = JSON.parse(response.result.content[0].text);
        
        if (content.threats_found) {
          console.log('\n✅ THREAT SEARCH RESULTS:');
          console.log(`   Query: "${content.query}"`);
          console.log(`   Timeframe: ${content.timeframe}`);
          console.log(`   Threats Found: ${content.threats_found.length}`);
          content.threats_found.slice(0, 2).forEach((threat, i) => {
            console.log(`   ${i+1}. ${threat.title}`);
            console.log(`      Severity: ${threat.severity}`);
            console.log(`      Types: ${threat.threat_types.join(', ')}`);
          });
        }
        
        if (content.analysis_results) {
          console.log('\n✅ INDICATOR ANALYSIS RESULTS:');
          console.log(`   Indicators Analyzed: ${content.analysis_results.length}`);
          console.log(`   Overall Risk: ${content.overall_threat.risk_level.toUpperCase()}`);
          content.analysis_results.forEach((analysis, i) => {
            console.log(`   ${i+1}. ${analysis.indicator} (${analysis.type})`);
            console.log(`      Reputation: ${analysis.reputation}`);
            console.log(`      Risk Level: ${analysis.risk_level}`);
          });
        }
        
        if (content.feed_items) {
          console.log('\n✅ SECURITY FEED MONITORING:');
          console.log(`   Keywords: ${content.keywords.join(', ')}`);
          console.log(`   Feed Items Found: ${content.feed_items.length}`);
          content.feed_items.slice(0, 2).forEach((item, i) => {
            console.log(`   ${i+1}. ${item.title}`);
            console.log(`      Source: ${item.source}`);
            console.log(`      Matched: ${item.matched_keywords.join(', ')}`);
          });
        }
      }
    } catch (e) {
      // Ignore non-JSON lines
    }
  });
});

server.stderr.on('data', (data) => {
  const message = data.toString();
  if (message.includes('🚀') || message.includes('🔍') || message.includes('🛡️') || message.includes('📡')) {
    console.log('📝', message.trim());
  }
});

// Cleanup
setTimeout(() => {
  console.log('\n🎉 Demo completed successfully!');
  console.log('\n📋 CYBERSECURITY TOOLS DEMONSTRATED:');
  console.log('✅ Threat Intelligence Search');
  console.log('✅ Indicator Reputation Analysis');  
  console.log('✅ Security Feed Monitoring');
  console.log('\n🔧 Ready for integration with Claude Desktop!');
  
  server.kill();
  process.exit(0);
}, 4000);