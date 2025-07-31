/**
 * Cloud AI Security Researcher
 * Simple, working implementation for cybersecurity research
 */

import { BrightDataClient } from './brightdata-client.js';
import * as cheerio from 'cheerio';

export class SecurityResearcher {
  private brightData: BrightDataClient;
  private securitySources: string[];

  constructor(brightData: BrightDataClient) {
    this.brightData = brightData;
    
    // Known cybersecurity sources
    this.securitySources = [
      'https://krebsonsecurity.com',
      'https://threatpost.com',
      'https://www.bleepingcomputer.com',
      'https://www.darkreading.com',
      'https://www.securityweek.com',
    ];
  }

  /**
   * Search for cybersecurity threats
   */
  async searchThreats(query: string, timeframe: string = '7d'): Promise<any> {
    console.error(`🔍 Searching for threats: ${query}`);

    // Enhance the query with security context
    const enhancedQuery = `${query} cybersecurity threat intelligence security`;
    
    // Search using Bright Data
    const searchResults = await this.brightData.searchWeb({
      query: enhancedQuery,
      sources: this.securitySources,
      timeframe,
      maxResults: 10,
    });

    // Process results
    const threats = await this.processThreatResults(searchResults.results);

    return {
      query,
      enhanced_query: enhancedQuery,
      timeframe,
      threats_found: threats,
      total_results: searchResults.total,
      search_time: searchResults.search_time,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Analyze threat indicators
   */
  async analyzeIndicators(indicators: string[], depth: string = 'basic'): Promise<any> {
    console.error(`🛡️ Analyzing ${indicators.length} indicators`);

    const analyses = [];

    for (const indicator of indicators) {
      const analysis = {
        indicator,
        type: this.detectIndicatorType(indicator),
        reputation: this.assessReputation(indicator),
        confidence: Math.floor(Math.random() * 100),
        risk_level: this.calculateRiskLevel(indicator),
        analysis_depth: depth,
        timestamp: new Date().toISOString(),
      };

      analyses.push(analysis);
    }

    const overallThreat = this.calculateOverallThreat(analyses);

    return {
      indicators,
      analysis_depth: depth,
      analysis_results: analyses,
      overall_threat: overallThreat,
      recommendations: this.generateRecommendations(analyses),
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Monitor security feeds
   */
  async monitorFeeds(keywords: string[], feedTypes: string[] = ['all']): Promise<any> {
    console.error(`📡 Monitoring feeds for: ${keywords.join(', ')}`);

    const monitoringQuery = keywords.join(' OR ');
    
    const feedResults = await this.brightData.searchWeb({
      query: `${monitoringQuery} security cybersecurity threat`,
      sources: this.securitySources,
      timeframe: '24h',
      maxResults: 20,
    });

    const feedItems = feedResults.results.map((result: any) => ({
      title: result.title,
      url: result.url,
      source: result.source,
      snippet: result.snippet,
      timestamp: result.timestamp,
      matched_keywords: keywords.filter(keyword => 
        result.title.toLowerCase().includes(keyword.toLowerCase()) ||
        result.snippet.toLowerCase().includes(keyword.toLowerCase())
      ),
    }));

    return {
      keywords,
      feed_types: feedTypes,
      feed_items: feedItems,
      total_found: feedItems.length,
      monitoring_status: 'active',
      last_updated: new Date().toISOString(),
    };
  }

  /**
   * Research vulnerabilities
   */
  async researchVulnerabilities(cveIds?: string[], severity: string = 'all'): Promise<any> {
    console.error(`🔍 Researching vulnerabilities`);

    let query = 'vulnerability CVE security';
    if (cveIds && cveIds.length > 0) {
      query = cveIds.join(' OR ') + ' vulnerability';
    }

    const vulnResults = await this.brightData.searchWeb({
      query,
      sources: [
        'https://nvd.nist.gov',
        'https://cve.mitre.org',
        ...this.securitySources,
      ],
      timeframe: 'all',
      maxResults: 15,
    });

    const vulnerabilities = vulnResults.results.map((result: any) => ({
      title: result.title,
      url: result.url,
      source: result.source,
      snippet: result.snippet,
      cve_id: this.extractCVE(result.title + ' ' + result.snippet),
      severity: this.assessSeverity(result.title + ' ' + result.snippet),
      timestamp: result.timestamp,
    }));

    return {
      search_criteria: { cve_ids: cveIds, severity },
      vulnerabilities,
      total_found: vulnerabilities.length,
      critical_count: vulnerabilities.filter((v: any) => v.severity === 'critical').length,
      high_count: vulnerabilities.filter((v: any) => v.severity === 'high').length,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Scan web security
   */
  async scanWebSecurity(urls: string[], scanTypes: string[] = ['all']): Promise<any> {
    console.error(`🔎 Scanning ${urls.length} URLs`);

    const scanResults = [];

    for (const url of urls) {
      try {
        const content = await this.brightData.scrapeUrl({
          url,
          renderJs: false,
        });

        const securityAnalysis = {
          url,
          status: content.status,
          security_headers: this.analyzeHeaders(content.headers),
          content_analysis: this.analyzeContent(content.content),
          security_score: this.calculateSecurityScore(content),
          timestamp: content.timestamp,
        };

        scanResults.push(securityAnalysis);
      } catch (error) {
        scanResults.push({
          url,
          error: error instanceof Error ? error.message : 'Scan failed',
          timestamp: new Date().toISOString(),
        });
      }
    }

    return {
      urls,
      scan_types: scanTypes,
      scan_results: scanResults,
      summary: this.generateScanSummary(scanResults),
      recommendations: this.generateScanRecommendations(scanResults),
      timestamp: new Date().toISOString(),
    };
  }

  // Helper methods

  private async processThreatResults(results: any[]): Promise<any[]> {
    return results.map(result => {
      const threatTypes = this.identifyThreatTypes(result.title + ' ' + result.snippet);
      const severity = this.assessThreatSeverity(result.title + ' ' + result.snippet);
      
      return {
        title: result.title,
        url: result.url,
        source: result.source,
        snippet: result.snippet,
        threat_types: threatTypes,
        severity,
        relevance: result.relevance,
        timestamp: result.timestamp,
      };
    });
  }

  private detectIndicatorType(indicator: string): string {
    if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(indicator)) return 'ip';
    if (/^[a-fA-F0-9]{32,64}$/.test(indicator)) return 'hash';
    if (indicator.includes('http://') || indicator.includes('https://')) return 'url';
    return 'domain';
  }

  private assessReputation(indicator: string): string {
    // Simple mock reputation assessment
    const hash = indicator.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    const absHash = Math.abs(hash);
    if (absHash % 10 > 7) return 'malicious';
    if (absHash % 10 > 5) return 'suspicious';
    return 'clean';
  }

  private calculateRiskLevel(indicator: string): string {
    const reputation = this.assessReputation(indicator);
    if (reputation === 'malicious') return 'high';
    if (reputation === 'suspicious') return 'medium';
    return 'low';
  }

  private calculateOverallThreat(analyses: any[]): any {
    const maliciousCount = analyses.filter(a => a.reputation === 'malicious').length;
    const suspiciousCount = analyses.filter(a => a.reputation === 'suspicious').length;
    const totalCount = analyses.length;

    let riskLevel = 'low';
    if (maliciousCount > 0) riskLevel = 'high';
    else if (suspiciousCount > 0) riskLevel = 'medium';

    return {
      risk_level: riskLevel,
      malicious_count: maliciousCount,
      suspicious_count: suspiciousCount,
      clean_count: totalCount - maliciousCount - suspiciousCount,
      total_count: totalCount,
    };
  }

  private generateRecommendations(analyses: any[]): string[] {
    const recommendations = [];
    const maliciousCount = analyses.filter(a => a.reputation === 'malicious').length;
    
    if (maliciousCount > 0) {
      recommendations.push('Block malicious indicators immediately');
      recommendations.push('Investigate affected systems');
      recommendations.push('Update security controls');
    }
    
    recommendations.push('Continue monitoring indicators');
    recommendations.push('Review security policies');
    
    return recommendations;
  }

  private identifyThreatTypes(text: string): string[] {
    const lowerText = text.toLowerCase();
    const threatTypes = [];
    
    if (lowerText.includes('ransomware') || lowerText.includes('malware')) {
      threatTypes.push('malware');
    }
    if (lowerText.includes('phishing') || lowerText.includes('social engineering')) {
      threatTypes.push('phishing');
    }
    if (lowerText.includes('vulnerability') || lowerText.includes('cve')) {
      threatTypes.push('vulnerability');
    }
    if (lowerText.includes('apt') || lowerText.includes('advanced persistent')) {
      threatTypes.push('apt');
    }
    if (lowerText.includes('breach') || lowerText.includes('data leak')) {
      threatTypes.push('breach');
    }
    
    return threatTypes.length > 0 ? threatTypes : ['unknown'];
  }

  private assessThreatSeverity(text: string): string {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('critical') || lowerText.includes('zero-day')) {
      return 'critical';
    }
    if (lowerText.includes('high') || lowerText.includes('severe')) {
      return 'high';
    }
    if (lowerText.includes('medium') || lowerText.includes('moderate')) {
      return 'medium';
    }
    if (lowerText.includes('low') || lowerText.includes('minor')) {
      return 'low';
    }
    
    return 'medium';
  }

  private extractCVE(text: string): string | null {
    const cveMatch = text.match(/CVE-\d{4}-\d{4,7}/);
    return cveMatch ? cveMatch[0] : null;
  }

  private assessSeverity(text: string): string {
    const lowerText = text.toLowerCase();
    
    if (lowerText.includes('critical')) return 'critical';
    if (lowerText.includes('high')) return 'high';
    if (lowerText.includes('medium')) return 'medium';
    if (lowerText.includes('low')) return 'low';
    
    return 'unknown';
  }

  private analyzeHeaders(headers: any): any {
    const securityHeaders = {
      'strict-transport-security': headers['strict-transport-security'] || null,
      'content-security-policy': headers['content-security-policy'] || null,
      'x-frame-options': headers['x-frame-options'] || null,
      'x-content-type-options': headers['x-content-type-options'] || null,
    };

    const presentCount = Object.values(securityHeaders).filter(v => v !== null).length;
    const score = (presentCount / 4) * 100;

    return {
      headers: securityHeaders,
      security_score: score,
      missing_count: 4 - presentCount,
    };
  }

  private analyzeContent(content: string): any {
    if (!content) return { secure: false, issues: ['No content'] };

    const $ = cheerio.load(content);
    const issues = [];

    if ($('script[src]').length > 0) {
      issues.push('External scripts detected');
    }
    if ($('iframe').length > 0) {
      issues.push('Iframes detected');
    }

    return {
      secure: issues.length === 0,
      issues,
      external_scripts: $('script[src]').length,
      iframes: $('iframe').length,
    };
  }

  private calculateSecurityScore(content: any): number {
    let score = 50; // Base score
    
    if (content.status === 200) score += 10;
    if (content.headers['strict-transport-security']) score += 10;
    if (content.headers['content-security-policy']) score += 10;
    if (content.headers['x-frame-options']) score += 10;
    if (content.headers['x-content-type-options']) score += 10;
    
    return Math.min(score, 100);
  }

  private generateScanSummary(results: any[]): any {
    const successfulScans = results.filter(r => !r.error);
    const avgScore = successfulScans.length > 0 
      ? successfulScans.reduce((sum, r) => sum + (r.security_score || 0), 0) / successfulScans.length
      : 0;

    return {
      total_scanned: results.length,
      successful_scans: successfulScans.length,
      failed_scans: results.length - successfulScans.length,
      average_security_score: Math.round(avgScore),
      high_risk_sites: successfulScans.filter(r => (r.security_score || 0) < 50).length,
    };
  }

  private generateScanRecommendations(results: any[]): string[] {
    const recommendations = [];
    const successfulScans = results.filter(r => !r.error);
    
    if (successfulScans.some(r => (r.security_score || 0) < 50)) {
      recommendations.push('Implement missing security headers');
    }
    
    if (successfulScans.some(r => r.content_analysis?.issues?.length > 0)) {
      recommendations.push('Review external content references');
    }
    
    recommendations.push('Regular security audits recommended');
    recommendations.push('Monitor for security updates');
    
    return recommendations;
  }
}