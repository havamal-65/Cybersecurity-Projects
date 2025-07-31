#!/usr/bin/env node
/**
 * Bright Data MCP Server with Cloud AI Security Researcher
 * Clean, working implementation based on the original concepts
 */
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import dotenv from 'dotenv';
import { BrightDataClient } from './brightdata-client.js';
import { SecurityResearcher } from './security-researcher.js';
// Load environment variables
dotenv.config();
class BrightDataSecurityMCP {
    server;
    brightData;
    securityResearcher;
    constructor() {
        this.server = new Server({
            name: 'brightdata-security-mcp',
            version: '1.0.0',
        }, {
            capabilities: {
                tools: {},
            },
        });
        // Initialize services
        this.brightData = new BrightDataClient({
            apiToken: process.env.BRIGHT_DATA_API_TOKEN,
            zoneId: process.env.BRIGHT_DATA_ZONE_ID,
        });
        this.securityResearcher = new SecurityResearcher(this.brightData);
        this.setupToolHandlers();
    }
    setupToolHandlers() {
        // Define security research tools
        const tools = [
            {
                name: 'search_security_threats',
                description: 'Search for cybersecurity threats and intelligence using Bright Data',
                inputSchema: {
                    type: 'object',
                    properties: {
                        query: {
                            type: 'string',
                            description: 'Security threat to search for',
                        },
                        timeframe: {
                            type: 'string',
                            enum: ['24h', '7d', '30d', 'all'],
                            description: 'Time range for search results',
                        },
                    },
                    required: ['query'],
                },
            },
            {
                name: 'analyze_threat_indicators',
                description: 'Analyze IPs, domains, URLs, or hashes for malicious activity',
                inputSchema: {
                    type: 'object',
                    properties: {
                        indicators: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'List of indicators to analyze',
                        },
                        analysis_depth: {
                            type: 'string',
                            enum: ['basic', 'detailed', 'comprehensive'],
                            description: 'Depth of analysis to perform',
                        },
                    },
                    required: ['indicators'],
                },
            },
            {
                name: 'monitor_security_feeds',
                description: 'Monitor real-time security news and threat feeds',
                inputSchema: {
                    type: 'object',
                    properties: {
                        keywords: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'Keywords to monitor for',
                        },
                        feed_types: {
                            type: 'array',
                            items: {
                                type: 'string',
                                enum: ['news', 'advisories', 'threat_intel', 'all']
                            },
                            description: 'Types of feeds to monitor',
                        },
                    },
                    required: ['keywords'],
                },
            },
            {
                name: 'research_vulnerabilities',
                description: 'Research specific vulnerabilities and CVEs',
                inputSchema: {
                    type: 'object',
                    properties: {
                        cve_ids: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'CVE IDs to research',
                        },
                        severity: {
                            type: 'string',
                            enum: ['critical', 'high', 'medium', 'low', 'all'],
                            description: 'Minimum severity level',
                        },
                    },
                },
            },
            {
                name: 'scan_web_security',
                description: 'Perform security analysis of websites',
                inputSchema: {
                    type: 'object',
                    properties: {
                        urls: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'URLs to analyze for security issues',
                        },
                        scan_types: {
                            type: 'array',
                            items: {
                                type: 'string',
                                enum: ['headers', 'ssl', 'technologies', 'all']
                            },
                            description: 'Types of security scans to perform',
                        },
                    },
                    required: ['urls'],
                },
            },
        ];
        // Register tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return { tools };
        });
        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;
            try {
                let result;
                switch (name) {
                    case 'search_security_threats':
                        result = await this.securityResearcher.searchThreats(args?.query || '', args?.timeframe || '7d');
                        break;
                    case 'analyze_threat_indicators':
                        result = await this.securityResearcher.analyzeIndicators(args?.indicators || [], args?.analysis_depth || 'basic');
                        break;
                    case 'monitor_security_feeds':
                        result = await this.securityResearcher.monitorFeeds(args?.keywords || [], args?.feed_types || ['all']);
                        break;
                    case 'research_vulnerabilities':
                        result = await this.securityResearcher.researchVulnerabilities(args?.cve_ids, args?.severity || 'all');
                        break;
                    case 'scan_web_security':
                        result = await this.securityResearcher.scanWebSecurity(args?.urls || [], args?.scan_types || ['all']);
                        break;
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify(result, null, 2),
                        },
                    ],
                };
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Unknown error';
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Error: ${errorMessage}`,
                        },
                    ],
                };
            }
        });
    }
    async start() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('🚀 Bright Data Security MCP Server started');
    }
}
// Start the server
const server = new BrightDataSecurityMCP();
server.start().catch((error) => {
    console.error('Failed to start server:', error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map