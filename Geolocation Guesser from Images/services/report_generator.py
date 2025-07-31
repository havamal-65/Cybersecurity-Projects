"""
OSINT Geolocation Analysis Report Generator
Converts analysis results into professional markdown reports
"""

from datetime import datetime
import json
# regex removed - using structured JSON from MiniCPM-V instead
from typing import Dict, List, Any, Optional

class OSINTReportGenerator:
    """Generate professional OSINT analysis reports in markdown format"""
    
    def __init__(self):
        self.report_version = "1.0"
        self.generated_timestamp = datetime.utcnow()
    
    def generate_full_report(self, image_data: Dict, analysis_results: List[Dict], 
                           exif_data: Optional[Dict] = None) -> str:
        """
        Generate a comprehensive OSINT analysis report
        
        Args:
            image_data: Basic image information (filename, size, etc.)
            analysis_results: List of analysis results from different methods
            exif_data: EXIF metadata if available
            
        Returns:
            Markdown formatted report string
        """
        report_sections = []
        
        # Header and summary
        report_sections.append(self._generate_header(image_data))
        report_sections.append(self._generate_executive_summary(analysis_results, exif_data))
        
        # EXIF and technical analysis
        if exif_data:
            report_sections.append(self._generate_technical_analysis(exif_data))
        
        # Location intelligence
        report_sections.append(self._generate_location_intelligence(analysis_results))
        
        # Text analysis
        report_sections.append(self._generate_text_analysis(analysis_results))
        
        # Visual intelligence (from MiniCPM-V)
        report_sections.append(self._generate_visual_intelligence(analysis_results))
        
        # Confidence assessment
        report_sections.append(self._generate_confidence_assessment(analysis_results))
        
        # Recommendations
        report_sections.append(self._generate_recommendations(analysis_results, exif_data))
        
        # Footer
        report_sections.append(self._generate_footer())
        
        return "\n\n".join(filter(None, report_sections))
    
    def _generate_header(self, image_data: Dict) -> str:
        """Generate report header with image details"""
        timestamp = self.generated_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return f"""# 🔍 OSINT Geolocation Analysis Report

## 📋 Case Information
- **Image File**: `{image_data.get('filename', 'Unknown')}`
- **File Size**: {self._format_file_size(image_data.get('file_size', 0))}
- **Analysis Date**: {timestamp}
- **Report Version**: {self.report_version}
- **Analysis ID**: `{image_data.get('id', 'N/A')}`

---"""
    
    def _generate_executive_summary(self, results: List[Dict], exif_data: Optional[Dict]) -> str:
        """Generate executive summary section"""
        total_results = len(results)
        gps_available = bool(exif_data and exif_data.get('gps_coordinates'))
        
        # Count analysis methods used
        methods_used = set()
        geographic_indicators = 0
        text_blocks_found = 0
        
        for result in results:
            method = result.get('method_used', 'unknown')
            methods_used.add(method)
            
            if result.get('raw_response'):
                try:
                    raw_data = json.loads(result['raw_response']) if isinstance(result['raw_response'], str) else result['raw_response']
                    if isinstance(raw_data, dict):
                        geographic_indicators += len(raw_data.get('geographic_indicators', []))
                        text_blocks_found += len(raw_data.get('text_blocks', []))
                except:
                    pass
        
        confidence_level = self._calculate_overall_confidence(results)
        confidence_desc = self._get_confidence_description(confidence_level)
        
        summary = f"""## 📊 Executive Summary

### 🎯 Analysis Overview
- **Total Analysis Methods**: {len(methods_used)}
- **Results Generated**: {total_results}
- **GPS Data Available**: {'✅ Yes' if gps_available else '❌ No'}
- **Geographic Indicators Found**: {geographic_indicators}
- **Text Elements Extracted**: {text_blocks_found}

### 🔬 Confidence Assessment
- **Overall Confidence**: {confidence_level*100:.1f}% - **{confidence_desc}**
- **Primary Analysis Method**: {', '.join(methods_used) if methods_used else 'None'}

### 📍 Location Intelligence Status
"""
        
        if gps_available:
            gps = exif_data['gps_coordinates']
            summary += f"- **GPS Coordinates**: {gps['latitude']:.6f}, {gps['longitude']:.6f}\n"
            summary += f"- **Coordinate Reference**: {gps.get('lat_ref', 'N')}{gps.get('lon_ref', 'E')}\n"
        else:
            summary += "- **GPS Coordinates**: Not available in EXIF data\n"
            summary += "- **Alternative Methods**: Analyzing visual and text clues\n"
        
        return summary
    
    def _generate_technical_analysis(self, exif_data: Dict) -> str:
        """Generate technical EXIF analysis section"""
        section = "## 🔧 Technical Analysis\n\n### 📷 Camera Information\n"
        
        camera_info = exif_data.get('camera_info', {})
        if camera_info:
            section += f"- **Camera Make**: {camera_info.get('make', 'Unknown')}\n"
            section += f"- **Camera Model**: {camera_info.get('model', 'Unknown')}\n"
            section += f"- **Software**: {camera_info.get('software', 'Unknown')}\n"
            
            if 'iso' in camera_info:
                section += f"- **ISO**: {camera_info['iso']}\n"
            if 'aperture' in camera_info:
                section += f"- **Aperture**: {camera_info['aperture']}\n"
            if 'shutter_speed' in camera_info:
                section += f"- **Shutter Speed**: {camera_info['shutter_speed']}\n"
            if 'focal_length' in camera_info:
                section += f"- **Focal Length**: {camera_info['focal_length']}\n"
        else:
            section += "- **Camera Information**: Not available in EXIF data\n"
        
        # GPS Information
        section += "\n### 🌍 GPS Metadata\n"
        gps_data = exif_data.get('gps_coordinates')
        if gps_data:
            section += f"- **Latitude**: {gps_data['latitude']:.6f}°\n"
            section += f"- **Longitude**: {gps_data['longitude']:.6f}°\n"
            section += f"- **Coordinate System**: WGS84\n"
            if 'altitude' in gps_data:
                section += f"- **Altitude**: {gps_data['altitude']:.1f}m above sea level\n"
            if 'timestamp' in gps_data:
                section += f"- **GPS Timestamp**: {gps_data['timestamp']}\n"
        else:
            section += "- **GPS Data**: Not embedded in image\n"
        
        # Timestamps
        timestamps = exif_data.get('timestamps', {})
        if timestamps:
            section += "\n### ⏰ Timestamp Analysis\n"
            if 'datetime_original' in timestamps:
                section += f"- **Photo Taken**: {timestamps['datetime_original']}\n"
            if 'datetime' in timestamps:
                section += f"- **Last Modified**: {timestamps['datetime']}\n"
            if 'datetime_digitized' in timestamps:
                section += f"- **Digitized**: {timestamps['datetime_digitized']}\n"
        
        return section
    
    def _generate_location_intelligence(self, results: List[Dict]) -> str:
        """Generate location intelligence analysis"""
        section = "## 📍 Location Intelligence\n\n"
        
        # Extract location results
        location_results = [r for r in results if r.get('latitude') and r.get('longitude')]
        
        if location_results:
            section += "### 🎯 Identified Coordinates\n\n"
            for i, result in enumerate(location_results, 1):
                method = result.get('method_used', 'Unknown')
                confidence = result.get('confidence_score', 0)
                lat = result.get('latitude')
                lon = result.get('longitude')
                
                section += f"**Location {i}** ({method})\n"
                section += f"- **Coordinates**: {lat:.6f}, {lon:.6f}\n"
                section += f"- **Confidence**: {confidence*100:.1f}%\n"
                section += f"- **Source**: {result.get('source_api', 'Unknown')}\n"
                
                if result.get('accuracy_meters'):
                    section += f"- **Accuracy**: ±{result['accuracy_meters']}m\n"
                
                section += f"- **Google Maps**: [View Location](https://maps.google.com/?q={lat},{lon})\n"
                section += f"- **OpenStreetMap**: [View Location](https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=15)\n\n"
        
        # Geographic indicators from text/visual analysis
        geographic_indicators = []
        for result in results:
            if result.get('raw_response'):
                try:
                    raw_data = json.loads(result['raw_response']) if isinstance(result['raw_response'], str) else result['raw_response']
                    if isinstance(raw_data, dict):
                        indicators = raw_data.get('geographic_indicators', [])
                        geographic_indicators.extend(indicators)
                except:
                    pass
        
        if geographic_indicators:
            section += "### 🗺️ Geographic Clues Found\n\n"
            
            # Group indicators by type
            indicator_types = {}
            for indicator in geographic_indicators:
                ind_type = indicator.get('type', 'unknown')
                if ind_type not in indicator_types:
                    indicator_types[ind_type] = []
                indicator_types[ind_type].append(indicator)
            
            for ind_type, indicators in indicator_types.items():
                section += f"**{ind_type.replace('_', ' ').title()}**\n"
                for indicator in indicators:
                    text = indicator.get('text', 'Unknown')
                    confidence = indicator.get('confidence', 0)
                    section += f"- `{text}` (Confidence: {confidence*100:.1f}%)\n"
                    
                    # Show validation warnings if present
                    warnings = indicator.get('validation_warnings', [])
                    if warnings:
                        for warning in warnings:
                            section += f"  - ⚠️ **Warning**: {warning}\n"
                section += "\n"
        
        # Business + Street Name correlation analysis
        business_names = []
        street_names = []
        for indicator in geographic_indicators:
            if indicator.get('type') == 'business_name':
                business_names.append(indicator)
            elif indicator.get('type') == 'street_name':
                street_names.append(indicator)
        
        if business_names and street_names:
            section += "### 🎯 Location Correlation Analysis\n\n"
            section += "**High-Value Intelligence**: Business name + street name combination detected\n\n"
            for business in business_names:
                for street in street_names:
                    combined_confidence = (business.get('confidence', 0) + street.get('confidence', 0)) / 2
                    section += f"**Potential Exact Location**:\n"
                    section += f"- Business: `{business.get('text', '')}` ({business.get('confidence', 0)*100:.1f}% confidence)\n"
                    section += f"- Street: `{street.get('text', '')}` ({street.get('confidence', 0)*100:.1f}% confidence)\n"
                    section += f"- **Combined Intelligence Score**: {combined_confidence*100:.1f}%\n"
                    section += f"- **Search Recommendation**: \"{business.get('text', '')} {street.get('text', '')}\"\n\n"
        
        if not location_results and not geographic_indicators:
            section += "### ❌ No Geographic Data Found\n"
            section += "- No GPS coordinates available in EXIF data\n"
            section += "- No geographic indicators detected in visual/text analysis\n"
            section += "- Consider analyzing additional visual elements or metadata\n"
        
        return section
    
    def _generate_text_analysis(self, results: List[Dict]) -> str:
        """Generate text analysis section"""
        section = "## 📝 Text Analysis\n\n"
        
        # Extract text analysis results
        text_blocks = []
        ocr_methods = set()
        
        for result in results:
            if result.get('raw_response'):
                try:
                    raw_data = json.loads(result['raw_response']) if isinstance(result['raw_response'], str) else result['raw_response']
                    if isinstance(raw_data, dict):
                        blocks = raw_data.get('text_blocks', [])
                        text_blocks.extend(blocks)
                        if raw_data.get('method'):
                            ocr_methods.add(raw_data['method'])
                except:
                    pass
        
        if text_blocks:
            section += f"### 🔤 Extracted Text Elements ({len(text_blocks)} found)\n\n"
            section += f"**Analysis Methods Used**: {', '.join(ocr_methods) if ocr_methods else 'Standard OCR'}\n\n"
            
            # Categorize text blocks for better organization
            business_text = []
            high_confidence_text = []
            supplemental_text = []
            
            for block in text_blocks:
                text = block.get('text', '').strip()
                if not text:
                    continue
                    
                method = block.get('method', 'unknown')
                confidence = block.get('confidence', 0)
                
                # Normalize confidence to 0-100 scale
                if confidence <= 1.0:
                    display_confidence = confidence * 100
                else:
                    display_confidence = confidence
                
                # Categorize text
                text_lower = text.lower()
                business_keywords = ['restaurant', 'cafe', 'pizza', 'deli', 'market', 'shop', 'store', 'bar', 'grill', 'bistro']
                
                if any(keyword in text_lower for keyword in business_keywords):
                    business_text.append((block, display_confidence))
                elif 'supplemental' in method or 'fallback' in method:
                    supplemental_text.append((block, display_confidence))
                else:
                    high_confidence_text.append((block, display_confidence))
            
            # Display business-related text first (highest priority)
            if business_text:
                section += "#### 🏪 Business & Commercial Text (High Priority)\n"
                for block, conf in sorted(business_text, key=lambda x: x[1], reverse=True):
                    text = block.get('text', '').strip()
                    method = block.get('method', 'unknown')
                    section += f"- **`{text}`** ({conf:.1f}% confidence) - {method}\n"
                    if block.get('source') == 'tesseract_business_detection':
                        section += f"  - 🎯 **Location Intelligence**: Potential business name for exact location identification\n"
                section += "\n"
            
            # Display high confidence text
            if high_confidence_text:
                section += "#### 📝 Primary Text Detection\n"
                for block, conf in sorted(high_confidence_text, key=lambda x: x[1], reverse=True)[:15]:
                    text = block.get('text', '').strip()
                    method = block.get('method', 'unknown')
                    section += f"- **`{text}`** ({conf:.1f}% confidence) - {method}\n"
                section += "\n"
            
            # Display supplemental text that might have been missed
            if supplemental_text:
                section += "#### 🔍 Additional Text Detection (Secondary OCR)\n"
                section += "*Text detected by fallback OCR methods - may include business names missed by primary analysis*\n\n"
                for block, conf in sorted(supplemental_text, key=lambda x: x[1], reverse=True)[:10]:
                    text = block.get('text', '').strip()
                    method = block.get('method', 'unknown')
                    section += f"- **`{text}`** ({conf:.1f}% confidence) - {method}\n"
                section += "\n"
            
            total_shown = len(business_text) + min(15, len(high_confidence_text)) + min(10, len(supplemental_text))
            if len(text_blocks) > total_shown:
                section += f"*... and {len(text_blocks) - total_shown} additional text elements*\n\n"
        
        # Language analysis
        detected_languages = set()
        for result in results:
            if result.get('raw_response'):
                try:
                    raw_data = json.loads(result['raw_response']) if isinstance(result['raw_response'], str) else result['raw_response']
                    if isinstance(raw_data, dict):
                        langs = raw_data.get('detected_languages', [])
                        detected_languages.update(langs)
                except:
                    pass
        
        if detected_languages:
            section += "### 🌐 Language Analysis\n"
            section += f"**Detected Languages**: {', '.join(detected_languages).title()}\n\n"
        
        if not text_blocks:
            section += "### ❌ No Text Elements Found\n"
            section += "- No readable text detected in the image\n"
            section += "- Image may not contain textual information\n"
            section += "- Consider using enhanced OCR models if text is expected\n"
        
        return section
    
    def _generate_visual_intelligence(self, results: List[Dict]) -> str:
        """Generate visual intelligence section from MiniCPM-V analysis"""
        section = "## 👁️ Visual Intelligence Analysis\n\n"
        
        # Find comprehensive analysis from MiniCPM-V
        comprehensive_analysis = None
        intelligence_categories = {}
        
        for result in results:
            if result.get('raw_response'):
                try:
                    raw_data = json.loads(result['raw_response']) if isinstance(result['raw_response'], str) else result['raw_response']
                    if isinstance(raw_data, dict):
                        if raw_data.get('method') == 'ollama_minicpm_comprehensive':
                            comprehensive_analysis = raw_data.get('full_text', '')
                            intelligence_categories = raw_data.get('intelligence_categories', {})
                            break
                except:
                    pass
        
        # Look for detailed JSON analysis from MiniCPM-V
        detailed_json_data = None
        for result in results:
            if result.get('raw_response'):
                try:
                    raw_data = json.loads(result['raw_response']) if isinstance(result['raw_response'], str) else result['raw_response']
                    if isinstance(raw_data, dict) and raw_data.get('method') == 'ollama_minicpm_comprehensive':
                        # Check if we have JSON data in full_text
                        full_text = raw_data.get('full_text', '')
                        if full_text.startswith('{'):
                            try:
                                # Try to extract just the JSON part (before any additional text)
                                json_start = full_text.find('{')
                                if json_start != -1:
                                    # Find matching closing brace
                                    brace_count = 0
                                    json_end = json_start
                                    for i in range(json_start, len(full_text)):
                                        if full_text[i] == '{':
                                            brace_count += 1
                                        elif full_text[i] == '}':
                                            brace_count -= 1
                                            if brace_count == 0:
                                                json_end = i + 1
                                                break
                                    
                                    if json_end > json_start and brace_count == 0:
                                        json_str = full_text[json_start:json_end]
                                        detailed_json_data = json.loads(json_str)
                                        break
                            except Exception as e:
                                print(f"JSON parsing failed: {e}")
                                pass
                except:
                    pass

        if detailed_json_data:
            section += "### 🤖 AI Visual Analysis (MiniCPM-V)\n\n"
            
            # Scene Overview from comprehensive prompt
            if detailed_json_data.get('scene_overview'):
                section += "**🎬 Complete Scene Description**\n"
                section += f"{detailed_json_data['scene_overview']}\n\n"
            
            # Detailed Analysis
            if detailed_json_data.get('detailed_analysis'):
                section += "**🔍 Comprehensive Analysis**\n"
                section += f"{detailed_json_data['detailed_analysis']}\n\n"
            
            # People & Activity from comprehensive analysis
            if detailed_json_data.get('people_and_activity'):
                section += "**👥 People & Activity**\n"
                people_items = detailed_json_data['people_and_activity']
                if isinstance(people_items, list):
                    for item in people_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {people_items}\n"
                section += "\n"
            
            # Architectural Features from comprehensive analysis
            if detailed_json_data.get('architectural_features'):
                section += "**🏢 Architectural Features**\n"
                arch_items = detailed_json_data['architectural_features']
                if isinstance(arch_items, list):
                    for item in arch_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {arch_items}\n"
                section += "\n"
            
            # Environmental Context from comprehensive analysis
            if detailed_json_data.get('environmental_context'):
                section += "**🌤️ Environmental Context**\n"
                env_items = detailed_json_data['environmental_context']
                if isinstance(env_items, list):
                    for item in env_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {env_items}\n"
                section += "\n"
            
            # Vehicles from comprehensive analysis
            if detailed_json_data.get('vehicles'):
                section += "**🚗 Vehicles**\n"
                vehicle_items = detailed_json_data['vehicles']
                if isinstance(vehicle_items, list):
                    for item in vehicle_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {vehicle_items}\n"
                section += "\n"
            
            # Infrastructure from comprehensive analysis
            if detailed_json_data.get('infrastructure'):
                section += "**🏗️ Infrastructure**\n"
                infra_items = detailed_json_data['infrastructure']
                if isinstance(infra_items, list):
                    for item in infra_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {infra_items}\n"
                section += "\n"
            
            # Landmarks and Buildings from comprehensive analysis
            if detailed_json_data.get('landmarks_and_buildings'):
                section += "**🏛️ Landmarks & Buildings**\n"
                landmark_items = detailed_json_data['landmarks_and_buildings']
                if isinstance(landmark_items, list):
                    for item in landmark_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {landmark_items}\n"
                section += "\n"
            
            # Signage and Text from comprehensive analysis
            if detailed_json_data.get('signage_and_text'):
                section += "**📝 Signage & Text**\n"
                signage_items = detailed_json_data['signage_and_text']
                if isinstance(signage_items, list):
                    for item in signage_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {signage_items}\n"
                section += "\n"
            
            # Geographic Indicators from comprehensive analysis
            if detailed_json_data.get('geographic_indicators'):
                section += "**📍 Geographic Indicators**\n"
                geo_items = detailed_json_data['geographic_indicators']
                if isinstance(geo_items, list):
                    for item in geo_items:
                        section += f"- {item}\n"
                else:
                    section += f"- {geo_items}\n"
                section += "\n"
            
                
        elif comprehensive_analysis:
            section += "### 🤖 AI Visual Analysis (MiniCPM-V)\n\n"
            
            # Extract key sections from comprehensive analysis
            analysis_sections = self._parse_minicpm_analysis(comprehensive_analysis)
            
            for section_name, content in analysis_sections.items():
                if content.strip():
                    section += f"**{section_name}**\n"
                    # Format content as bullet points
                    lines = content.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('-'):
                            section += f"- {line}\n"
                        elif line.startswith('-'):
                            section += f"{line}\n"
                    section += "\n"
        
        # Intelligence categories summary
        if intelligence_categories:
            section += "### 📊 Intelligence Categories\n\n"
            for category, items in intelligence_categories.items():
                if items:
                    section += f"**{category.replace('_', ' ').title()}** ({len(items)} items)\n"
                    for item in items[:5]:  # Show top 5 per category
                        section += f"- {item}\n"
                    if len(items) > 5:
                        section += f"- *... and {len(items) - 5} more items*\n"
                    section += "\n"
        
        if not comprehensive_analysis and not intelligence_categories:
            section += "### ❌ Visual Analysis Not Available\n"
            section += "- MiniCPM-V model not configured or unavailable\n"
            section += "- Install Ollama and run `ollama pull minicpm-v` for enhanced analysis\n"
            section += "- Alternative: Manual visual inspection recommended\n"
        
        return section
    
    def _generate_confidence_assessment(self, results: List[Dict]) -> str:
        """Generate confidence assessment section"""
        section = "## 🎯 Confidence Assessment\n\n"
        
        if not results:
            section += "### ❌ No Analysis Results Available\n"
            return section
        
        # Calculate confidence metrics
        confidence_scores = [r.get('confidence_score', 0) for r in results if r.get('confidence_score')]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            max_confidence = max(confidence_scores)
            min_confidence = min(confidence_scores)
            
            section += "### 📈 Statistical Analysis\n"
            section += f"- **Average Confidence**: {avg_confidence*100:.1f}%\n"
            section += f"- **Highest Confidence**: {max_confidence*100:.1f}%\n"
            section += f"- **Lowest Confidence**: {min_confidence*100:.1f}%\n"
            section += f"- **Total Data Points**: {len(confidence_scores)}\n\n"
        
        # Method reliability
        section += "### 🔬 Method Reliability\n"
        method_confidence = {}
        for result in results:
            method = result.get('method_used', 'unknown')
            confidence = result.get('confidence_score', 0)
            if method not in method_confidence:
                method_confidence[method] = []
            method_confidence[method].append(confidence)
        
        for method, scores in method_confidence.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            section += f"- **{method.replace('_', ' ').title()}**: {avg_score*100:.1f}% (n={len(scores)})\n"
        
        # Overall assessment
        overall_confidence = self._calculate_overall_confidence(results)
        assessment = self._get_confidence_description(overall_confidence)
        
        section += f"\n### 🏆 Overall Assessment\n"
        section += f"**{assessment}** - {overall_confidence*100:.1f}% confidence\n\n"
        
        # Convert to percentage if decimal
        confidence_pct = overall_confidence * 100 if overall_confidence <= 1.0 else overall_confidence
        
        if confidence_pct >= 80:
            section += "✅ **High confidence** - Results are likely accurate and reliable\n"
        elif confidence_pct >= 50:
            section += "⚠️ **Moderate confidence** - Results should be verified with additional sources\n"
        else:
            section += "❌ **Low confidence** - Results require manual verification and additional analysis\n"
        
        return section
    
    def _generate_recommendations(self, results: List[Dict], exif_data: Optional[Dict]) -> str:
        """Generate recommendations section"""
        section = "## 💡 Recommendations\n\n"
        
        recommendations = []
        
        # GPS-based recommendations
        if exif_data and exif_data.get('gps_coordinates'):
            recommendations.append("✅ **GPS data available** - Use coordinates for precise location verification")
            recommendations.append("🗺️ **Cross-reference coordinates** with mapping services for location confirmation")
        else:
            recommendations.append("❗ **No GPS data** - Rely on visual and textual analysis for location intelligence")
            recommendations.append("🔍 **Manual analysis needed** - Examine visual elements for geographic clues")
        
        # Text analysis recommendations
        text_found = any(r.get('raw_response', '').find('text_blocks') > -1 for r in results)
        if text_found:
            recommendations.append("📝 **Text elements detected** - Verify street names and addresses manually")
            recommendations.append("🌐 **Language analysis** - Consider cultural and regional context")
        else:
            recommendations.append("❓ **Limited text data** - Focus on visual elements and architectural features")
        
        # Analysis method recommendations
        methods_used = set(r.get('method_used', '') for r in results)
        if 'ollama_minicpm_comprehensive' not in methods_used:
            recommendations.append("🤖 **Enhanced AI analysis** - Install MiniCPM-V for deeper visual intelligence")
        
        # Security recommendations
        recommendations.append("🔒 **Privacy consideration** - Be aware of personal information in analysis")
        recommendations.append("⚖️ **Legal compliance** - Ensure analysis complies with local privacy laws")
        recommendations.append("🔍 **Verification needed** - Cross-reference findings with multiple sources")
        
        section += "### 🎯 Next Steps\n"
        for rec in recommendations:
            section += f"- {rec}\n"
        
        section += "\n### 🛠️ Additional Analysis Options\n"
        section += "- **Reverse image search** - Use Google Images or TinEye for similar images\n"
        section += "- **Metadata forensics** - Examine additional EXIF fields and hidden data\n"
        section += "- **Geospatial analysis** - Compare with satellite imagery and street view\n"
        section += "- **Social media correlation** - Search for related posts or images\n"
        
        return section
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""---

