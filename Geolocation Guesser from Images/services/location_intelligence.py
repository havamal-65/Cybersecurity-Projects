"""
Location Intelligence Service for OSINT Geolocation Analysis

This service processes comprehensive scene descriptions and extracts actionable
location intelligence by correlating multiple clues and using geocoding APIs.
"""

import re
import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import time


@dataclass
class LocationClue:
    """Structure for individual location clues"""
    clue_type: str  # 'street_name', 'business_name', 'block_number', 'landmark', etc.
    text: str
    confidence: float
    context: str = ""
    source: str = ""


@dataclass
class LocationCandidate:
    """Structure for potential location matches"""
    latitude: float
    longitude: float
    confidence: float
    address: str
    city: str
    state: str
    country: str
    matched_clues: List[LocationClue]
    source: str
    accuracy_meters: Optional[int] = None


class LocationIntelligenceProcessor:
    """
    Processes comprehensive scene descriptions to extract and correlate location intelligence
    """
    
    def __init__(self):
        self.geocoding_cache = {}
        self.street_patterns = [
            r'\b(\d+)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Place|Pl|Way|Court|Ct)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln|Place|Pl|Way|Court|Ct)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'  # Cross streets
        ]
        self.business_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Restaurant|Cafe|Pizza|Deli|Market|Shop|Store|Bar|Grill|Bistro|Coffee|Bakery)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(Bank|Hospital|School|University|Library|Hotel|Theater|Mall)\b'
        ]
        
    def process_scene_analysis(self, scene_data: Dict[str, Any]) -> List[LocationCandidate]:
        """
        Process comprehensive scene analysis to determine locations
        
        Args:
            scene_data: Scene analysis data from MiniCPM-V
            
        Returns:
            List of location candidates with confidence scores
        """
        try:
            # Extract location clues from all sources
            location_clues = self._extract_location_clues(scene_data)
            
            if not location_clues:
                return []
            
            # Group and correlate clues
            correlated_clues = self._correlate_clues(location_clues)
            
            # Generate location candidates using geocoding
            candidates = []
            for clue_group in correlated_clues:
                search_candidates = self._generate_search_queries(clue_group)
                for query in search_candidates:
                    geocoded_results = self._geocode_query(query)
                    for result in geocoded_results:
                        candidate = LocationCandidate(
                            latitude=result['lat'],
                            longitude=result['lon'],
                            confidence=self._calculate_candidate_confidence(result, clue_group),
                            address=result.get('display_name', ''),
                            city=result.get('city', ''),
                            state=result.get('state', ''),
                            country=result.get('country', ''),
                            matched_clues=clue_group,
                            source='geocoding_correlation',
                            accuracy_meters=result.get('accuracy', None)
                        )
                        candidates.append(candidate)
            
            # Sort by confidence and return top candidates
            candidates.sort(key=lambda x: x.confidence, reverse=True)
            return candidates[:5]  # Return top 5 candidates
            
        except Exception as e:
            print(f"Location intelligence processing error: {e}")
            return []
    
    def _extract_location_clues(self, scene_data: Dict[str, Any]) -> List[LocationClue]:
        """Extract structured location clues from scene analysis"""
        clues = []
        
        # Extract from different sections of the scene analysis
        sources = {
            'signage_and_text': scene_data.get('signage_and_text', []),
            'landmarks_and_buildings': scene_data.get('landmarks_and_buildings', []),
            'infrastructure': scene_data.get('infrastructure', []),
            'scene_overview': [scene_data.get('scene_overview', '')],
            'detailed_analysis': [scene_data.get('detailed_analysis', '')]
        }
        
        for source, texts in sources.items():
            if isinstance(texts, str):
                texts = [texts]
            
            for text in texts:
                if not text:
                    continue
                    
                # Extract street names and addresses
                clues.extend(self._extract_street_clues(text, source))
                
                # Extract business names
                clues.extend(self._extract_business_clues(text, source))
                
                # Extract block numbers and address components
                clues.extend(self._extract_address_clues(text, source))
                
                # Extract landmarks and POIs
                clues.extend(self._extract_landmark_clues(text, source))
        
        return clues
    
    def _extract_street_clues(self, text: str, source: str) -> List[LocationClue]:
        """Extract street names and cross streets"""
        clues = []
        
        for pattern in self.street_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if 'and' in pattern:  # Cross streets
                    street1, street2 = match.groups()
                    clues.append(LocationClue(
                        clue_type='cross_streets',
                        text=f"{street1} and {street2}",
                        confidence=0.9,
                        context=match.group(0),
                        source=source
                    ))
                elif match.group(1).isdigit():  # Street with number
                    number, street_name, street_type = match.groups()
                    clues.append(LocationClue(
                        clue_type='street_address',
                        text=f"{number} {street_name} {street_type}",
                        confidence=0.95,
                        context=match.group(0),
                        source=source
                    ))
                    clues.append(LocationClue(
                        clue_type='block_number',
                        text=number,
                        confidence=0.8,
                        context=match.group(0),
                        source=source
                    ))
                else:  # Street name only
                    street_name, street_type = match.groups()
                    clues.append(LocationClue(
                        clue_type='street_name',
                        text=f"{street_name} {street_type}",
                        confidence=0.85,
                        context=match.group(0),
                        source=source
                    ))
        
        return clues
    
    def _extract_business_clues(self, text: str, source: str) -> List[LocationClue]:
        """Extract business names and types"""
        clues = []
        
        for pattern in self.business_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                business_name, business_type = match.groups()
                clues.append(LocationClue(
                    clue_type='business_name',
                    text=f"{business_name} {business_type}",
                    confidence=0.9,
                    context=match.group(0),
                    source=source
                ))
        
        # Look for restaurant/business specific patterns
        restaurant_indicators = ['restaurant', 'cafe', 'pizza', 'deli', 'bar', 'grill']
        words = text.lower().split()
        
        for i, word in enumerate(words):
            if word in restaurant_indicators:
                # Look for capitalized words before the indicator (likely business name)
                business_words = []
                j = i - 1
                while j >= 0 and len(business_words) < 3:
                    if words[j][0].isupper() or words[j].istitle():
                        business_words.insert(0, words[j])
                        j -= 1
                    else:
                        break
                
                if business_words:
                    business_name = ' '.join(business_words)
                    clues.append(LocationClue(
                        clue_type='business_name',
                        text=f"{business_name} {word}",
                        confidence=0.8,
                        context=f"{business_name} {word}",
                        source=source
                    ))
        
        return clues
    
    def _extract_address_clues(self, text: str, source: str) -> List[LocationClue]:
        """Extract address components like ZIP codes, building numbers"""
        clues = []
        
        # ZIP codes
        zip_pattern = r'\b(\d{5}(?:-\d{4})?)\b'
        zip_matches = re.finditer(zip_pattern, text)
        for match in zip_matches:
            clues.append(LocationClue(
                clue_type='zip_code',
                text=match.group(1),
                confidence=0.95,
                context=match.group(0),
                source=source
            ))
        
        # Building/block numbers
        building_pattern = r'\b(\d{1,5})\s+(?=\w+\s+(?:Street|St|Avenue|Ave|Road|Rd))'
        building_matches = re.finditer(building_pattern, text, re.IGNORECASE)
        for match in building_matches:
            clues.append(LocationClue(
                clue_type='building_number',
                text=match.group(1),
                confidence=0.8,
                context=match.group(0),
                source=source
            ))
        
        return clues
    
    def _extract_landmark_clues(self, text: str, source: str) -> List[LocationClue]:
        """Extract landmarks and points of interest"""
        clues = []
        
        landmark_keywords = [
            'bridge', 'park', 'square', 'plaza', 'station', 'airport', 'hospital',
            'university', 'college', 'church', 'cathedral', 'mosque', 'temple',
            'museum', 'library', 'theater', 'stadium', 'arena', 'mall', 'center'
        ]
        
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in landmark_keywords:
                # Look for proper nouns before the landmark type
                landmark_words = []
                j = i - 1
                while j >= 0 and len(landmark_words) < 3:
                    if words[j][0].isupper() or words[j].istitle():
                        landmark_words.insert(0, words[j])
                        j -= 1
                    else:
                        break
                
                if landmark_words:
                    landmark_name = ' '.join(landmark_words)
                    clues.append(LocationClue(
                        clue_type='landmark',
                        text=f"{landmark_name} {word}",
                        confidence=0.85,
                        context=f"{landmark_name} {word}",
                        source=source
                    ))
        
        return clues
    
    def _correlate_clues(self, clues: List[LocationClue]) -> List[List[LocationClue]]:
        """Group related clues for more accurate geocoding"""
        if not clues:
            return []
        
        # Start with high-confidence combinations
        high_value_groups = []
        
        # Find business + street combinations (highest value)
        business_clues = [c for c in clues if c.clue_type == 'business_name']
        street_clues = [c for c in clues if c.clue_type in ['street_name', 'street_address', 'cross_streets']]
        
        for business in business_clues:
            for street in street_clues:
                high_value_groups.append([business, street])
        
        # Add any remaining high-confidence clues
        remaining_clues = [c for c in clues if c.confidence >= 0.9 and 
                          not any(c in group for group in high_value_groups)]
        
        if remaining_clues:
            high_value_groups.extend([[clue] for clue in remaining_clues])
        
        # If no high-value combinations, group by type
        if not high_value_groups:
            clue_types = {}
            for clue in clues:
                if clue.clue_type not in clue_types:
                    clue_types[clue.clue_type] = []
                clue_types[clue.clue_type].append(clue)
            
            high_value_groups = [clues_list for clues_list in clue_types.values() if clues_list]
        
        return high_value_groups
    
    def _generate_search_queries(self, clue_group: List[LocationClue]) -> List[str]:
        """Generate search queries from correlated clues"""
        queries = []
        
        # Extract different types of clues
        business_names = [c.text for c in clue_group if c.clue_type == 'business_name']
        street_names = [c.text for c in clue_group if c.clue_type in ['street_name', 'street_address', 'cross_streets']]
        landmarks = [c.text for c in clue_group if c.clue_type == 'landmark']
        zip_codes = [c.text for c in clue_group if c.clue_type == 'zip_code']
        
        # Business + Street combinations (most precise)
        for business in business_names:
            for street in street_names:
                queries.append(f"{business}, {street}")
                if zip_codes:
                    queries.append(f"{business}, {street}, {zip_codes[0]}")
        
        # Business + Landmark combinations
        for business in business_names:
            for landmark in landmarks:
                queries.append(f"{business} near {landmark}")
        
        # Street intersections
        cross_streets = [c.text for c in clue_group if c.clue_type == 'cross_streets']
        for cross_street in cross_streets:
            queries.append(cross_street)
            if zip_codes:
                queries.append(f"{cross_street}, {zip_codes[0]}")
        
        # Individual high-confidence clues
        for clue in clue_group:
            if clue.confidence >= 0.9:
                queries.append(clue.text)
        
        return queries[:10]  # Limit to prevent API overuse
    
    def _geocode_query(self, query: str) -> List[Dict[str, Any]]:
        """Geocode a search query using Nominatim (OpenStreetMap)"""
        if query in self.geocoding_cache:
            return self.geocoding_cache[query]
        
        try:
            # Use Nominatim for free geocoding
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 3,
                'addressdetails': 1,
                'extratags': 1
            }
            
            headers = {
                'User-Agent': 'OSINT-Geolocation-Analyzer/1.0'
            }
            
            # Rate limiting for Nominatim
            time.sleep(1)
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            processed_results = []
            
            for result in results:
                processed_result = {
                    'lat': float(result.get('lat', 0)),
                    'lon': float(result.get('lon', 0)),
                    'display_name': result.get('display_name', ''),
                    'city': result.get('address', {}).get('city', ''),
                    'state': result.get('address', {}).get('state', ''),
                    'country': result.get('address', {}).get('country', ''),
                    'importance': result.get('importance', 0),
                    'accuracy': self._estimate_accuracy(result)
                }
                processed_results.append(processed_result)
            
            self.geocoding_cache[query] = processed_results
            return processed_results
            
        except Exception as e:
            print(f"Geocoding error for '{query}': {e}")
            return []
    
    def _estimate_accuracy(self, geocoding_result: Dict) -> int:
        """Estimate accuracy in meters based on result type"""
        osm_type = geocoding_result.get('osm_type', '')
        place_type = geocoding_result.get('type', '')
        
        accuracy_map = {
            'building': 10,
            'house': 20,
            'shop': 30,
            'restaurant': 30,
            'amenity': 50,
            'street': 100,
            'neighbourhood': 500,
            'suburb': 1000,
            'city': 5000,
            'state': 50000
        }
        
        return accuracy_map.get(place_type, 1000)
    
    def _calculate_candidate_confidence(self, geocoding_result: Dict, matched_clues: List[LocationClue]) -> float:
        """Calculate confidence score for a location candidate"""
        base_confidence = 0.5
        
        # Boost for multiple clues
        clue_bonus = min(0.3, len(matched_clues) * 0.1)
        
        # Boost for high-confidence clues
        clue_confidence_bonus = sum(c.confidence for c in matched_clues) / len(matched_clues) * 0.2
        
        # Boost for geocoding importance
        importance_bonus = geocoding_result.get('importance', 0) * 0.2
        
        # Boost for precise result types
        result_type = geocoding_result.get('type', '')
        precision_bonus = 0.2 if result_type in ['building', 'shop', 'restaurant'] else 0.1
        
        total_confidence = base_confidence + clue_bonus + clue_confidence_bonus + importance_bonus + precision_bonus
        return min(0.95, total_confidence)


def process_location_intelligence(scene_analysis_data: Dict[str, Any]) -> List[LocationCandidate]:
    """
    Main function to process scene analysis for location intelligence
    
    Args:
        scene_analysis_data: Comprehensive scene analysis from MiniCPM-V
        
    Returns:
        List of location candidates with coordinates and confidence scores
    """
    try:
        processor = LocationIntelligenceProcessor()
        candidates = processor.process_scene_analysis(scene_analysis_data)
        
        return candidates
        
    except Exception as e:
        print(f"Location intelligence processing failed: {e}")
        return []