#!/usr/bin/env python3
"""
Test the report generation functionality
"""

from services.report_generator import OSINTReportGenerator
import json
from datetime import datetime

def test_report_generation():
    print("Testing OSINT Report Generation...")
    
    # Create sample data
    sample_image_data = {
        'id': 'test-123',
        'filename': 'sample_image.jpg',
        'file_size': 1024000,
        'upload_date': datetime.now().isoformat()
    }
    
    sample_results = [
        {
            'id': 'result-1',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'confidence_score': 85.5,
            'method_used': 'EXIF_GPS',
            'source_api': 'exif',
            'accuracy_meters': 10,
            'raw_response': json.dumps({
                'method': 'exif_extraction',
                'gps_coordinates': {
                    'latitude': 40.7128,
                    'longitude': -74.0060,
                    'lat_ref': 'N',
                    'lon_ref': 'W'
                },
                'text_blocks': [
                    {'text': 'NEW YORK', 'confidence': 90, 'method': 'tesseract'},
                    {'text': 'BROADWAY', 'confidence': 85, 'method': 'tesseract'}
                ],
                'geographic_indicators': [
                    {'type': 'known_location', 'text': 'NEW YORK', 'confidence': 0.9},
                    {'type': 'street_indicators', 'text': 'BROADWAY', 'confidence': 0.85}
                ],
                'detected_languages': ['english'],
                'intelligence_categories': {
                    'geographic': ['Geographic reference: NEW YORK', 'Street indicator: BROADWAY'],
                    'text_elements': ['Text element: Street signs visible']
                }
            }),
            'created_at': datetime.now().isoformat()
        }
    ]
    
    sample_exif_data = {
        'gps_coordinates': {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'lat_ref': 'N',
            'lon_ref': 'W',
            'altitude': 10.5
        },
        'camera_info': {
            'make': 'Canon',
            'model': 'EOS R5',
            'software': 'Adobe Lightroom',
            'iso': 400,
            'aperture': 'f/2.8',
            'focal_length': '85mm'
        },
        'timestamps': {
            'datetime_original': '2024:01:15 14:30:25',
            'datetime': '2024:01:15 14:30:25'
        }
    }
    
    # Generate report
    try:
        generator = OSINTReportGenerator()
        report = generator.generate_full_report(
            image_data=sample_image_data,
            analysis_results=sample_results,
            exif_data=sample_exif_data
        )
        
        print("[OK] Report generated successfully!")
        print(f"[OK] Report length: {len(report)} characters")
        
        # Save sample report
        with open('sample_osint_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        print("[OK] Sample report saved as 'sample_osint_report.md'")
        
        # Display first few lines
        print("\n[PREVIEW] First 10 lines of report:")
        lines = report.split('\n')
        for i, line in enumerate(lines[:10], 1):
            print(f"{i:2d}: {line}")
        
        if len(lines) > 10:
            print(f"... and {len(lines) - 10} more lines")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("\n[SUCCESS] Report generation test completed!")
    else:
        print("\n[FAILED] Report generation test failed!")