"""
OCR service optimized for natural scene text in OSINT geolocation
Uses EasyOCR and Keras-OCR which are much better for street signs, license plates, etc.
Tesseract kept as fallback for document-style text
"""

import cv2
import numpy as np
from PIL import Image
import os
import json
# Regex removed - using structured JSON from MiniCPM-V instead

# Primary OCR: Ollama MiniCPM-V (comprehensive OSINT analysis)
try:
    import ollama
    import base64
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Disable problematic OCR engines to avoid PyTorch conflicts
EASYOCR_AVAILABLE = False
KERAS_OCR_AVAILABLE = False

# Fallback: Tesseract (mainly for documents)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def get_default_minicpm_prompt():
    """
    Get the default prompt for MiniCPM-V location intelligence
    """
    return """You are an expert OSINT analyst. Analyze this image and extract ALL location intelligence. Return ONLY valid JSON.

{
  "location_analysis": {
    "business_names": ["exact text from business signs"],
    "street_names": ["exact street names from signs"],
    "street_addresses": ["full addresses like '123 Main St'"],
    "cross_streets": ["intersections like 'Main St and Oak Ave'"],
    "landmarks": ["notable buildings, monuments, distinctive features"],
    "license_plates": ["visible license plate text"],
    "geographic_text": ["city names, state names, country indicators"],
    "postal_codes": ["zip codes, postal codes"]
  },
  "scene_description": "Complete description of what you see",
  "coordinates_estimate": {
    "confidence": "high/medium/low",
    "reasoning": "why you think this location",
    "suggested_search": "best search query for finding exact location"
  }
}

EXTRACT EVERY PIECE OF TEXT YOU CAN SEE. Read all signs, street names, business names, addresses, license plates. Be precise and thorough."""

def analyze_image_with_vision(image_path, preprocess=True, languages=['en'], custom_prompt=None):
    """
    Analyze image using comprehensive AI vision analysis with MiniCPM-V
    Provides complete scene description including text, objects, and location intelligence
    
    Args:
        image_path: Path to image file
        preprocess: Whether to preprocess image (legacy parameter, kept for compatibility)
        languages: Languages for analysis (legacy parameter, kept for compatibility)
        custom_prompt: Optional custom prompt for MiniCPM-V analysis
    
    Returns:
        Dictionary with comprehensive visual analysis and location intelligence
    """
    try:
        if not os.path.exists(image_path):
            return {'error': 'Image file not found'}
        
        # MiniCPM-V comprehensive vision analysis (primary and only method)
        if OLLAMA_AVAILABLE:
            print("DEBUG: Starting MiniCPM-V comprehensive vision analysis...")
            result = extract_with_ollama_minicpm(image_path, custom_prompt)
            print(f"DEBUG: MiniCPM-V analysis complete - Success: {result.get('success', False)}")
            if not result.get('success'):
                print(f"DEBUG: MiniCPM-V error: {result.get('error', 'Unknown error')}")
            return result
        else:
            return {
                'success': False,
                'error': 'MiniCPM-V not available - install Ollama and run: ollama pull minicpm-v',
                'method': 'none',
                'message': 'Comprehensive vision analysis requires MiniCPM-V model'
            }
        
    except Exception as e:
        return {'error': f'OCR extraction failed: {str(e)}'}

