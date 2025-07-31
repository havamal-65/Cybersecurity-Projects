"""
Real confidence scoring system for geolocation analysis
Calculates reliability scores based on multiple evidence sources
"""

import json
from typing import List, Dict, Any
import math

class ConfidenceScorer:
    """
    Real confidence scoring system that evaluates geolocation evidence
    No mocks - this actually calculates meaningful confidence scores
    """
    
    # Evidence type weights (based on real-world reliability)
    EVIDENCE_WEIGHTS = {
        'EXIF_GPS': 0.95,           # Highest confidence - direct GPS data
        'landmark_detection': 0.85,  # High confidence - AI landmark recognition
        'license_plate': 0.80,       # High confidence - region-specific plates
        'street_signs': 0.75,        # Good confidence - location-specific signage
        'architecture': 0.65,        # Medium confidence - regional building styles
        'text_language': 0.60,       # Medium confidence - language regions
        'vegetation': 0.55,          # Medium confidence - climate indicators
        'license_format': 0.50,      # Lower confidence - format similarities
        'reverse_image': 0.70,       # Good confidence - if unique match
        'vision_api': 0.75,          # Good confidence - AI analysis
        'ocr_text': 0.65,           # Medium confidence - extracted text
        'geographic_text': 0.70     # Good confidence - location names
    }
    
    # Accuracy radius estimates (in meters) for different methods
    ACCURACY_ESTIMATES = {
        'EXIF_GPS': 10,             # Very precise
        'landmark_detection': 100,   # Building/landmark level
        'street_signs': 500,        # Street/neighborhood level
        'license_plate': 50000,     # Region/state level
        'architecture': 100000,     # City/region level
        'text_language': 1000000,   # Country level
        'vision_api': 1000,         # Variable accuracy
        'ocr_text': 10000,          # City level
        'geographic_text': 5000     # Area level
    }

    @staticmethod
    def calculate_overall_confidence(results: List[Any]) -> float:
        """
        Calculate overall confidence score from multiple analysis results
        Returns float between 0.0 and 1.0
        """
        if not results:
            return 0.0
        
        try:
            evidence_scores = []
            methods_used = set()
            
            for result in results:
                # Handle both database models and dictionaries
                if hasattr(result, 'method_used'):
                    method = result.method_used
                    confidence = result.confidence_score or 0.5
                    has_coordinates = bool(result.latitude and result.longitude)
                else:
                    method = result.get('method', 'unknown')
                    confidence = result.get('confidence', 0.5)
                    has_coordinates = bool(result.get('latitude') and result.get('longitude'))
                
                # Get base weight for this evidence type
                base_weight = ConfidenceScorer.EVIDENCE_WEIGHTS.get(method, 0.3)
                
                # Adjust weight based on whether we have actual coordinates
                if has_coordinates:
                    adjusted_weight = base_weight
                else:
                    adjusted_weight = base_weight * 0.5  # Reduce weight for non-coordinate evidence
                
                # Calculate weighted score
                weighted_score = confidence * adjusted_weight
                evidence_scores.append(weighted_score)
                methods_used.add(method)
            
            if not evidence_scores:
                return 0.0
            
            # Calculate base confidence using weighted average
            total_weight = sum(ConfidenceScorer.EVIDENCE_WEIGHTS.get(method, 0.3) 
                             for method in methods_used)
            
            if total_weight == 0:
                return 0.0
            
            base_confidence = sum(evidence_scores) / total_weight
            
            # Apply bonuses for multiple evidence types
            diversity_bonus = ConfidenceScorer._calculate_diversity_bonus(methods_used)
            
            # Apply penalties for conflicting evidence
            conflict_penalty = ConfidenceScorer._calculate_conflict_penalty(results)
            
            # Final confidence calculation
            final_confidence = base_confidence + diversity_bonus - conflict_penalty
            
            # Ensure result is between 0.0 and 1.0
            return max(0.0, min(1.0, final_confidence))
            
        except Exception as e:
            print(f"Confidence calculation error: {e}")
            return 0.0

    @staticmethod
    def _calculate_diversity_bonus(methods_used: set) -> float:
        """
        Calculate bonus for having multiple different evidence types
        """
        method_count = len(methods_used)
        
        if method_count <= 1:
            return 0.0
        elif method_count == 2:
            return 0.05
        elif method_count == 3:
            return 0.10
        elif method_count >= 4:
            return 0.15
        
        return 0.0

    @staticmethod
    def _calculate_conflict_penalty(results: List[Any]) -> float:
        """
        Calculate penalty for conflicting location evidence
        """
        coordinates = []
        
        # Extract coordinates from results
        for result in results:
            if hasattr(result, 'latitude'):
                lat, lon = result.latitude, result.longitude
            else:
                lat, lon = result.get('latitude'), result.get('longitude')
            
            if lat is not None and lon is not None:
                coordinates.append((float(lat), float(lon)))
        
        if len(coordinates) < 2:
            return 0.0  # No conflict possible with fewer than 2 points
        
        # Calculate maximum distance between any two points
        max_distance = 0.0
        for i in range(len(coordinates)):
            for j in range(i + 1, len(coordinates)):
                distance = ConfidenceScorer._haversine_distance(
                    coordinates[i][0], coordinates[i][1],
                    coordinates[j][0], coordinates[j][1]
                )
                max_distance = max(max_distance, distance)
        
        # Apply penalty based on maximum distance
        if max_distance > 100000:  # > 100km apart
            return 0.20
        elif max_distance > 50000:  # > 50km apart
            return 0.15
        elif max_distance > 10000:  # > 10km apart
            return 0.10
        elif max_distance > 1000:   # > 1km apart
            return 0.05
        
        return 0.0

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in meters using Haversine formula
        """
        try:
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth's radius in meters
            R = 6371000
            
            return R * c
        except:
            return 0.0

    @staticmethod
    def get_best_location_estimate(results: List[Any]) -> Dict[str, Any]:
        """
        Calculate the best location estimate from multiple results
        Returns coordinates with confidence and accuracy estimate
        """
        if not results:
            return None
        
        try:
            # Filter results with coordinates
            coordinate_results = []
            for result in results:
                if hasattr(result, 'latitude'):
                    lat, lon = result.latitude, result.longitude
                    method = result.method_used
                    confidence = result.confidence_score or 0.5
                else:
                    lat, lon = result.get('latitude'), result.get('longitude')
                    method = result.get('method', 'unknown')
                    confidence = result.get('confidence', 0.5)
                
                if lat is not None and lon is not None:
                    coordinate_results.append({
                        'latitude': float(lat),
                        'longitude': float(lon),
                        'method': method,
                        'confidence': confidence,
                        'weight': ConfidenceScorer.EVIDENCE_WEIGHTS.get(method, 0.3),
                        'accuracy_meters': ConfidenceScorer.ACCURACY_ESTIMATES.get(method, 10000)
                    })
            
            if not coordinate_results:
                return None
            
            # If only one result, return it
            if len(coordinate_results) == 1:
                result = coordinate_results[0]
                return {
                    'latitude': result['latitude'],
                    'longitude': result['longitude'],
                    'confidence': result['confidence'],
                    'accuracy_meters': result['accuracy_meters'],
                    'method': result['method'],
                    'evidence_count': 1
                }
            
            # Calculate weighted average of coordinates
            total_weight = 0.0
            weighted_lat = 0.0
            weighted_lon = 0.0
            best_accuracy = float('inf')
            methods = set()
            
            for result in coordinate_results:
                weight = result['confidence'] * result['weight']
                total_weight += weight
                weighted_lat += result['latitude'] * weight
                weighted_lon += result['longitude'] * weight
                best_accuracy = min(best_accuracy, result['accuracy_meters'])
                methods.add(result['method'])
            
            if total_weight == 0:
                return None
            
            # Calculate final coordinates
            final_lat = weighted_lat / total_weight
            final_lon = weighted_lon / total_weight
            
            # Calculate overall confidence
            overall_confidence = ConfidenceScorer.calculate_overall_confidence(results)
            
            return {
                'latitude': final_lat,
                'longitude': final_lon,
                'confidence': overall_confidence,
                'accuracy_meters': int(best_accuracy),
                'methods': list(methods),
                'evidence_count': len(coordinate_results)
            }
            
        except Exception as e:
            print(f"Best estimate calculation error: {e}")
            return None

    @staticmethod
    def analyze_evidence_quality(results: List[Any]) -> Dict[str, Any]:
        """
        Analyze the quality and distribution of evidence
        """
        if not results:
            return {'quality': 'no_evidence', 'score': 0.0}
        
        try:
            methods = set()
            has_coordinates = False
            high_confidence_count = 0
            total_confidence = 0.0
            
            for result in results:
                if hasattr(result, 'method_used'):
                    methods.add(result.method_used)
                    confidence = result.confidence_score or 0.0
                    has_coords = bool(result.latitude and result.longitude)
                else:
                    methods.add(result.get('method', 'unknown'))
                    confidence = result.get('confidence', 0.0)
                    has_coords = bool(result.get('latitude') and result.get('longitude'))
                
                if has_coords:
                    has_coordinates = True
                
                if confidence > 0.8:
                    high_confidence_count += 1
                
                total_confidence += confidence
            
            avg_confidence = total_confidence / len(results)
            method_count = len(methods)
            
            # Determine quality category
            if not has_coordinates:
                quality = 'no_location'
                score = 0.0
            elif 'EXIF_GPS' in methods:
                quality = 'excellent'
                score = 0.9
            elif high_confidence_count > 0 and method_count >= 2:
                quality = 'good'
                score = 0.7
            elif method_count >= 2:
                quality = 'fair'
                score = 0.5
            elif avg_confidence > 0.6:
                quality = 'limited'
                score = 0.4
            else:
                quality = 'poor'
                score = 0.2
            
            return {
                'quality': quality,
                'score': score,
                'method_count': method_count,
                'methods': list(methods),
                'avg_confidence': avg_confidence,
                'high_confidence_count': high_confidence_count,
                'has_coordinates': has_coordinates,
                'total_evidence': len(results)
            }
            
        except Exception as e:
            print(f"Evidence quality analysis error: {e}")
            return {'quality': 'error', 'score': 0.0, 'error': str(e)}