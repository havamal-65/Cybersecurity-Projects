"""
Reverse Image Search Service for OSINT Geolocation Analysis

This service provides reverse image search capabilities to find matching or similar images
online that could provide location context. Uses multiple search engines and APIs.
"""

import requests
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import base64


class ReverseImageSearcher:
    """
    Handles reverse image search operations across multiple platforms
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_all_engines(self, image_path: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Perform reverse image search across multiple engines
        
        Args:
            image_path: Path to the image file
            max_results: Maximum number of results per engine
            
        Returns:
            Dictionary containing search results from all engines
        """
        results = {
            'success': True,
            'image_hash': self._calculate_image_hash(image_path),
            'search_engines': {},
            'consolidated_results': [],
            'location_indicators': [],
            'confidence_score': 0.0,
            'method': 'reverse_image_search'
        }
        
        try:
            # TinEye search (free API available)
            tineye_results = self._search_tineye(image_path, max_results)
            if tineye_results:
                results['search_engines']['tineye'] = tineye_results
                
            # Google Images search (via web scraping - be careful with rate limits)
            google_results = self._search_google_images(image_path, max_results)
            if google_results:
                results['search_engines']['google'] = google_results
                
            # Yandex Images search
            yandex_results = self._search_yandex_images(image_path, max_results)
            if yandex_results:
                results['search_engines']['yandex'] = yandex_results
                
            # Consolidate and analyze results
            results['consolidated_results'] = self._consolidate_results(results['search_engines'])
            results['location_indicators'] = self._extract_location_indicators(results['consolidated_results'])
            results['confidence_score'] = self._calculate_confidence(results)
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            
        return results
    
    def _calculate_image_hash(self, image_path: str) -> str:
        """Calculate SHA256 hash of the image"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _search_tineye(self, image_path: str, max_results: int) -> Optional[Dict]:
        """
        Search using TinEye reverse image search
        Note: This is a placeholder - TinEye requires API key for automated access
        """
        try:
            # TinEye API would go here
            # For now, return simulated structure
            return {
                'engine': 'tineye',
                'total_matches': 0,
                'matches': [],
                'search_time': time.time(),
                'note': 'TinEye API integration required'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _search_google_images(self, image_path: str, max_results: int) -> Optional[Dict]:
        """
        Search using Google Images reverse search
        Note: This uses web scraping which may be rate-limited
        """
        try:
            # Encode image for upload
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                
            # Google Images reverse search endpoint
            search_url = "https://www.google.com/searchbyimage/upload"
            
            files = {'encoded_image': img_data}
            data = {'image_content': ''}
            
            # Note: This is a simplified approach and may not work reliably
            # Production systems should use Google Vision API or Custom Search API
            
            return {
                'engine': 'google_images',
                'total_matches': 0,
                'matches': [],
                'search_time': time.time(),
                'note': 'Google Vision API integration recommended'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _search_yandex_images(self, image_path: str, max_results: int) -> Optional[Dict]:
        """
        Search using Yandex Images reverse search
        """
        try:
            # Yandex Images has a reverse search API
            # This is a placeholder for the actual implementation
            
            return {
                'engine': 'yandex_images',
                'total_matches': 0,
                'matches': [],
                'search_time': time.time(),
                'note': 'Yandex Images API integration required'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _consolidate_results(self, search_engines: Dict) -> List[Dict]:
        """
        Consolidate results from multiple search engines
        """
        consolidated = []
        
        for engine, results in search_engines.items():
            if results and 'matches' in results:
                for match in results['matches']:
                    consolidated.append({
                        'source_engine': engine,
                        'url': match.get('url', ''),
                        'title': match.get('title', ''),
                        'description': match.get('description', ''),
                        'domain': match.get('domain', ''),
                        'similarity_score': match.get('similarity', 0.0),
                        'date_found': match.get('date', ''),
                        'location_hints': self._extract_location_from_text(
                            f"{match.get('title', '')} {match.get('description', '')}"
                        )
                    })
        
        # Sort by similarity score
        consolidated.sort(key=lambda x: x['similarity_score'], reverse=True)
        return consolidated
    
    def _extract_location_indicators(self, consolidated_results: List[Dict]) -> List[Dict]:
        """
        Extract potential location indicators from search results
        """
        indicators = []
        
        for result in consolidated_results:
            # Extract from URL domains
            domain_hints = self._analyze_domain_for_location(result['domain'])
            if domain_hints:
                indicators.extend(domain_hints)
            
            # Extract from titles and descriptions
            text_hints = result.get('location_hints', [])
            if text_hints:
                indicators.extend(text_hints)
        
        # Deduplicate and score indicators
        unique_indicators = self._deduplicate_indicators(indicators)
        return unique_indicators
    
    def _extract_location_from_text(self, text: str) -> List[Dict]:
        """
        Extract location information from text using simple patterns
        """
        import re
        
        indicators = []
        
        # Common location patterns
        patterns = {
            'city_state': r'\b([A-Z][a-z]+),\s*([A-Z]{2})\b',
            'country': r'\b(United States|USA|UK|United Kingdom|Canada|Australia|Germany|France|Japan|China|India)\b',
            'city': r'\b(New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose)\b',
            'coordinates': r'\b(-?\d{1,3}\.\d+),\s*(-?\d{1,3}\.\d+)\b'
        }
        
        for pattern_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                indicators.append({
                    'type': pattern_type,
                    'text': match.group(),
                    'confidence': 0.7,
                    'source': 'text_extraction'
                })
        
        return indicators
    
    def _analyze_domain_for_location(self, domain: str) -> List[Dict]:
        """
        Analyze domain for geographic indicators
        """
        indicators = []
        
        # Country code top-level domains
        ccTLDs = {
            '.uk': 'United Kingdom',
            '.ca': 'Canada',
            '.au': 'Australia',
            '.de': 'Germany',
            '.fr': 'France',
            '.jp': 'Japan',
            '.cn': 'China',
            '.in': 'India',
            '.br': 'Brazil',
            '.mx': 'Mexico'
        }
        
        for tld, country in ccTLDs.items():
            if domain.endswith(tld):
                indicators.append({
                    'type': 'country_domain',
                    'text': country,
                    'confidence': 0.8,
                    'source': 'domain_analysis'
                })
        
        # Geographic subdomains
        geo_subdomains = ['local', 'city', 'regional', 'news']
        for subdomain in geo_subdomains:
            if subdomain in domain:
                indicators.append({
                    'type': 'geographic_subdomain',
                    'text': subdomain,
                    'confidence': 0.6,
                    'source': 'subdomain_analysis'
                })
        
        return indicators
    
    def _deduplicate_indicators(self, indicators: List[Dict]) -> List[Dict]:
        """
        Remove duplicate location indicators and consolidate scores
        """
        seen = {}
        
        for indicator in indicators:
            key = f"{indicator['type']}_{indicator['text'].lower()}"
            if key in seen:
                # Increase confidence for repeated indicators
                seen[key]['confidence'] = min(0.95, seen[key]['confidence'] + 0.1)
                seen[key]['frequency'] = seen[key].get('frequency', 1) + 1
            else:
                indicator['frequency'] = 1
                seen[key] = indicator
        
        return list(seen.values())
    
    def _calculate_confidence(self, results: Dict) -> float:
        """
        Calculate overall confidence score for reverse image search results
        """
        if not results.get('consolidated_results'):
            return 0.0
        
        # Base confidence on number of matches and their similarity scores
        total_results = len(results['consolidated_results'])
        avg_similarity = sum(r.get('similarity_score', 0) for r in results['consolidated_results']) / total_results
        
        # Location indicators boost confidence
        location_indicators = len(results.get('location_indicators', []))
        
        # Calculate weighted confidence
        confidence = (avg_similarity * 0.6 + 
                     min(total_results / 10, 1.0) * 0.3 + 
                     min(location_indicators / 5, 1.0) * 0.1)
        
        return min(confidence, 0.95)


def perform_reverse_image_search(image_path: str) -> Dict[str, Any]:
    """
    Main function to perform reverse image search analysis
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing search results and location indicators
    """
    try:
        searcher = ReverseImageSearcher()
        results = searcher.search_all_engines(image_path)
        
        return {
            'success': True,
            'method': 'reverse_image_search',
            'results': results,
            'analysis_summary': {
                'total_engines_used': len(results.get('search_engines', {})),
                'total_matches_found': len(results.get('consolidated_results', [])),
                'location_indicators_found': len(results.get('location_indicators', [])),
                'confidence_score': results.get('confidence_score', 0.0)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'method': 'reverse_image_search',
            'error': str(e)
        }