def extract_with_ollama_minicpm(image_path, custom_prompt=None):
    """
    Extract comprehensive OSINT intelligence using Ollama MiniCPM-V
    Args:
        image_path: Path to the image file
        custom_prompt: Optional custom prompt to use instead of default
    """
    try:
        # Check if MiniCPM-V model is available
        models = ollama.list()
        available_models = [model.model for model in models.models]
        
        if 'minicpm-v:latest' not in available_models:
            return {'error': 'MiniCPM-V model not found in Ollama. Run: ollama pull minicpm-v'}
        
        # Encode image to base64
        with open(image_path, 'rb') as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Use custom prompt if provided, otherwise use default comprehensive scene analysis prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = get_default_minicpm_prompt()
        
        # Send request to Ollama with timeout handling
        print("DEBUG: Sending request to Ollama MiniCPM-V (this may take 30-60 seconds)...")
        print(f"DEBUG: Using prompt length: {len(prompt)} characters")
        try:
            response = ollama.generate(
                model='minicpm-v',
                prompt=prompt,
                images=[image_base64],
                stream=False
            )
            print("DEBUG: Ollama analysis completed successfully")
            print(f"DEBUG: Response length: {len(response.get('response', ''))} characters")
        except Exception as ollama_error:
            print(f"Ollama request failed: {ollama_error}")
            # Fall back to a basic response to prevent complete failure
            return {
                'success': True,
                'method': 'ollama_minicpm_fallback',
                'full_text': f'Ollama analysis failed: {str(ollama_error)}. Image processing attempted but model may be loading.',
                'text_blocks': [],
                'geographic_indicators': [],
                'detected_languages': ['unknown'],
                'total_blocks': 0,
                'average_confidence': 0,
                'intelligence_categories': {}
            }
        
        # Extract response text
        analysis_text = response['response']
        
        # Check if response is HTML instead of JSON
        if analysis_text.strip().lower().startswith('<!doctype') or analysis_text.strip().lower().startswith('<html'):
            print("WARNING: MiniCPM-V returned HTML instead of JSON. Using fallback analysis.")
            return {
                'success': True,
                'method': 'ollama_minicpm_fallback_html',
                'full_text': 'MiniCPM-V returned HTML instead of JSON. This may indicate the model needs different prompting or is overloaded.',
                'text_blocks': [],
                'geographic_indicators': [],
                'detected_languages': ['unknown'],
                'total_blocks': 0,
                'average_confidence': 0,
                'intelligence_categories': {},
                'error_type': 'html_response'
            }
        
        # Try to parse JSON response from MiniCPM-V
        try:
            # Extract JSON from response (may have extra text)
            json_start = analysis_text.find('{')
            if json_start != -1:
                # Find the end of the JSON object
                brace_count = 0
                json_end = json_start
                for i in range(json_start, len(analysis_text)):
                    if analysis_text[i] == '{':
                        brace_count += 1
                    elif analysis_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                json_text = analysis_text[json_start:json_end]
                parsed_data = json.loads(json_text)
                print(f"DEBUG: Successfully extracted JSON from response")
            else:
                # Fallback to full text parsing
                parsed_data = json.loads(analysis_text.strip())
            
            # Extract structured data
            text_blocks = []
            geographic_indicators = []
            
            # Process text elements from JSON
            for item in parsed_data.get('text_elements', []):
                text_blocks.append({
                    'text': item.get('text', ''),
                    'confidence': item.get('confidence', 85),
                    'bbox': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                    'method': 'minicpm_structured',
                    'source': 'json_response'
                })
            
            # Process geographic indicators from JSON (flexible format)
            for item in parsed_data.get('geographic_indicators', []):
                # Handle both expected format and MiniCPM-V's actual format
                text = item.get('text', item.get('name', ''))
                confidence = item.get('confidence', 85)  # Default confidence
                indicator_type = item.get('type', 'city_name' if item.get('country') else 'unknown')
                description = item.get('description', '')
                
                # If MiniCPM-V format, create description from available fields
                if item.get('country') and not description:
                    description = f"Located in {item['country']}"
                
                # Validate street names for accuracy
                validation_warnings = []
                if indicator_type == 'street_name' and text:
                    validation_warnings = validate_street_name(text, confidence)
                
                if text:  # Only add if we have actual text
                    geographic_indicators.append({
                        'type': indicator_type,
                        'text': text,
                        'confidence': confidence / 100.0,  # Convert to decimal
                        'description': description,
                        'validation_warnings': validation_warnings
                    })
            
            # Process landmarks as geographic indicators (flexible format)
            for landmark in parsed_data.get('landmarks', []):
                name = landmark.get('name', '')
                confidence = landmark.get('confidence', 90)
                description = landmark.get('description', '')
                
                # If MiniCPM-V format, create description from type
                if landmark.get('type') and not description:
                    description = f"Type: {landmark['type']}"
                
                if name:  # Only add if we have a name
                    geographic_indicators.append({
                        'type': 'landmark',
                        'text': name,
                        'confidence': confidence / 100.0,  # Convert to decimal
                        'description': description
                    })
            
            # Process new comprehensive analysis fields
            comprehensive_data = {
                'people': parsed_data.get('people', []),
                'architectural_features': parsed_data.get('architectural_features', []),
                'environmental_details': parsed_data.get('environmental_details', []),
                'scene_composition': parsed_data.get('scene_composition', {}),
                'signs': parsed_data.get('signs', []),
                'vehicles': parsed_data.get('vehicles', []),
                'license_plates': parsed_data.get('license_plates', [])
            }
            
            # Use detailed analysis as full text
            detailed_analysis = parsed_data.get('detailed_analysis', analysis_text)
                
        except json.JSONDecodeError:
            print("DEBUG: JSON parsing failed - no structured data available")
            print(f"DEBUG: Raw response text: {analysis_text[:200]}...")
            geographic_indicators = []
            text_blocks = []
            detailed_analysis = analysis_text
            comprehensive_data = {}
            parsed_data = None
        
        # Detect languages mentioned in the analysis
        detected_languages = detect_text_languages(detailed_analysis)
        
        # MiniCPM-V handles ALL location intelligence - no additional processing needed
        location_candidates = []
        if parsed_data and parsed_data.get('location_analysis'):
            print("DEBUG: MiniCPM-V provided structured location data")
            # Use MiniCPM-V's suggested search query for geocoding
            suggested_search = parsed_data.get('coordinates_estimate', {}).get('suggested_search')
            if suggested_search:
                try:
                    from .location_intelligence import LocationIntelligenceProcessor
                    processor = LocationIntelligenceProcessor()
                    geocoded_results = processor._geocode_query(suggested_search)
                    for result in geocoded_results[:3]:  # Top 3 results
                        candidate = type('LocationCandidate', (), {
                            'latitude': result['lat'],
                            'longitude': result['lon'],
                            'confidence': 0.9,  # High confidence from MiniCPM-V
                            'address': result.get('display_name', ''),
                            'city': result.get('city', ''),
                            'state': result.get('state', ''),
                            'country': result.get('country', ''),
                            'matched_clues': [],
                            'source': 'minicpm_direct',
                            'accuracy_meters': result.get('accuracy', None)
                        })()
                        location_candidates.append(candidate)
                    print(f"DEBUG: Geocoded {len(location_candidates)} candidates from MiniCPM-V search query")
                except Exception as e:
                    print(f"DEBUG: Geocoding failed: {e}")
        
        # Include comprehensive data if available
        result = {
            'success': True,
            'method': 'ollama_minicpm_comprehensive',
            'full_text': detailed_analysis,
            'text_blocks': text_blocks,
            'geographic_indicators': geographic_indicators,
            'location_candidates': location_candidates,
            'detected_languages': detected_languages,
            'total_blocks': len(text_blocks),
            'average_confidence': 95,  # High confidence for MiniCPM-V analysis
            'intelligence_categories': categorize_osint_intelligence(detailed_analysis)
        }
        
        # Add comprehensive analysis data if available
        if 'comprehensive_data' in locals():
            result['comprehensive_analysis'] = comprehensive_data
            
        return result
        
    except Exception as e:
        return {'error': f'Ollama MiniCPM-V failed: {str(e)}'}

