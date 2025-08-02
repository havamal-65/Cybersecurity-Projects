from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename

# Enable python-magic for better file validation
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
from datetime import datetime
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///osint_geolocation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
# Temporarily disable CSRF for testing - re-enable for production
# csrf = CSRFProtect(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Database Models
class Investigation(db.Model):
    __tablename__ = 'investigations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    images = db.relationship('Image', backref='investigation', lazy='dynamic', cascade='all, delete-orphan')

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investigation_id = db.Column(db.String(36), db.ForeignKey('investigations.id'))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    upload_path = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(50))
    exif_data = db.Column(db.Text)  # JSON string
    processing_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    results = db.relationship('GeolocationResult', backref='image', lazy='dynamic', cascade='all, delete-orphan')

class GeolocationResult(db.Model):
    __tablename__ = 'geolocation_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = db.Column(db.String(36), db.ForeignKey('images.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    accuracy_meters = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)
    method_used = db.Column(db.String(100))
    source_api = db.Column(db.String(50))
    raw_response = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# File validation constants
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/webp'
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file):
    """Validate uploaded file for security and format compliance"""
    try:
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided"
        
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > MAX_FILE_SIZE:
            return False, "File too large (max 10MB)"
        
        if size == 0:
            return False, "Empty file"
        
        # Check extension
        filename = secure_filename(file.filename)
        if '.' not in filename:
            return False, "No file extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Check MIME type
        if MAGIC_AVAILABLE:
            file_content = file.read(1024)
            file.seek(0)
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
            except:
                mime_type = file.content_type
        else:
            # Fallback to browser-provided content type
            mime_type = file.content_type
        
        if mime_type not in ALLOWED_MIME_TYPES:
            return False, f"Invalid file type: {mime_type}"
        
        # Calculate hash
        file_hash = hashlib.sha256()
        while True:
            chunk = file.read(4096)
            if not chunk:
                break
            file_hash.update(chunk)
        file.seek(0)
        
        return True, {
            'filename': filename,
            'original_filename': file.filename,
            'size': size,
            'mime_type': mime_type,
            'hash': file_hash.hexdigest()
        }
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
@limiter.limit("10 per minute")
def upload_image():
    """Upload and validate image file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate file
        is_valid, result = validate_file(file)
        if not is_valid:
            return jsonify({'error': result}), 400
        
        # Generate secure filename
        file_id = str(uuid.uuid4())
        ext = result['filename'].rsplit('.', 1)[1].lower()
        secure_name = f"{file_id}.{ext}"
        
        # Save file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        file.save(upload_path)
        
        # Create investigation if not provided
        investigation_name = request.form.get('investigation_name', f'Analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        investigation = Investigation(name=investigation_name)
        db.session.add(investigation)
        db.session.flush()  # Get the ID
        
        # Create image record
        image = Image(
            investigation_id=investigation.id,
            filename=secure_name,
            original_filename=result['original_filename'],
            file_hash=result['hash'],
            upload_path=upload_path,
            file_size=result['size'],
            mime_type=result['mime_type'],
            processing_status='uploaded'
        )
        
        db.session.add(image)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'image_id': image.id,
            'investigation_id': investigation.id,
            'filename': result['original_filename'],
            'size': result['size'],
            'status': 'uploaded',
            'message': 'File uploaded successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/analyze/<image_id>', methods=['POST'])
@limiter.limit("5 per minute")
def analyze_image(image_id):
    """Analyze uploaded image for geolocation data"""
    try:
        print(f"DEBUG: Analyzing image ID: {image_id}")
        
        # Use atomic transaction with row locking to prevent race conditions
        with db.session.begin():
            image = Image.query.with_for_update().get(image_id)
            
            if not image:
                print(f"DEBUG: Image not found: {image_id}")
                return jsonify({'error': 'Image not found'}), 404
            
            if image.processing_status == 'processing':
                print(f"DEBUG: Image already processing: {image_id}")
                return jsonify({'error': 'Analysis already in progress'}), 400
            
            # Update status atomically
            image.processing_status = 'processing'
        
        # Import analysis services here to avoid circular imports
        try:
            from services.exif_extractor import extract_exif_data
            from services.vision_service import analyze_image_with_vision
            from services.confidence_scorer import ConfidenceScorer
            print("DEBUG: All services imported successfully")
        except ImportError as e:
            print(f"DEBUG: Import error: {e}")
            return jsonify({'error': f'Service import failed: {str(e)}'}), 500
        
        results = []
        
        # Extract EXIF data
        try:
            print(f"DEBUG: Extracting EXIF from: {image.upload_path}")
            exif_data = extract_exif_data(image.upload_path)
            print(f"DEBUG: EXIF extraction result: {type(exif_data)}")
            image.exif_data = json.dumps(exif_data) if exif_data else None
            
            # Check for GPS data in EXIF
            if exif_data and exif_data.get('gps_coordinates'):
                print("DEBUG: GPS coordinates found in EXIF")
                gps = exif_data['gps_coordinates']
                result = GeolocationResult(
                    image_id=image.id,
                    latitude=gps['latitude'],
                    longitude=gps['longitude'],
                    confidence_score=0.95,  # High confidence for GPS data
                    method_used='EXIF_GPS',
                    source_api='exif',
                    raw_response=json.dumps(exif_data)
                )
                db.session.add(result)
                results.append(result)
            else:
                print("DEBUG: No GPS coordinates found in EXIF")
        except Exception as e:
            print(f"DEBUG: EXIF extraction error: {e}")
            # Continue with other analysis methods even if EXIF fails
        
        # Vision Analysis for comprehensive scene understanding and location intelligence
        print("DEBUG: Starting vision analysis...")
        try:
            vision_results = analyze_image_with_vision(image.upload_path)
            print(f"DEBUG: Vision analysis completed - Success: {vision_results.get('success', False)}")
        except Exception as vision_error:
            print(f"DEBUG: Vision analysis error: {vision_error}")
            vision_results = {'success': False, 'error': str(vision_error)}
        
        if vision_results and vision_results.get('success'):
            # Store vision analysis data for display
            existing_data = json.loads(image.exif_data) if image.exif_data else {}
            existing_data['vision_results'] = vision_results
            image.exif_data = json.dumps(existing_data)
            
            # Process location candidates from intelligent analysis
            location_candidates = vision_results.get('location_candidates', [])
            for candidate in location_candidates:
                # Create GeolocationResult for each location candidate
                result = GeolocationResult(
                    image_id=image.id,
                    latitude=candidate.latitude,
                    longitude=candidate.longitude,
                    confidence_score=candidate.confidence,
                    method_used='location_intelligence',
                    source_api='comprehensive_analysis',
                    accuracy_meters=candidate.accuracy_meters,
                    raw_response=json.dumps({
                        'address': candidate.address,
                        'city': candidate.city,
                        'state': candidate.state,
                        'country': candidate.country,
                        'matched_clues': [{'type': c.clue_type, 'text': c.text, 'confidence': c.confidence} for c in candidate.matched_clues],
                        'source': candidate.source
                    })
                )
                db.session.add(result)
                results.append(result)
                print(f"Added location candidate: {candidate.city}, {candidate.state} ({candidate.confidence:.2f} confidence)")
            
            # Process geographic indicators from vision analysis (fallback for non-geocoded indicators)
            geographic_indicators = vision_results.get('geographic_indicators', [])
            for indicator in geographic_indicators:
                if indicator.get('type') in ['known_location', 'country_indicators']:
                    # Only add if we don't already have location candidates
                    if not location_candidates:
                        result = GeolocationResult(
                            image_id=image.id,
                            latitude=None,  # Geographic indicator without coordinates
                            longitude=None,
                            confidence_score=indicator.get('confidence', 0.6),
                            method_used='vision_geographic_text',
                            source_api='vision_analysis',
                            raw_response=json.dumps(indicator)
                        )
                        db.session.add(result)
                        results.append(result)
        
        
        # Calculate overall confidence
        overall_confidence = ConfidenceScorer.calculate_overall_confidence(results)
        
        # Update processing status
        image.processing_status = 'completed' if results else 'no_location_found'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'image_id': image.id,
            'status': image.processing_status,
            'results_count': len(results),
            'overall_confidence': overall_confidence,
            'message': f'Analysis completed. Found {len(results)} location indicators.'
        })
        
    except Exception as e:
        print(f"DEBUG: Analysis error: {e}")
        try:
            if 'image' in locals():
                image.processing_status = 'error'
                db.session.commit()
        except:
            pass  # Don't fail on cleanup errors
        
        # Provide helpful error messages without exposing internal details
        error_msg = 'Analysis failed'
        if 'import' in str(e).lower():
            error_msg = 'Required analysis services are not available'
        elif 'file' in str(e).lower():
            error_msg = 'Could not process the uploaded file'
        elif 'database' in str(e).lower():
            error_msg = 'Database error occurred'
        
        return jsonify({
            'error': error_msg,
            'details': str(e) if app.debug else 'Please try again or contact support',
            'retry_possible': True
        }), 500

@app.route('/api/results/<image_id>')
def get_results(image_id):
    """Get analysis results for an image"""
    try:
        print(f"DEBUG: Getting results for image ID: {image_id}")
        image = Image.query.get(image_id)
        if not image:
            print(f"DEBUG: Image not found for results: {image_id}")
            return jsonify({'error': 'Image not found'}), 404
            
        results = GeolocationResult.query.filter_by(image_id=image_id).all()
        print(f"DEBUG: Found {len(results)} results")
        
        # Parse EXIF data
        exif_data = None
        if image.exif_data:
            try:
                exif_data = json.loads(image.exif_data)
            except:
                pass
        
        # Format results
        formatted_results = []
        for result in results:
            raw_data = None
            if result.raw_response:
                try:
                    raw_data = json.loads(result.raw_response)
                except:
                    pass
            
            formatted_results.append({
                'id': result.id,
                'latitude': result.latitude,
                'longitude': result.longitude,
                'confidence': result.confidence_score,
                'method': result.method_used,
                'source': result.source_api,
                'accuracy_meters': result.accuracy_meters,
                'raw_data': raw_data,
                'created_at': result.created_at.isoformat()
            })
        
        # Calculate best estimate
        best_result = None
        if formatted_results:
            best_result = max(formatted_results, key=lambda x: x['confidence'] or 0)
        
        response_data = {
            'success': True,
            'image': {
                'id': image.id,
                'filename': image.original_filename,
                'status': image.processing_status,
                'upload_date': image.created_at.isoformat()
            },
            'exif_data': exif_data,
            'results': formatted_results,
            'best_estimate': best_result,
            'total_results': len(formatted_results)
        }
        print(f"DEBUG: Returning results: {len(formatted_results)} results found")
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get results: {str(e)}'}), 500

@app.route('/api/status/<image_id>')
def get_status(image_id):
    """Get processing status for an image"""
    try:
        print(f"DEBUG: Getting status for image ID: {image_id}")
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        return jsonify({
            'success': True,
            'status': image.processing_status,
            'progress': 100 if image.processing_status == 'completed' else 50
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500

@app.route('/api/report/<image_id>')
def generate_report(image_id):
    """Generate a comprehensive markdown report for an image analysis"""
    try:
        print(f"DEBUG: Generating report for image ID: {image_id}")
        
        # Get image data
        image = Image.query.get(image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get analysis results
        results = GeolocationResult.query.filter_by(image_id=image_id).all()
        
        # Parse EXIF data
        exif_data = None
        if image.exif_data:
            try:
                exif_data = json.loads(image.exif_data)
            except:
                pass
        
        # Import report generator
        from services.report_generator import OSINTReportGenerator
        
        # Prepare data for report generation
        image_data = {
            'id': image.id,
            'filename': image.original_filename,
            'file_size': image.file_size,
            'upload_date': image.created_at.isoformat()
        }
        
        # Format results for report generator
        formatted_results = []
        for result in results:
            raw_data = None
            if result.raw_response:
                try:
                    raw_data = json.loads(result.raw_response)
                except:
                    pass
            
            formatted_results.append({
                'id': result.id,
                'latitude': result.latitude,
                'longitude': result.longitude,
                'confidence_score': result.confidence_score,
                'method_used': result.method_used,
                'source_api': result.source_api,
                'accuracy_meters': result.accuracy_meters,
                'raw_response': result.raw_response,
                'created_at': result.created_at.isoformat()
            })
        
        # Add MiniCPM-V comprehensive analysis from vision results if available
        if exif_data and 'vision_results' in exif_data:
            vision_data = exif_data['vision_results']
            if vision_data.get('method') == 'ollama_minicpm_comprehensive':
                # Add the comprehensive analysis as a special result entry
                formatted_results.append({
                    'id': 'minicpm_analysis',
                    'latitude': None,
                    'longitude': None,
                    'confidence_score': vision_data.get('average_confidence', 95) / 100.0,
                    'method_used': 'ollama_minicpm_comprehensive',
                    'source_api': 'visual_analysis',
                    'accuracy_meters': None,
                    'raw_response': json.dumps(vision_data),
                    'created_at': image.created_at.isoformat()
                })
        
        # Generate report
        generator = OSINTReportGenerator()
        markdown_report = generator.generate_full_report(
            image_data=image_data,
            analysis_results=formatted_results,
            exif_data=exif_data
        )
        
        # Return based on requested format
        format_type = request.args.get('format', 'json')
        
        if format_type == 'markdown':
            return markdown_report, 200, {'Content-Type': 'text/markdown; charset=utf-8'}
        elif format_type == 'html':
            # Convert markdown to HTML (basic implementation)
            html_report = markdown_report.replace('\n', '<br>\n')
            html_report = f"<!DOCTYPE html><html><head><title>OSINT Report</title><meta charset='utf-8'></head><body style='font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;'><pre style='white-space: pre-wrap;'>{html_report}</pre></body></html>"
            return html_report, 200, {'Content-Type': 'text/html; charset=utf-8'}
        else:
            # Default JSON response with markdown content
            return jsonify({
                'success': True,
                'markdown_report': markdown_report,
                'image_id': image_id,
                'analysis_date': generator.generated_timestamp.isoformat(),
                'results_count': len(formatted_results)
            })
        
    except Exception as e:
        print(f"DEBUG: Report generation error: {e}")
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files (with security checks)"""
    # Basic security check - only serve files from our upload directory
    if not filename or '..' in filename or '/' in filename:
        return "Invalid filename", 400
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Database session cleanup
@app.teardown_appcontext
def cleanup_db_session(error):
    """Ensure database session is properly cleaned up after each request"""
    if error:
        db.session.rollback()
    db.session.remove()

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)