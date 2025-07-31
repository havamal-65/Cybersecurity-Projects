"""
Real EXIF data extraction service
Extracts GPS coordinates and metadata from image files
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from datetime import datetime
import os

def extract_exif_data(image_path):
    """
    Extract comprehensive EXIF metadata from image file
    Returns dict with GPS coordinates and camera information
    """
    try:
        if not os.path.exists(image_path):
            return {'error': 'Image file not found'}
        
        # Open image
        with Image.open(image_path) as img:
            exifdata = img.getexif()
            
            if not exifdata:
                return {'message': 'No EXIF data found'}
            
            metadata = {}
            
            # Extract standard EXIF tags
            for tag_id, value in exifdata.items():
                tag = TAGS.get(tag_id, tag_id)
                
                # Convert bytes to string for text fields
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                
                metadata[tag] = value
            
            # Extract GPS data
            gps_data = _extract_gps_coordinates(exifdata)
            if gps_data:
                metadata['gps_coordinates'] = gps_data
                metadata['has_gps'] = True
            else:
                metadata['has_gps'] = False
            
            # Extract camera information
            camera_info = _extract_camera_info(metadata)
            if camera_info:
                metadata['camera_info'] = camera_info
            
            # Extract timestamp information
            timestamp_info = _extract_timestamps(metadata)
            if timestamp_info:
                metadata['timestamps'] = timestamp_info
            
            return metadata
            
    except Exception as e:
        return {'error': f'EXIF extraction failed: {str(e)}'}

def _extract_gps_coordinates(exifdata):
    """Extract and convert GPS coordinates to decimal degrees"""
    try:
        gps_info = {}
        
        # Get GPS info from EXIF
        if hasattr(exifdata, 'get_ifd') and piexif.GPS.GPSLatitude in exifdata.get_ifd(piexif.GPSIFD):
            # Use piexif for more reliable GPS extraction
            gps_ifd = exifdata.get_ifd(piexif.GPSIFD)
            
            if piexif.GPS.GPSLatitude in gps_ifd and piexif.GPS.GPSLongitude in gps_ifd:
                # Extract latitude
                lat_dms = gps_ifd[piexif.GPS.GPSLatitude]
                lat_ref = gps_ifd.get(piexif.GPS.GPSLatitudeRef, b'N').decode()
                latitude = _dms_to_decimal(lat_dms, lat_ref)
                
                # Extract longitude
                lon_dms = gps_ifd[piexif.GPS.GPSLongitude]
                lon_ref = gps_ifd.get(piexif.GPS.GPSLongitudeRef, b'E').decode()
                longitude = _dms_to_decimal(lon_dms, lon_ref)
                
                gps_info = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'lat_ref': lat_ref,
                    'lon_ref': lon_ref
                }
                
                # Extract altitude if available
                if piexif.GPS.GPSAltitude in gps_ifd:
                    altitude_rational = gps_ifd[piexif.GPS.GPSAltitude]
                    altitude = altitude_rational[0] / altitude_rational[1] if altitude_rational[1] != 0 else 0
                    altitude_ref = gps_ifd.get(piexif.GPS.GPSAltitudeRef, 0)
                    if altitude_ref == 1:  # Below sea level
                        altitude = -altitude
                    gps_info['altitude'] = altitude
                
                # Extract GPS timestamp if available
                if piexif.GPS.GPSTimeStamp in gps_ifd and piexif.GPS.GPSDateStamp in gps_ifd:
                    time_stamp = gps_ifd[piexif.GPS.GPSTimeStamp]
                    date_stamp = gps_ifd[piexif.GPS.GPSDateStamp].decode()
                    
                    hours = time_stamp[0][0] / time_stamp[0][1] if time_stamp[0][1] != 0 else 0
                    minutes = time_stamp[1][0] / time_stamp[1][1] if time_stamp[1][1] != 0 else 0
                    seconds = time_stamp[2][0] / time_stamp[2][1] if time_stamp[2][1] != 0 else 0
                    
                    gps_info['timestamp'] = f"{date_stamp} {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d} UTC"
        
        # Fallback: try standard EXIF GPS extraction
        elif 'GPSInfo' in exifdata:
            gps_raw = exifdata['GPSInfo']
            
            # Convert GPS tags
            gps_data = {}
            for key, val in gps_raw.items():
                decode = GPSTAGS.get(key, key)
                gps_data[decode] = val
            
            # Extract coordinates if available
            if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                lat = _convert_to_degrees(gps_data['GPSLatitude'])
                lon = _convert_to_degrees(gps_data['GPSLongitude'])
                
                # Apply hemisphere corrections
                if gps_data.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                if gps_data.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                
                gps_info = {
                    'latitude': lat,
                    'longitude': lon,
                    'lat_ref': gps_data.get('GPSLatitudeRef', 'N'),
                    'lon_ref': gps_data.get('GPSLongitudeRef', 'E')
                }
        
        return gps_info if gps_info else None
        
    except Exception as e:
        print(f"GPS extraction error: {e}")
        return None

def _dms_to_decimal(dms_tuple, ref):
    """Convert degrees, minutes, seconds to decimal degrees"""
    try:
        degrees = dms_tuple[0][0] / dms_tuple[0][1] if dms_tuple[0][1] != 0 else 0
        minutes = dms_tuple[1][0] / dms_tuple[1][1] if dms_tuple[1][1] != 0 else 0
        seconds = dms_tuple[2][0] / dms_tuple[2][1] if dms_tuple[2][1] != 0 else 0
        
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    except:
        return 0

def _convert_to_degrees(value):
    """Convert GPS coordinates to decimal degrees (fallback method)"""
    try:
        d, m, s = value
        return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)
    except:
        return 0

def _extract_camera_info(metadata):
    """Extract camera and shooting information"""
    camera_info = {}
    
    # Camera make and model
    if 'Make' in metadata:
        camera_info['make'] = metadata['Make']
    if 'Model' in metadata:
        camera_info['model'] = metadata['Model']
    if 'Software' in metadata:
        camera_info['software'] = metadata['Software']
    
    # Camera settings
    if 'ISO' in metadata or 'ISOSpeedRatings' in metadata:
        camera_info['iso'] = metadata.get('ISO') or metadata.get('ISOSpeedRatings')
    if 'FNumber' in metadata:
        camera_info['aperture'] = f"f/{metadata['FNumber']}"
    if 'ExposureTime' in metadata:
        camera_info['shutter_speed'] = metadata['ExposureTime']
    if 'FocalLength' in metadata:
        camera_info['focal_length'] = f"{metadata['FocalLength']}mm"
    
    # Flash information
    if 'Flash' in metadata:
        camera_info['flash'] = metadata['Flash']
    
    return camera_info if camera_info else None

def _extract_timestamps(metadata):
    """Extract various timestamp information"""
    timestamps = {}
    
    # Original date/time
    if 'DateTime' in metadata:
        timestamps['datetime'] = metadata['DateTime']
    if 'DateTimeOriginal' in metadata:
        timestamps['datetime_original'] = metadata['DateTimeOriginal']
    if 'DateTimeDigitized' in metadata:
        timestamps['datetime_digitized'] = metadata['DateTimeDigitized']
    
    # Try to parse timestamps
    for key, value in timestamps.items():
        try:
            if isinstance(value, str):
                # Parse EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
                parsed = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                timestamps[f"{key}_parsed"] = parsed.isoformat()
        except:
            continue
    
    return timestamps if timestamps else None

def get_image_dimensions(image_path):
    """Get image dimensions and basic info"""
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': os.path.getsize(image_path)
            }
    except Exception as e:
        return {'error': f'Could not get image info: {str(e)}'}