#!/usr/bin/env python3
"""
Test the upload endpoint directly
"""

import requests
import os

def test_upload():
    # Test if server is running
    try:
        response = requests.get('http://localhost:5000/')
        print(f"[OK] Server is running - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Server is not running. Start it with: python app.py")
        return
    
    # Test upload endpoint with a sample file
    sample_files = [
        "uploads/0544bf74-8825-4af4-87b5-28a12717d2b0.jpg",
        "uploads/daa1358b-a53f-4649-84a2-c278f03512b7.png"
    ]
    
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            print(f"[TEST] Testing upload with: {sample_file}")
            
            try:
                with open(sample_file, 'rb') as f:
                    files = {'file': f}
                    response = requests.post('http://localhost:5000/api/upload', 
                                           files=files, 
                                           timeout=10)
                
                print(f"[RESULT] Upload status: {response.status_code}")
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    print(f"[SUCCESS] Upload successful: {data}")
                    return data.get('image_id')
                else:
                    print(f"[ERROR] Upload failed: {response.text}")
                    
            except requests.exceptions.Timeout:
                print("[ERROR] Upload request timed out")
            except Exception as e:
                print(f"[ERROR] Upload error: {e}")
            break
    else:
        print("[ERROR] No sample files found in uploads/ directory")
    
    return None

if __name__ == "__main__":
    test_upload()