def extract_with_easyocr(image_path, languages=['en']):
    """
    Extract text using EasyOCR - best for natural scene text
    """
    try:
        # Initialize EasyOCR reader
        reader = easyocr.Reader(languages, gpu=False)  # Set gpu=True if CUDA available
        
        # Read text from image
        results = reader.readtext(image_path)
        
        text_blocks = []
        full_text_parts = []
        
        for (bbox, text, confidence) in results:
            # EasyOCR returns confidence as 0-1, convert to percentage
            conf_percent = int(confidence * 100)
            
            if conf_percent > 30 and text.strip():  # Filter low confidence
                # Convert bbox coordinates
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                text_blocks.append({
                    'text': text.strip(),
                    'confidence': conf_percent,
                    'bbox': {
                        'x': int(min(x_coords)),
                        'y': int(min(y_coords)),
                        'width': int(max(x_coords) - min(x_coords)),
                        'height': int(max(y_coords) - min(y_coords))
                    },
                    'method': 'easyocr'
                })
                
                full_text_parts.append(text.strip())
        
        full_text = ' '.join(full_text_parts)
        
        # Note: Geographic indicators analysis only available through MiniCPM-V structured JSON
        geographic_indicators = []
        detected_languages = detect_text_languages(full_text)
        
        return {
            'success': True,
            'method': 'easyocr',
            'full_text': full_text,
            'text_blocks': text_blocks,
            'geographic_indicators': geographic_indicators,
            'detected_languages': detected_languages,
            'total_blocks': len(text_blocks),
            'average_confidence': sum(block['confidence'] for block in text_blocks) / len(text_blocks) if text_blocks else 0
        }
        
    except Exception as e:
        return {'error': f'EasyOCR failed: {str(e)}'}

