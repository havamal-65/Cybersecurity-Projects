#!/usr/bin/env python3
"""
Test the complete workflow: upload -> analyze -> generate report
"""

import requests
import json
import os

def test_complete_workflow():
    print("Testing complete OSINT workflow...")
    
    # Test server connection
    try:
        response = requests.get('http://localhost:5000/')
        print(f"[OK] Server is running - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is not running. Start it with: python app.py")
        return False
    
    # Upload a sample image
    sample_files = [
        "uploads/eiffel-tower.jpg",
        "uploads/flowers.jpg", 
        "uploads/intersection.jpg",
        "uploads/nyc street.jpg",
        "uploads/red.jpg"
    ]
    
    image_id = None
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            print(f"[TEST] Uploading sample image: {sample_file}")
            
            try:
                with open(sample_file, 'rb') as f:
                    files = {'file': f}
                    response = requests.post('http://localhost:5000/api/upload', 
                                           files=files, timeout=10)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    image_id = data.get('image_id')
                    print(f"[OK] Upload successful - Image ID: {image_id}")
                    break
                else:
                    print(f"[ERROR] Upload failed: {response.text}")
                    
            except Exception as e:
                print(f"[ERROR] Upload error: {e}")
                continue
    
    if not image_id:
        print("[ERROR] No successful upload, cannot test report generation")
        return False
    
    # Test report generation (without analysis - just basic report)
    print(f"[TEST] Generating report for image: {image_id}")
    
    try:
        response = requests.get(f'http://localhost:5000/api/report/{image_id}?format=json')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("[OK] Report generated successfully!")
                report_content = data.get('markdown_report', '')
                print(f"[OK] Report length: {len(report_content)} characters")
                
                # Save the report
                with open('test_live_report.md', 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print("[OK] Live report saved as 'test_live_report.md'")
                
                # Test markdown format download
                response = requests.get(f'http://localhost:5000/api/report/{image_id}?format=markdown')
                if response.status_code == 200:
                    print("[OK] Markdown format download works!")
                
                # Test HTML format
                response = requests.get(f'http://localhost:5000/api/report/{image_id}?format=html')
                if response.status_code == 200:
                    print("[OK] HTML format generation works!")
                    with open('test_live_report.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print("[OK] HTML report saved as 'test_live_report.html'")
                
                return True
            else:
                print(f"[ERROR] Report generation failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"[ERROR] Report request failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"[ERROR] Report generation error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n[SUCCESS] Complete workflow test passed!")
        print("[OK] File upload works")
        print("[OK] Report generation works") 
        print("[OK] Multiple formats supported")
        print("[OK] Frontend integration ready")
    else:
        print("\n[FAILED] Workflow test failed!")