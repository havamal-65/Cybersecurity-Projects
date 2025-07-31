#!/usr/bin/env python3
"""
Analyze all 5 photos and generate comprehensive reports
"""

import requests
import time
import os
from pathlib import Path

def analyze_all_photos():
    """Analyze all photos in uploads directory and generate reports"""
    
    # Your 5 photos
    photos = [
        "uploads/eiffel-tower.jpg",
        "uploads/flowers.jpg", 
        "uploads/intersection.jpg",
        "uploads/nyc street.jpg",
        "uploads/red.jpg"
    ]
    
    server_url = "http://localhost:5000"
    reports_dir = "generated_reports"
    
    # Create reports directory
    os.makedirs(reports_dir, exist_ok=True)
    
    print("[INFO] Starting analysis of all 5 photos...")
    print("=" * 60)
    
    # Check server is running
    try:
        response = requests.get(server_url)
        print("[OK] Server is running")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is not running. Start it with: python app.py")
        return
    
    results = []
    
    for i, photo_path in enumerate(photos, 1):
        if not os.path.exists(photo_path):
            print(f"[ERROR] Photo {i}: {photo_path} not found")
            continue
            
        photo_name = Path(photo_path).name
        print(f"\n[PHOTO {i}] Analyzing: {photo_name}")
        print("-" * 40)
        
        try:
            # Upload image
            with open(photo_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f'{server_url}/api/upload', files=files)
                
            if not response.ok:
                print(f"[ERROR] Upload failed: {response.text}")
                continue
                
            data = response.json()
            image_id = data.get('image_id')
            print(f"[OK] Uploaded successfully - ID: {image_id}")
            
            # Start analysis
            print("[INFO] Starting analysis...")
            response = requests.post(f'{server_url}/api/analyze/{image_id}')
            
            if not response.ok:
                print(f"[ERROR] Analysis failed: {response.text}")
                continue
                
            analysis_data = response.json()
            print(f"[OK] Analysis completed - Found {analysis_data.get('results_count', 0)} indicators")
            
            # Wait for analysis to complete
            time.sleep(3)
            
            # Generate report
            print("[INFO] Generating report...")
            response = requests.get(f'{server_url}/api/report/{image_id}?format=json')
            
            if not response.ok:
                print(f"[ERROR] Report generation failed: {response.text}")
                continue
                
            report_data = response.json()
            
            if report_data.get('success'):
                markdown_report = report_data['markdown_report']
                
                # Save markdown report
                report_filename = f"{reports_dir}/{photo_name.replace('.jpg', '').replace('.png', '')}_report.md"
                with open(report_filename, 'w', encoding='utf-8') as f:
                    f.write(markdown_report)
                
                print(f"[OK] Report saved: {report_filename}")
                print(f"[INFO] Report length: {len(markdown_report)} characters")
                
                # Also save HTML version
                html_response = requests.get(f'{server_url}/api/report/{image_id}?format=html')
                if html_response.ok:
                    html_filename = f"{reports_dir}/{photo_name.replace('.jpg', '').replace('.png', '')}_report.html"
                    with open(html_filename, 'w', encoding='utf-8') as f:
                        f.write(html_response.text)
                    print(f"[OK] HTML report saved: {html_filename}")
                
                results.append({
                    'photo': photo_name,
                    'image_id': image_id,
                    'report_file': report_filename,
                    'analysis_results': analysis_data.get('results_count', 0),
                    'confidence': analysis_data.get('overall_confidence', 0)
                })
                
            else:
                print(f"[ERROR] Report generation failed: {report_data.get('error')}")
                
        except Exception as e:
            print(f"[ERROR] Error processing {photo_name}: {e}")
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUMMARY] ANALYSIS COMPLETE")
    print("=" * 60)
    
    if results:
        print(f"[SUCCESS] Successfully analyzed {len(results)} photos:")
        for result in results:
            print(f"  Photo: {result['photo']}")
            print(f"    Indicators: {result['analysis_results']}")
            print(f"    Confidence: {result['confidence']:.1%}")
            print(f"    Report: {result['report_file']}")
            print()
            
        print(f"[INFO] All reports saved in: {reports_dir}/")
        print("[INFO] Open the HTML files in your browser for best viewing experience")
        
    else:
        print("[ERROR] No photos were successfully analyzed")

if __name__ == "__main__":
    analyze_all_photos()