def extract_with_keras_ocr(image_path):
    """
    Extract text using Keras-OCR - good for street signs and natural scenes
    """
    try:
        # Initialize Keras-OCR pipeline
        pipeline = keras_ocr.pipeline.Pipeline()
        
        # Load and process image
        image = keras_ocr.tools.read(image_path)
        predictions = pipeline.recognize([image])[0]
        
        text_blocks = []
        full_text_parts = []
        
        for text, bbox in predictions:
            if text.strip():
                # Keras-OCR bbox format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                text_blocks.append({
                    'text': text.strip(),
                    'confidence': 85,  # Keras-OCR doesn't provide confidence, use default
                    'bbox': {
                        'x': int(min(x_coords)),
                        'y': int(min(y_coords)),
                        'width': int(max(x_coords) - min(x_coords)),
                        'height': int(max(y_coords) - min(y_coords))
                    },
                    'method': 'keras_ocr'
                })
                
                full_text_parts.append(text.strip())
        
        full_text = ' '.join(full_text_parts)
        
        # Note: Geographic indicators analysis only available through MiniCPM-V structured JSON
        geographic_indicators = []
        detected_languages = detect_text_languages(full_text)
        
        return {
            'success': True,
            'method': 'keras_ocr',
            'full_text': full_text,
            'text_blocks': text_blocks,
            'geographic_indicators': geographic_indicators,
            'detected_languages': detected_languages,
            'total_blocks': len(text_blocks),
            'average_confidence': 85  # Default since Keras-OCR doesn't provide per-word confidence
        }
        
    except Exception as e:
        return {'error': f'Keras-OCR failed: {str(e)}'}

def extract_with_tesseract(image_path, preprocess=True, languages=['eng']):
    """
    Extract text using Tesseract - mainly for document-style text
    """
    try:
        # Load and preprocess image
        if preprocess:
            processed_image = preprocess_for_ocr(image_path)
        else:
            processed_image = cv2.imread(image_path)
        
        if processed_image is None:
            return {'error': 'Could not load image'}
        
        # Convert to PIL Image
        if len(processed_image.shape) == 3:
            pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
        else:
            pil_image = Image.fromarray(processed_image)
        
        # Configure for better scene text recognition
        lang_string = '+'.join(languages) if isinstance(languages, list) else str(languages)
        custom_config = r'--oem 3 --psm 6'  # Less restrictive for scene text
        
        # Get full text
        full_text = pytesseract.image_to_string(pil_image, lang=lang_string, config=custom_config)
        
        # Get detailed data
        detailed_data = pytesseract.image_to_data(pil_image, lang=lang_string, config=custom_config, output_type=pytesseract.Output.DICT)
        
        # Process results
        text_blocks = []
        n_boxes = len(detailed_data['text'])
        
        for i in range(n_boxes):
            confidence = int(detailed_data['conf'][i])
            text = detailed_data['text'][i].strip()
            
            if confidence > 30 and text:
                text_blocks.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': {
                        'x': detailed_data['left'][i],
                        'y': detailed_data['top'][i],
                        'width': detailed_data['width'][i],
                        'height': detailed_data['height'][i]
                    },
                    'method': 'tesseract'
                })
        
        # Note: Geographic indicators analysis only available through MiniCPM-V structured JSON
        geographic_indicators = []
        detected_languages = detect_text_languages(full_text)
        
        return {
            'success': True,
            'method': 'tesseract',
            'full_text': full_text.strip(),
            'text_blocks': text_blocks,
            'geographic_indicators': geographic_indicators,
            'detected_languages': detected_languages,
            'total_blocks': len(text_blocks),
            'average_confidence': sum(block['confidence'] for block in text_blocks) / len(text_blocks) if text_blocks else 0
        }
        
    except Exception as e:
        return {'error': f'Tesseract failed: {str(e)}'}

