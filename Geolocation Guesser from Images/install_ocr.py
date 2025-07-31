"""
OCR Installation Script for OSINT Geolocation Tool
Handles PyTorch dependency conflicts and installs EasyOCR properly
"""

import subprocess
import sys
import importlib.util

def check_module(module_name):
    """Check if a module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def run_command(command):
    """Run a pip command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Command: {command}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run command {command}: {e}")
        return False

def install_ocr_dependencies():
    """Install OCR dependencies handling PyTorch conflicts"""
    
    print("=== OSINT Geolocation Tool OCR Setup ===\n")
    
    # Check current PyTorch installation
    if check_module('torch'):
        try:
            import torch
            print(f"Current PyTorch version: {torch.__version__}")
        except:
            print("PyTorch installed but import failed")
    else:
        print("PyTorch not found")
    
    if check_module('easyocr'):
        print("EasyOCR already installed")
        try:
            import easyocr
            print("EasyOCR import successful - OCR should work!")
            return True
        except Exception as e:
            print(f"EasyOCR import failed: {e}")
    
    print("\n=== Installing EasyOCR (this may take a few minutes) ===")
    
    # Try to install EasyOCR - let it handle PyTorch dependencies
    if run_command("pip install easyocr --no-deps"):
        print("EasyOCR installed without dependencies")
        
        # Install required dependencies manually
        dependencies = [
            "torch",
            "torchvision", 
            "opencv-python",
            "numpy",
            "Pillow",
            "requests",
            "PyYAML"
        ]
        
        for dep in dependencies:
            if not check_module(dep.lower().replace('-', '')):
                print(f"Installing {dep}...")
                run_command(f"pip install {dep}")
    else:
        print("Trying standard EasyOCR installation...")
        if not run_command("pip install easyocr"):
            print("EasyOCR installation failed")
            return False
    
    # Test EasyOCR installation
    print("\n=== Testing EasyOCR Installation ===")
    try:
        import easyocr
        print("✅ EasyOCR successfully installed and imported!")
        return True
    except ImportError as e:
        print(f"❌ EasyOCR import failed: {e}")
        print("The app will run without OCR functionality")
        return False
    except Exception as e:
        print(f"❌ EasyOCR test failed: {e}")
        return False

def install_tesseract_fallback():
    """Install Tesseract as fallback OCR"""
    print("\n=== Installing Tesseract OCR Fallback ===")
    
    if check_module('pytesseract'):
        print("pytesseract already installed")
        return True
    
    if run_command("pip install pytesseract"):
        print("✅ pytesseract installed")
        print("Note: You still need to install Tesseract executable:")
        print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return True
    else:
        print("❌ pytesseract installation failed")
        return False

if __name__ == "__main__":
    print("Starting OCR installation for OSINT Geolocation Tool...")
    
    # Try EasyOCR first
    easyocr_success = install_ocr_dependencies()
    
    # If EasyOCR fails, try Tesseract
    if not easyocr_success:
        print("\nEasyOCR installation failed, trying Tesseract fallback...")
        tesseract_success = install_tesseract_fallback()
        
        if not tesseract_success:
            print("\n❌ Both OCR engines failed to install")
            print("The app will run with EXIF analysis only")
        else:
            print("\n✅ Tesseract OCR installed as fallback")
    else:
        print("\n✅ EasyOCR installation completed successfully!")
    
    print("\n=== Installation Complete ===")
    print("You can now run: python app.py")