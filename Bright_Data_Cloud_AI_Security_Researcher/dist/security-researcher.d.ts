/**
 * Cloud AI Security Researcher
 * Simple, working implementation for cybersecurity research
 */
import { BrightDataClient } from './brightdata-client.js';
export declare class SecurityResearcher {
    private brightData;
    private securitySources;
    constructor(brightData: BrightDataClient);
    /**
     * Search for cybersecurity threats
     */
    searchThreats(query: string, timeframe?: string): Promise<any>;
    /**
     * Analyze threat indicators
     */
    analyzeIndicators(indicators: string[], depth?: string): Promise<any>;
    /**
     * Monitor security feeds
     */
    monitorFeeds(keywords: string[], feedTypes?: string[]): Promise<any>;
    /**
     * Research vulnerabilities
     */
    researchVulnerabilities(cveIds?: string[], severity?: string): Promise<any>;
    /**
     * Scan web security
     */
    scanWebSecurity(urls: string[], scanTypes?: string[]): Promise<any>;
    private processThreatResults;
    private detectIndicatorType;
    private assessReputation;
    private calculateRiskLevel;
    private calculateOverallThreat;
    private generateRecommendations;
    private identifyThreatTypes;
    private assessThreatSeverity;
    private extractCVE;
    private assessSeverity;
    private analyzeHeaders;
    private analyzeContent;
    private calculateSecurityScore;
    private generateScanSummary;
    private generateScanRecommendations;
}