def preprocess_for_ocr(image_path):
    """
    Preprocess image to improve OCR accuracy
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        # Use Otsu's thresholding for automatic threshold selection
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the image
        kernel = np.ones((2, 2), np.uint8)
        
        # Remove noise
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Close gaps
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Dilate to make text thicker (helps with OCR)
        dilated = cv2.dilate(closing, kernel, iterations=1)
        
        return dilated
        
    except Exception as e:
        print(f"Preprocessing error: {e}")
        # Return original image if preprocessing fails
        return cv2.imread(image_path)

# Geographic analysis now handled by MiniCPM-V structured JSON response

def detect_text_languages(text):
    """
    Simple language detection based on character patterns
    Note: In production, you'd use a proper language detection library
    """
    if not text:
        return ['unknown']
    
    # Handle different input types (string, list, dict)
    if isinstance(text, list):
        text = ' '.join(str(item) for item in text)
    elif isinstance(text, dict):
        text = str(text)
    elif not isinstance(text, str):
        text = str(text)
    
    detected = []
    text_lower = text.lower()
    
    # Check for different scripts using character range checks
    for char in text:
        char_code = ord(char)
        
        # Cyrillic (Russian)
        if 0x0430 <= char_code <= 0x044F or 0x0451 == char_code:
            if 'russian' not in detected:
                detected.append('russian')
        
        # Greek
        elif 0x03B1 <= char_code <= 0x03C9:
            if 'greek' not in detected:
                detected.append('greek')
        
        # Chinese
        elif 0x4E00 <= char_code <= 0x9FFF:
            if 'chinese' not in detected:
                detected.append('chinese')
        
        # Japanese (Hiragana and Katakana)
        elif (0x3040 <= char_code <= 0x309F) or (0x30A0 <= char_code <= 0x30FF):
            if 'japanese' not in detected:
                detected.append('japanese')
        
        # Korean
        elif 0xAC00 <= char_code <= 0xD7AF:
            if 'korean' not in detected:
                detected.append('korean')
        
        # Arabic
        elif 0x0600 <= char_code <= 0x06FF:
            if 'arabic' not in detected:
                detected.append('arabic')
    
    # Check for European language indicators
    if any(c in text_lower for c in ['ä', 'ö', 'ü', 'ß']):
        detected.append('german')
    elif any(c in text_lower for c in ['à', 'á', 'â', 'ã', 'ç', 'è', 'é', 'ê', 'ë', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ù', 'ú', 'û', 'ü', 'ý']):
        detected.append('romance_language')  # French, Spanish, Italian, etc.
    
    # Default to English if only Latin characters and no other language detected
    if not detected and any(c.isalpha() for c in text):
        detected.append('english')
    
    return detected if detected else ['unknown']

# Text element extraction now handled by MiniCPM-V structured JSON response

def categorize_osint_intelligence(analysis_text):
    """
    Categorize the intelligence found in the comprehensive analysis
    """
    categories = {
        'geographic': [],
        'temporal': [],
        'environmental': [],
        'infrastructure': [],
        'cultural': [],
        'vehicles': [],
        'text_elements': []
    }
    
    # Handle different input types
    if isinstance(analysis_text, dict):
        # Convert dict to string representation
        analysis_text = str(analysis_text)
    elif not isinstance(analysis_text, str):
        # Convert other types to string
        analysis_text = str(analysis_text)
    
    if not analysis_text:
        return categories
        
    text_upper = analysis_text.upper()
    
    # Geographic indicators
    geographic_terms = [
        'STREET', 'AVENUE', 'ROAD', 'BOULEVARD', 'ADDRESS', 'BUILDING', 'CITY', 'TOWN',
        'NEIGHBORHOOD', 'DISTRICT', 'LOCATION', 'COORDINATES', 'POSTAL', 'ZIP'
    ]
    for term in geographic_terms:
        if term in text_upper:
            categories['geographic'].append(f"Geographic reference: {term}")
    
    # Temporal indicators
    temporal_terms = [
        'TIME', 'CLOCK', 'DAY', 'NIGHT', 'MORNING', 'AFTERNOON', 'EVENING', 'SHADOW',
        'LIGHTING', 'SEASON', 'WEATHER', 'SUNNY', 'CLOUDY', 'OVERCAST'
    ]
    for term in temporal_terms:
        if term in text_upper:
            categories['temporal'].append(f"Temporal indicator: {term}")
    
    # Environmental indicators
    environmental_terms = [
        'TREE', 'PLANT', 'VEGETATION', 'FOLIAGE', 'LANDSCAPE', 'TERRAIN', 'MOUNTAIN',
        'HILL', 'WATER', 'RIVER', 'GEOLOGICAL', 'FLORA', 'FAUNA', 'ANIMAL', 'BIRD'
    ]
    for term in environmental_terms:
        if term in text_upper:
            categories['environmental'].append(f"Environmental element: {term}")
    
    # Infrastructure indicators
    infrastructure_terms = [
        'TRAFFIC', 'ROAD', 'STREET', 'SIDEWALK', 'BUILDING', 'ARCHITECTURE', 'BRIDGE',
        'UTILITY', 'POWER', 'INFRASTRUCTURE', 'URBAN', 'PLANNING', 'STOP', 'SIGN'
    ]
    for term in infrastructure_terms:
        if term in text_upper:
            categories['infrastructure'].append(f"Infrastructure element: {term}")
    
    # Cultural indicators
    cultural_terms = [
        'CLOTHING', 'STYLE', 'PEOPLE', 'PEDESTRIAN', 'CULTURAL', 'DRESS', 'ACTIVITY',
        'BEHAVIOR', 'SOCIAL', 'HUMAN', 'PERSON'
    ]
    for term in cultural_terms:
        if term in text_upper:
            categories['cultural'].append(f"Cultural indicator: {term}")
    
    # Vehicle indicators
    vehicle_terms = [
        'CAR', 'VEHICLE', 'TRUCK', 'BUS', 'MOTORCYCLE', 'TAXI', 'LICENSE', 'PLATE',
        'TRANSPORTATION', 'PARKING', 'TRAFFIC'
    ]
    for term in vehicle_terms:
        if term in text_upper:
            categories['vehicles'].append(f"Vehicle element: {term}")
    
    # Text elements
    text_terms = [
        'TEXT', 'SIGN', 'BILLBOARD', 'DISPLAY', 'WRITING', 'LETTERS', 'NUMBERS',
        'WORDS', 'READING', 'VISIBLE'
    ]
    for term in text_terms:
        if term in text_upper:
            categories['text_elements'].append(f"Text element: {term}")
    
    # Remove duplicates and limit results
    for category in categories:
        categories[category] = list(set(categories[category]))[:5]  # Top 5 per category
    
    return categories

def validate_street_name(street_name, confidence):
    """
    Basic validation for street names to flag potentially inaccurate readings
    """
    warnings = []
    
    # Common OCR misreadings that should be flagged
    suspicious_patterns = [
        'weybren',  # Not a real street name pattern
        'qqqq', 'wwww', 'eeee',  # Repetitive characters often indicate OCR errors
        '|||', '...', '---',  # Special character patterns
    ]
    
    street_lower = street_name.lower()
    
    # Check for suspicious patterns
    for pattern in suspicious_patterns:
        if pattern in street_lower:
            warnings.append(f"Suspicious pattern '{pattern}' detected - possible OCR error")
    
    # Check for unusual character combinations
    if len(street_name) > 3:
        vowels = 'aeiou'
        consonant_count = 0
        for char in street_name.lower():
            if char.isalpha() and char not in vowels:
                consonant_count += 1
            else:
                consonant_count = 0
            if consonant_count > 4:  # Too many consecutive consonants
                warnings.append("Unusual consonant pattern - verify spelling")
                break
    
    # If low confidence and warnings, suggest manual verification
    if confidence < 70 and warnings:
        warnings.append("Low confidence reading with suspicious patterns - manual verification recommended")
    
    return warnings

def combine_ocr_results(primary_result, secondary_result):
    """
    Combine results from MiniCPM-V and Tesseract for comprehensive text extraction
    Prioritizes MiniCPM-V's structured analysis while adding missed text from Tesseract
    """
    try:
        # Start with primary result as base
        combined = primary_result.copy()
        
        # Get existing text from primary result
        primary_texts = set()
        for block in primary_result.get('text_blocks', []):
            primary_texts.add(block.get('text', '').strip().lower())
        
        # Add unique text blocks from secondary result
        secondary_blocks = []
        for block in secondary_result.get('text_blocks', []):
            text = block.get('text', '').strip()
            if text and text.lower() not in primary_texts:
                # Add with indication it came from secondary OCR
                enhanced_block = block.copy()
                enhanced_block['method'] = f"{enhanced_block.get('method', 'tesseract')}_supplemental"
                enhanced_block['source'] = 'tesseract_fallback'
                secondary_blocks.append(enhanced_block)
                primary_texts.add(text.lower())  # Prevent duplicates
        
        # Merge text blocks
        all_text_blocks = combined.get('text_blocks', []) + secondary_blocks
        combined['text_blocks'] = all_text_blocks
        combined['total_blocks'] = len(all_text_blocks)
        
        # Analyze secondary text for potential business names and geographic indicators
        business_indicators = extract_business_intelligence(secondary_blocks)
        
        # Add business intelligence to geographic indicators
        existing_geo = combined.get('geographic_indicators', [])
        combined['geographic_indicators'] = existing_geo + business_indicators
        
        # Update method to indicate multi-pass analysis
        combined['method'] = f"{combined.get('method', 'unknown')}_multipass"
        
        # Enhanced full text combining both sources
        primary_text = combined.get('full_text', '')
        secondary_texts = [block.get('text', '') for block in secondary_blocks if block.get('text', '')]
        if secondary_texts:
            additional_text = ' | '.join(secondary_texts)
            combined['full_text'] = f"{primary_text}\n\nAdditional text detected: {additional_text}"
        
        return combined
        
    except Exception as e:
        print(f"Error combining OCR results: {e}")
        return primary_result

def extract_business_intelligence(text_blocks):
    """
    Extract business names and location intelligence from text blocks
    """
    business_indicators = []
    business_keywords = ['restaurant', 'cafe', 'pizza', 'deli', 'market', 'shop', 'store', 'bar', 'grill', 'bistro']
    
    for block in text_blocks:
        text = block.get('text', '').strip()
        confidence = block.get('confidence', 70)
        
        if not text:
            continue
        
        # Check if text contains business keywords or appears to be a business name
        text_lower = text.lower()
        is_business = False
        business_type = 'business'
        
        for keyword in business_keywords:
            if keyword in text_lower:
                is_business = True
                business_type = keyword
                break
        
        # Also check for patterns that look like business names
        if not is_business:
            # Business names often have specific patterns
            if (len(text.split()) <= 4 and  # Short names
                text[0].isupper() and  # Starts with capital
                not text.lower().startswith(('the ', 'and ', 'or ', 'but '))):  # Not common words
                is_business = True
                business_type = 'potential_business'
        
        if is_business:
            business_indicators.append({
                'type': 'business_name',
                'text': text,
                'confidence': min(confidence / 100.0, 0.8),  # Cap confidence for supplemental text
                'description': f"Potential {business_type} detected via secondary OCR",
                'validation_warnings': [],
                'source': 'tesseract_business_detection'
            })
    
    return business_indicators

def extract_license_plates(image_path):
    """
    Specialized function to extract potential license plate text
    """
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply more aggressive preprocessing for license plates
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Edge detection to find rectangular regions
        edges = cv2.Canny(enhanced, 50, 150, apertureSize=3)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        license_candidates = []
        
        for contour in contours:
            # Filter contours by area and aspect ratio
            area = cv2.contourArea(contour)
            if area < 1000:  # Too small
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # License plates typically have aspect ratio between 2:1 and 5:1
            if 2.0 <= aspect_ratio <= 5.0:
                # Extract region
                roi = enhanced[y:y+h, x:x+w]
                
                # Apply OCR with config optimized for license plates
                config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                text = pytesseract.image_to_string(roi, config=config).strip()
                
                # Filter results that look like license plates (alphanumeric characters only)
                if text and len(text) >= 3 and all(c.isalnum() or c in ' -' for c in text):
                    license_candidates.append({
                        'text': text,
                        'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': 0.7,  # Base confidence for license plate detection
                        'aspect_ratio': aspect_ratio
                    })
        
        return license_candidates
        
    except Exception as e:
        print(f"License plate extraction error: {e}")
        return []

def get_ocr_capabilities():
    """
    Check OCR system capabilities and configuration
    """
    try:
        # Check if Tesseract is available
        version = pytesseract.get_tesseract_version()
        
        # Get available languages
        try:
            languages = pytesseract.get_languages()
        except:
            languages = ['eng']  # Default
        
        return {
            'tesseract_available': True,
            'version': str(version),
            'available_languages': languages,
            'status': 'ready'
        }
        
    except Exception as e:
        return {
            'tesseract_available': False,
            'error': str(e),
            'status': 'not_configured',
            'setup_instructions': [
                'Install Tesseract OCR',
                'Add Tesseract to system PATH',
                'Install additional language packs if needed',
                'Configure pytesseract.tesseract_cmd if necessary'
            ]
        }