## 📋 Report Information

**Generated by**: OSINT Geolocation Analyzer v{self.report_version}  
**Analysis Engine**: Multi-method approach (EXIF, OCR, AI Vision)  
**Generated on**: {self.generated_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}  

> ⚠️ **Disclaimer**: This analysis is for educational and research purposes only. Results should be verified through multiple independent sources. The accuracy of geolocation data depends on available metadata and image quality.

---

*Report generated using advanced OSINT techniques and AI-powered image analysis*"""
    
    # Helper methods
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _calculate_overall_confidence(self, results: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not results:
            return 0.0
        
        confidence_scores = [r.get('confidence_score', 0) for r in results if r.get('confidence_score')]
        if not confidence_scores:
            return 0.0
        
        # Weighted average - higher scores have more weight
        total_weight = sum(score / 100 for score in confidence_scores)
        weighted_sum = sum(score * (score / 100) for score in confidence_scores)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_confidence_description(self, confidence: float) -> str:
        """Get confidence level description"""
        # Convert to percentage if it's a decimal
        confidence_pct = confidence * 100 if confidence <= 1.0 else confidence
        
        if confidence_pct >= 90:
            return "Excellent"
        elif confidence_pct >= 80:
            return "High"
        elif confidence_pct >= 60:
            return "Moderate"
        elif confidence_pct >= 40:
            return "Low"
        else:
            return "Very Low"
    
    def _parse_minicpm_analysis(self, analysis_text: str) -> Dict[str, str]:
        """Parse MiniCPM-V comprehensive analysis into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check if this is a section header (all caps with colons)
            if line.isupper() and ':' in line and len(line) < 50:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.replace(':', '').strip()
                current_content = []
            elif current_section and line:
                current_content.append(line)
        
        # Save final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections