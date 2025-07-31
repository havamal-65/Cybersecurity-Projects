/**
 * Bright Data Client for MCP Server
 * Based on: github.com/luminati-io/brightdata-mcp
 */

import axios, { AxiosInstance } from 'axios';

interface BrightDataConfig {
  apiToken?: string;
  zoneId?: string;
  endpoint?: string;
}

interface SearchOptions {
  query: string;
  sources?: string[];
  timeframe?: string;
  maxResults?: number;
}

interface ScrapingOptions {
  url: string;
  renderJs?: boolean;
  waitTime?: number;
  headers?: Record<string, string>;
}

export class BrightDataClient {
  private config: BrightDataConfig;
  private httpClient: AxiosInstance;
  private isConfigured: boolean;

  constructor(config: BrightDataConfig) {
    this.config = {
      endpoint: 'https://api.bright-data.com',
      ...config,
    };

    this.isConfigured = !!(this.config.apiToken && this.config.zoneId);

    this.httpClient = axios.create({
      baseURL: this.config.endpoint,
      timeout: 30000,
      headers: {
        'Authorization': `Bearer ${this.config.apiToken}`,
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Search the web for security-related content
   */
  async searchWeb(options: SearchOptions): Promise<any> {
    if (!this.isConfigured) {
      return this.getMockSearchResults(options);
    }

    try {
      const response = await this.httpClient.post('/search', {
        query: options.query,
        zone_id: this.config.zoneId,
        sources: options.sources,
        timeframe: options.timeframe,
        max_results: options.maxResults || 20,
      });

      return this.processSearchResults(response.data);
    } catch (error) {
      console.error('Bright Data search failed:', error);
      return this.getMockSearchResults(options);
    }
  }

  /**
   * Scrape a specific URL
   */
  async scrapeUrl(options: ScrapingOptions): Promise<any> {
    if (!this.isConfigured) {
      return this.getMockScrapingResult(options);
    }

    try {
      const response = await this.httpClient.post('/scrape', {
        url: options.url,
        zone_id: this.config.zoneId,
        render_js: options.renderJs || false,
        wait_time: options.waitTime || 0,
        headers: options.headers || {},
      });

      return {
        url: options.url,
        content: response.data.content,
        status: response.data.status,
        headers: response.data.headers,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Bright Data scraping failed:', error);
      return this.getMockScrapingResult(options);
    }
  }

  /**
   * Get multiple URLs in parallel
   */
  async scrapeMultiple(urls: string[], options: Partial<ScrapingOptions> = {}): Promise<any[]> {
    const promises = urls.map(url => this.scrapeUrl({ url, ...options }));
    return Promise.all(promises);
  }

  /**
   * Monitor URLs for changes
   */
  async monitorUrls(urls: string[], interval: number = 3600): Promise<any> {
    if (!this.isConfigured) {
      return {
        monitoring: true,
        urls,
        interval,
        message: 'Mock monitoring active - would check for changes every ' + interval + ' seconds',
      };
    }

    try {
      const response = await this.httpClient.post('/monitor', {
        urls,
        zone_id: this.config.zoneId,
        interval,
      });

      return response.data;
    } catch (error) {
      console.error('Bright Data monitoring failed:', error);
      return {
        monitoring: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Mock implementations for when API is not configured
  private getMockSearchResults(options: SearchOptions): any {
    return {
      query: options.query,
      results: [
        {
          title: `Security Analysis: ${options.query}`,
          url: 'https://securityresearch.example.com/analysis',
          snippet: `Comprehensive analysis of ${options.query} including threat indicators, attack patterns, and mitigation strategies.`,
          source: 'Security Research Portal',
          timestamp: new Date().toISOString(),
          relevance: 0.95,
        },
        {
          title: `Threat Intelligence: ${options.query}`,
          url: 'https://threatlabs.example.com/intel',
          snippet: `Latest threat intelligence regarding ${options.query} with IOCs, TTPs, and attribution information.`,
          source: 'Threat Intelligence Labs',
          timestamp: new Date().toISOString(),
          relevance: 0.92,
        },
        {
          title: `Security Advisory: ${options.query}`,
          url: 'https://advisories.example.com/latest',
          snippet: `Security advisory and recommendations for ${options.query} including patches and workarounds.`,
          source: 'Security Advisories',
          timestamp: new Date().toISOString(),
          relevance: 0.88,
        },
      ],
      total: 3,
      search_time: 247,
      mock_data: true,
    };
  }

  private getMockScrapingResult(options: ScrapingOptions): any {
    return {
      url: options.url,
      content: `
        <html>
          <head><title>Security Analysis</title></head>
          <body>
            <h1>Cybersecurity Research</h1>
            <p>This would be the scraped content from ${options.url}</p>
            <div class="threat-indicators">
              <h2>Threat Indicators</h2>
              <ul>
                <li>Malicious IP: 192.168.1.100</li>
                <li>Suspicious domain: evil.example.com</li>
                <li>File hash: d41d8cd98f00b204e9800998ecf8427e</li>
              </ul>
            </div>
          </body>
        </html>
      `,
      status: 200,
      headers: {
        'content-type': 'text/html',
        'server': 'nginx',
      },
      timestamp: new Date().toISOString(),
      mock_data: true,
    };
  }

  private processSearchResults(data: any): any {
    // Process and normalize search results from Bright Data
    return {
      results: data.results?.map((result: any) => ({
        title: result.title || '',
        url: result.url || '',
        snippet: result.snippet || result.description || '',
        source: result.source || this.extractDomain(result.url || ''),
        timestamp: result.timestamp || new Date().toISOString(),
        relevance: result.relevance || 0.5,
      })) || [],
      total: data.total || 0,
      search_time: data.search_time || 0,
    };
  }

  private extractDomain(url: string): string {
    try {
      return new URL(url).hostname;
    } catch {
      return 'unknown';
    }
  }

  /**
   * Check if the client is properly configured
   */
  isReady(): boolean {
    return this.isConfigured;
  }

  /**
   * Get configuration status
   */
  getStatus(): any {
    return {
      configured: this.isConfigured,
      has_api_token: !!this.config.apiToken,
      has_zone_id: !!this.config.zoneId,
      endpoint: this.config.endpoint,
    };
  }
}