#!/usr/bin/env python3
"""
Simple test to check if the Flask app starts correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app, db
    print("[OK] App imports successfully")
    
    # Test app context
    with app.app_context():
        db.create_all()
        print("[OK] Database initialization works")
    
    # Test if app can start
    print("[OK] Flask app configuration:")
    print(f"   - Debug mode: {app.debug}")
    print(f"   - Secret key set: {'SECRET_KEY' in app.config}")
    print(f"   - Upload folder: {app.config.get('UPLOAD_FOLDER')}")
    print(f"   - Max content length: {app.config.get('MAX_CONTENT_LENGTH')}")
    
    # Test routes
    print("[OK] Registered routes:")
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/static'):
            print(f"   - {rule.rule} [{', '.join(rule.methods)}]")
    
    print("\n[READY] App appears ready to run!")
    print("Try: python app.py")
    
except Exception as e:
    print(f"[ERROR] Error during app initialization: {e}")
    import traceback
    traceback.print_exc()