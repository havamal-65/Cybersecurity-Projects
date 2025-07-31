/**
 * Bright Data Client for MCP Server
 * Based on: github.com/luminati-io/brightdata-mcp
 */
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
export declare class BrightDataClient {
    private config;
    private httpClient;
    private isConfigured;
    constructor(config: BrightDataConfig);
    /**
     * Search the web for security-related content
     */
    searchWeb(options: SearchOptions): Promise<any>;
    /**
     * Scrape a specific URL
     */
    scrapeUrl(options: ScrapingOptions): Promise<any>;
    /**
     * Get multiple URLs in parallel
     */
    scrapeMultiple(urls: string[], options?: Partial<ScrapingOptions>): Promise<any[]>;
    /**
     * Monitor URLs for changes
     */
    monitorUrls(urls: string[], interval?: number): Promise<any>;
    private getMockSearchResults;
    private getMockScrapingResult;
    private processSearchResults;
    private extractDomain;
    /**
     * Check if the client is properly configured
     */
    isReady(): boolean;
    /**
     * Get configuration status
     */
    getStatus(): any;
}
export {};
