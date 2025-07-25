import logging
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response
import threading
import time

logger = logging.getLogger(__name__)

class DashboardServer:
    """
    Web dashboard for the ESP32 security device simulation.
    Provides visualization of security events and device status.
    """
    
    def __init__(self, engine, config=None):
        """
        Initialize the dashboard server.
        
        Args:
            engine: The simulation engine
            config (dict, optional): Configuration parameters
        """
        self.engine = engine
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            'host': '127.0.0.1',
            'port': 5000,
            'debug': False,
            'update_interval': 1.0  # Update interval in seconds
        }
        
        # Apply default config for missing values
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Initialize state
        self.server_thread = None
        self.running = False
        
        # Register with engine
        self.engine.register_component('dashboard', self)
        
        logger.info("Dashboard server initialized")
    
    def initialize(self):
        """Initialize the dashboard server."""
        logger.info("Dashboard server starting")
        self.start_server()
    
    def setup_routes(self):
        """Set up Flask routes."""
        app = self.app
        
        @app.route('/')
        def index():
            """Render the main dashboard page."""
            return render_template('index.html')
        
        @app.route('/api/test', methods=['GET', 'POST'])
        def test():
            """Simple test endpoint to verify API connectivity."""
            if request.method == 'POST':
                logger.info(f"Test POST received. Headers: {dict(request.headers)}")
                logger.info(f"Test POST data: {request.data}")
                try:
                    # Try to parse as JSON
                    if request.is_json:
                        data = request.get_json()
                    else:
                        data = json.loads(request.data.decode('utf-8'))
                    logger.info(f"Test POST parsed JSON: {data}")
                    return jsonify({"status": "success", "received": data})
                except Exception as e:
                    logger.error(f"Error parsing test data: {e}")
                    return jsonify({"status": "error", "message": str(e)})
            else:
                return jsonify({"status": "success", "message": "API test endpoint is working"})
        
        @app.route('/api/status')
        def status():
            """Get current simulation status."""
            return jsonify({
                'status': 'running' if self.engine.running else 'stopped',
                'uptime': (datetime.now() - self.engine.start_time).total_seconds() if self.engine.running else 0,
                'components': list(self.engine.components.keys())
            })
        
        @app.route('/api/network')
        def network():
            """Get network statistics."""
            if 'network' not in self.engine.components:
                return jsonify({'error': 'Network component not found'})
            
            network = self.engine.components['network']
            recent_packets = network.get_recent_packets(20)  # Last 20 packets
            
            # Convert packets to JSON-serializable format
            packets_data = []
            for packet_data in recent_packets:
                # Convert Scapy packet to string representation
                packet_str = str(packet_data['packet'])
                
                # Extract basic information
                packet_info = {
                    'timestamp': packet_data['timestamp'].isoformat(),
                    'summary': packet_str.split('\n')[0],
                    'is_attack': packet_data.get('is_attack', False),
                    'attack_type': packet_data.get('attack_type'),
                    'processed': packet_data.get('processed', False),
                    'firewall_action': packet_data.get('firewall_action'),
                    'firewall_reason': packet_data.get('firewall_reason')
                }
                
                packets_data.append(packet_info)
            
            return jsonify({
                'recent_packets': packets_data,
                'attack_in_progress': network.attack_in_progress,
                'attack_type': network.attack_type
            })
        
        @app.route('/api/security')
        def security():
            """Get security statistics."""
            security_stats = {}
            
            # MAC randomization stats
            if 'mac_randomizer' in self.engine.components:
                mac_randomizer = self.engine.components['mac_randomizer']
                security_stats['mac_address'] = mac_randomizer.get_current_mac()
                security_stats['last_mac_change'] = mac_randomizer.last_change_time
            
            # Firewall stats
            if 'firewall' in self.engine.components:
                firewall = self.engine.components['firewall']
                security_stats['firewall'] = firewall.get_stats()
                
                # Get recent blocked packets
                blocked = firewall.get_blocked_packets(10)
                blocked_data = []
                for packet_data in blocked:
                    packet_str = str(packet_data['packet'])
                    packet_info = {
                        'timestamp': packet_data['timestamp'].isoformat(),
                        'summary': packet_str.split('\n')[0],
                        'reason': packet_data.get('firewall_reason')
                    }
                    blocked_data.append(packet_info)
                
                security_stats['recent_blocked'] = blocked_data
            
            # Encryption stats
            if 'encryption' in self.engine.components:
                encryption = self.engine.components['encryption']
                security_stats['encryption'] = encryption.get_stats()
            
            return jsonify(security_stats)
        
        @app.route('/api/alerts')
        def alerts():
            """Get security alerts."""
            if 'ids' not in self.engine.components:
                return jsonify({'error': 'IDS component not found'})
            
            ids = self.engine.components['ids']
            alerts_data = ids.get_alerts(20)  # Last 20 alerts
            
            # Make alerts JSON-serializable
            for alert in alerts_data:
                alert['timestamp'] = datetime.fromtimestamp(alert['timestamp']).isoformat()
            
            return jsonify({
                'alerts': alerts_data
            })
        
        @app.route('/api/config', methods=['GET', 'POST'])
        def config():
            """Get or update simulation configuration."""
            if request.method == 'POST':
                try:
                    # Log the raw request for debugging
                    logger.info(f"Received POST to /api/config. Headers: {dict(request.headers)}")
                    logger.info(f"Raw request data: {request.data}")

                    # Extract the data from the request
                    config_data = None
                    
                    # Try multiple parsing methods
                    if request.is_json:
                        config_data = request.get_json(force=True)
                        logger.info("Parsed request as JSON using get_json()")
                    elif request.form:
                        # Form data
                        config_data = {k: v for k, v in request.form.items()}
                        logger.info("Parsed request as form data")
                    elif request.data:
                        # Raw data - try to parse as JSON
                        try:
                            config_data = json.loads(request.data.decode('utf-8'))
                            logger.info("Parsed request data as JSON manually")
                        except:
                            # If not valid JSON, try to parse as a query string
                            try:
                                from urllib.parse import parse_qs
                                parsed = parse_qs(request.data.decode('utf-8'))
                                config_data = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                                logger.info("Parsed request as query string")
                            except:
                                logger.error("Could not parse request data in any format")
                                return jsonify({'status': 'error', 'message': 'Invalid request format'}), 400
                    
                    if not config_data:
                        logger.error("No config data could be extracted from the request")
                        return jsonify({'status': 'error', 'message': 'No configuration data provided'}), 400
                    
                    logger.info(f"Parsed configuration update: {config_data}")
                    
                    # Toggle firewall policy if requested
                    if 'firewall' in config_data and isinstance(config_data['firewall'], dict) and 'default_policy' in config_data['firewall'] and 'firewall' in self.engine.components:
                        firewall = self.engine.components['firewall']
                        new_policy = config_data['firewall']['default_policy']
                        if new_policy in ['allow', 'block']:
                            firewall.config['default_policy'] = new_policy
                            logger.info(f"Updated firewall default policy to: {new_policy}")
                    
                    # Update firewall rules if provided
                    if 'firewall_rules' in config_data and 'firewall' in self.engine.components:
                        firewall = self.engine.components['firewall']
                        
                        # Replace rules
                        firewall.config['rules'] = config_data['firewall_rules']
                        logger.info(f"Updated firewall rules: {len(firewall.config['rules'])} rules")
                    
                    # Toggle IDS if requested
                    if 'ids' in config_data and isinstance(config_data['ids'], dict) and 'ids' in self.engine.components:
                        ids = self.engine.components['ids']
                        if 'signature_detection' in config_data['ids']:
                            ids.config['signature_detection'] = config_data['ids']['signature_detection']
                            logger.info(f"Updated IDS signature detection to: {ids.config['signature_detection']}")
                        if 'anomaly_detection' in config_data['ids']:
                            ids.config['anomaly_detection'] = config_data['ids']['anomaly_detection']
                            logger.info(f"Updated IDS anomaly detection to: {ids.config['anomaly_detection']}")
                    
                    # Rotate MAC address if requested
                    if config_data.get('rotate_mac', False) and 'mac_randomizer' in self.engine.components:
                        mac_randomizer = self.engine.components['mac_randomizer']
                        new_mac = mac_randomizer.randomize_now()
                        logger.info(f"MAC address manually rotated to: {new_mac}")
                    
                    # Clear alerts if requested
                    if config_data.get('clear_alerts', False) and 'ids' in self.engine.components:
                        ids = self.engine.components['ids']
                        ids.clear_alerts()
                        logger.info("Security alerts cleared")
                    
                    return jsonify({'status': 'success'})
                except Exception as e:
                    logger.error(f"Error processing configuration update: {e}", exc_info=True)
                    return jsonify({'status': 'error', 'message': str(e)}), 400
            else:
                # Return current configuration
                config_data = {}
                
                # Firewall configuration
                if 'firewall' in self.engine.components:
                    firewall = self.engine.components['firewall']
                    config_data['firewall'] = {
                        'rules': firewall.config['rules'],
                        'default_policy': firewall.config['default_policy'],
                        'rate_limiting': firewall.config['rate_limiting']
                    }
                
                # MAC randomization configuration
                if 'mac_randomizer' in self.engine.components:
                    mac_randomizer = self.engine.components['mac_randomizer']
                    config_data['mac_randomizer'] = {
                        'randomization_interval': mac_randomizer.config['randomization_interval']
                    }
                
                # IDS configuration
                if 'ids' in self.engine.components:
                    ids = self.engine.components['ids']
                    config_data['ids'] = {
                        'signature_detection': ids.config['signature_detection'],
                        'anomaly_detection': ids.config['anomaly_detection'],
                        'alert_threshold': ids.config['alert_threshold']
                    }
                
                return jsonify(config_data)
        
        # Add CORS headers to all responses
        @app.after_request
        def add_cors_headers(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        # Handle OPTIONS requests
        @app.route('/api/config', methods=['OPTIONS'])
        def options():
            return Response('', 204)
    
    def start_server(self):
        """Start the Flask server in a separate thread."""
        if self.running:
            logger.warning("Dashboard server is already running")
            return
        
        def run_server():
            self.app.run(
                host=self.config['host'],
                port=self.config['port'],
                debug=self.config['debug'],
                use_reloader=False  # Disable reloader in thread
            )
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True
        
        logger.info(f"Dashboard server started at http://{self.config['host']}:{self.config['port']}/")
    
    def update(self, cycle):
        """
        Update the dashboard for the current cycle.
        
        Args:
            cycle (int): Current simulation cycle
        """
        # No update required, the dashboard will pull data from the API
        pass
    
    def shutdown(self):
        """Shut down the dashboard server."""
        logger.info("Dashboard server shutting down")
        # No explicit shutdown required for Flask in a thread
        self.running = False
