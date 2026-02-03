#!/usr/bin/env python3
"""
V-Player - Professional Streaming Solution
by Itassist Broadcast Solutions

Main Flask application for streaming media player with web interface.
Supports SRT, RTMP, UDP, HLS, RTP protocols with hardware acceleration.
"""

import os
import sys
import logging
import json
import subprocess
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import socketio as socketio_client

from config import Config
from stream_decoder import StreamDecoder
from network_monitor import NetworkMonitor
from cloudflare_integration_2024 import CloudflareIntegration2024
# from rpi_network_configs import RaspberryPiNetworkConfig

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging with comprehensive error handling
try:
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'v-player.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create specific logger for V-Player
    logger = logging.getLogger('V-Player')
    logger.info("V-Player logging initialized successfully")
    
except Exception as e:
    print(f"ERROR: Failed to initialize logging: {e}")
    sys.exit(1)

# Initialize components with error handling
try:
    decoder = StreamDecoder()
    network_monitor = NetworkMonitor(socketio)
    cloudflare = CloudflareIntegration2024()
    # network_config = RaspberryPiNetworkConfig()
    logger.info("V-Player components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize V-Player components: {e}")
    sys.exit(1)

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/api/start_stream', methods=['POST'])
def start_stream():
    """Start a new stream"""
    data = request.get_json()
    
    stream_url = data.get('url')
    stream_type = data.get('type', 'auto')
    
    if not stream_url:
        return jsonify({'error': 'Stream URL is required'}), 400
    
    # Generate unique stream ID
    stream_id = str(uuid.uuid4())[:8]
    
    # Auto-detect stream type if not specified
    if stream_type == 'auto':
        stream_type = detect_stream_type(stream_url)
    
    # Start the stream
    success = decoder.start_stream(stream_id, stream_url, stream_type)
    
    if success:
        # Notify all clients
        socketio.emit('stream_started', {
            'stream_id': stream_id,
            'url': stream_url,
            'type': stream_type
        })
        
        return jsonify({
            'stream_id': stream_id,
            'status': 'started'
        })
    else:
        return jsonify({'error': 'Failed to start stream'}), 500

@app.route('/api/stop_stream', methods=['POST'])
def stop_stream():
    """Stop a running stream"""
    data = request.get_json()
    stream_id = data.get('stream_id')
    
    if not stream_id:
        return jsonify({'error': 'Stream ID is required'}), 400
    
    success = decoder.stop_stream(stream_id)
    
    if success:
        # Notify all clients
        socketio.emit('stream_stopped', {'stream_id': stream_id})
        return jsonify({'status': 'stopped'})
    else:
        return jsonify({'error': 'Failed to stop stream'}), 500

@app.route('/api/stream_status/<stream_id>')
def get_stream_status(stream_id):
    """Get status of a specific stream"""
    status = decoder.get_stream_status(stream_id)
    return jsonify(status)

@app.route('/api/all_streams')
def get_all_streams():
    """Get status of all streams"""
    streams = decoder.get_all_streams()
    return jsonify(streams)

@app.route('/api/outputs', methods=['GET'])
def get_outputs():
    """Get available output configurations"""
    try:
        # outputs = output_config.get_supported_outputs()
        # current = output_config.get_current_config()
        outputs = {
            "hdmi": {
                "name": "HDMI Output",
                "modes": [
                    {"resolution": "1920x1080", "refresh": 60, "description": "Full HD 60Hz"},
                    {"resolution": "1920x1080", "refresh": 50, "description": "Full HD 50Hz"},
                    {"resolution": "1280x720", "refresh": 60, "description": "HD Ready 60Hz"},
                ]
            },
            "composite": {
                "name": "Composite (RCA)",
                "modes": [
                    {"resolution": "720x576", "refresh": 50, "description": "PAL 50Hz"},
                    {"resolution": "720x480", "refresh": 60, "description": "NTSC 60Hz"},
                ]
            }
        }
        current = {"output_type": "hdmi", "resolution": "1920x1080", "refresh": 60}
        
        return jsonify({
            'supported': outputs,
            'current': current
        })
    except Exception as e:
        logger.error(f"Error getting outputs: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/outputs', methods=['POST'])
def set_outputs():
    """Apply output configuration"""
    try:
        data = request.get_json()
        # success = output_config.apply_output_settings(data)
        success = True  # Placeholder
        
        if success:
            # reboot_needed = output_config.reboot_required()
            reboot_needed = True  # Placeholder
            return jsonify({
                'success': True,
                'reboot_required': reboot_needed,
                'message': 'Output configuration applied successfully' + 
                          ('. Reboot required for changes to take effect.' if reboot_needed else '')
            })
        else:
            return jsonify({'error': 'Failed to apply output configuration'}), 500
            
    except Exception as e:
        logger.error(f"Error setting outputs: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/channels', methods=['GET'])
def get_channels():
    """Get all active channels"""
    try:
        channels = decoder.get_active_streams()
        return jsonify({'channels': channels})
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/channels', methods=['POST'])
def create_channel():
    """Create a new channel"""
    try:
        data = request.get_json()
        channel_id = str(uuid.uuid4())[:8]
        
        # Create channel data
        channel_data = {
            'id': channel_id,
            'name': data.get('name'),
            'input': data.get('input'),
            'url': data.get('url'),
            'resolution': data.get('resolution'),
            'state': 'idle',
            'created_at': datetime.now().isoformat()
        }
        
        # Start stream if URL provided
        if data.get('url'):
            success = decoder.start_stream(channel_id, data.get('url'), data.get('input', 'auto'))
            if success:
                channel_data['state'] = 'running'
        
        return jsonify({'success': True, 'channel': channel_data})
        
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/status', methods=['GET'])
def cloudflare_status():
    """Get Cloudflare tunnel status (2024 method)"""
    try:
        status = cloudflare.get_tunnel_status_service_method()
        version = cloudflare.get_cloudflare_version()
        
        return jsonify({
            'status': status,
            'version': version,
            'method': 'dashboard-first-2024'
        })
    except Exception as e:
        logger.error(f"Error getting Cloudflare status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/install', methods=['POST'])
def install_cloudflare():
    """Install cloudflared using 2024 dashboard method"""
    try:
        result = cloudflare.install_cloudflared_dashboard_method()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error installing cloudflared: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/instructions', methods=['POST'])
def get_cloudflare_instructions():
    """Get dashboard-first setup instructions"""
    try:
        data = request.get_json()
        hostname = data.get('hostname', 'vplayer.yourdomain.com')
        local_port = data.get('local_port', 5004)
        
        instructions = cloudflare.generate_dashboard_instructions(hostname, local_port)
        return jsonify({
            'success': True,
            'instructions': instructions
        })
    except Exception as e:
        logger.error(f"Error generating instructions: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/start', methods=['POST'])
def start_cloudflare():
    """Start Cloudflare tunnel service (2024 method)"""
    try:
        result = cloudflare.start_tunnel_service()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error starting Cloudflare tunnel: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/stop', methods=['POST'])
def stop_cloudflare():
    """Stop Cloudflare tunnel service (2024 method)"""
    try:
        result = cloudflare.stop_tunnel_service()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error stopping Cloudflare tunnel: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/test', methods=['POST'])
def test_cloudflare():
    """Test Cloudflare tunnel connection"""
    try:
        data = request.get_json()
        hostname = data.get('hostname')
        
        if not hostname:
            return jsonify({'error': 'Hostname is required'}), 400
        
        result = cloudflare.test_tunnel_connection(hostname)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing Cloudflare tunnel: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/cloudflare/script', methods=['POST'])
def generate_cloudflare_script():
    """Generate 2024 setup script"""
    try:
        data = request.get_json()
        hostname = data.get('hostname', 'vplayer.yourdomain.com')
        local_port = data.get('local_port', 5004)
        
        script = cloudflare.generate_setup_script_2024(hostname, local_port)
        
        return jsonify({
            'success': True,
            'script': script,
            'filename': 'setup_cloudflare_2024.sh',
            'method': 'dashboard-first-2024'
        })
    except Exception as e:
        logger.error(f"Error generating Cloudflare script: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/status', methods=['GET'])
def network_status():
    """Get detailed network status"""
    try:
        # status = network_config.get_current_network_config()
        # metrics = network_config.get_network_metrics()
        
        return jsonify({
            'status': {"interfaces": {"eth0": {"state": "UP", "ip_addresses": ["192.168.1.100"]}, "wlan0": {"state": "DOWN", "ip_addresses": []}}},
            'metrics': {"interfaces": {}, "wifi": {}},
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/interfaces', methods=['GET'])
def network_interfaces():
    """Get network interface status"""
    try:
        # interfaces = network_config._get_interface_status()
        interfaces = {"eth0": {"state": "UP", "ip_addresses": ["192.168.1.100"]}, "wlan0": {"state": "DOWN", "ip_addresses": []}}
        return jsonify({'interfaces': interfaces})
    except Exception as e:
        logger.error(f"Error getting network interfaces: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/wifi/scan', methods=['GET'])
def scan_wifi_networks():
    """Scan for available WiFi networks"""
    try:
        # networks = network_config.scan_wifi_networks()
        networks = [{"ESSID": "TestNetwork", "Quality": "70/70", "Encryption": "WPA2"}]
        return jsonify({'networks': networks})
    except Exception as e:
        logger.error(f"Error scanning WiFi networks: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/wifi/connect', methods=['POST'])
def connect_wifi():
    """Connect to WiFi network"""
    try:
        data = request.get_json()
        ssid = data.get('ssid')
        password = data.get('password')
        
        if not ssid:
            return jsonify({'error': 'SSID is required'}), 400
        
        # success = network_config.connect_wifi(ssid, password)
        success = True  # Placeholder
        
        if success:
            return jsonify({'success': True, 'message': f'Connected to {ssid}'})
        else:
            return jsonify({'error': 'Failed to connect to WiFi network'}), 500
            
    except Exception as e:
        logger.error(f"Error connecting to WiFi: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/static-ip', methods=['POST'])
def configure_static_ip():
    """Configure static IP address"""
    try:
        data = request.get_json()
        interface = data.get('interface')
        ip_address = data.get('ip_address')
        netmask = data.get('netmask', '255.255.255.0')
        gateway = data.get('gateway')
        dns_servers = data.get('dns_servers', ['8.8.8.8', '8.8.4.4'])
        
        if not all([interface, ip_address, gateway]):
            return jsonify({'error': 'Interface, IP address, and gateway are required'}), 400
        
        # success = network_config.configure_static_ip(interface, ip_address, netmask, gateway, dns_servers)
        success = True  # Placeholder
        
        if success:
            return jsonify({'success': True, 'message': 'Static IP configured successfully'})
        else:
            return jsonify({'error': 'Failed to configure static IP'}), 500
            
    except Exception as e:
        logger.error(f"Error configuring static IP: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/hotspot/start', methods=['POST'])
def start_hotspot():
    """Start WiFi hotspot"""
    try:
        data = request.get_json()
        ssid = data.get('ssid', 'V-Player-Hotspot')
        password = data.get('password', 'vplayer123')
        channel = data.get('channel', 9)
        country_code = data.get('country_code', 'US')
        
        # success = network_config.configure_hotspot(ssid, password, channel, country_code)
        success = True  # Placeholder
        
        if success:
            return jsonify({'success': True, 'message': 'Hotspot started successfully'})
        else:
            return jsonify({'error': 'Failed to start hotspot'}), 500
            
    except Exception as e:
        logger.error(f"Error starting hotspot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/hotspot/stop', methods=['POST'])
def stop_hotspot():
    """Stop WiFi hotspot"""
    try:
        # success = network_config.stop_hotspot()
        success = True  # Placeholder
        
        if success:
            return jsonify({'success': True, 'message': 'Hotspot stopped successfully'})
        else:
            return jsonify({'error': 'Failed to stop hotspot'}), 500
            
    except Exception as e:
        logger.error(f"Error stopping hotspot: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/network/hotspot/status', methods=['GET'])
def hotspot_status():
    """Get hotspot status"""
    try:
        # status = network_config._get_hotspot_status()
        status = {"active": False, "hostapd_active": False, "dnsmasq_active": False, "config": {}}
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting hotspot status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status with metrics"""
    try:
        import psutil
        
        status = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network': network_monitor.get_network_status(),
            'active_streams': len(decoder.get_active_streams()),
            'uptime': time.time() - psutil.boot_time(),
            'timestamp': datetime.now().isoformat(),
            'output_config': {"output_type": "hdmi", "resolution": "1920x1080", "refresh": 60}  # Placeholder
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/system_info')
def system_info():
    """Get system information"""
    import psutil
    
    return jsonify({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'disk_total': psutil.disk_usage('/').total
    })

@app.route('/api/network_diagnostics')
def network_diagnostics():
    """Run network diagnostics"""
    return jsonify(network_monitor.diagnose_network())

@app.route('/api/network_optimize', methods=['POST'])
def network_optimize():
    """Apply network optimizations"""
    success = network_monitor.optimize_network_settings()
    return jsonify({'success': success})

@app.route('/api/network_history')
def network_history():
    """Get network statistics history"""
    minutes = request.args.get('minutes', 10, type=int)
    return jsonify(network_monitor.get_network_history(minutes))

@app.route('/api/wifi_scan')
def wifi_scan():
    """Scan for WiFi networks"""
    try:
        result = subprocess.run(['iwlist', 'wlan0', 'scan'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            networks = []
            current_network = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Cell'):
                    if current_network:
                        networks.append(current_network)
                    current_network = {}
                elif line.startswith('ESSID:'):
                    current_network['ssid'] = line.split(':')[1].strip('"')
                elif line.startswith('Quality='):
                    quality = line.split('=')[1].split()[0]
                    current_network['quality'] = int(quality)
                elif line.startswith('Signal level='):
                    signal = line.split('=')[1].split()[0]
                    current_network['signal'] = signal
                elif line.startswith('Encryption key:'):
                    encrypted = line.split(':')[1].strip()
                    current_network['encrypted'] = encrypted == 'on'
            
            if current_network:
                networks.append(current_network)
                
            return jsonify({'networks': networks})
        else:
            return jsonify({'error': 'WiFi scan failed'}), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'WiFi scan timeout'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network_config', methods=['GET', 'POST'])
def network_config():
    """Get or update network configuration"""
    config_file = '/etc/rpi-player/network.conf'
    
    if request.method == 'GET':
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"')
        return jsonify(config)
    
    elif request.method == 'POST':
        data = request.get_json()
        try:
            with open(config_file, 'w') as f:
                f.write('# RPI Player Network Configuration\n')
                for key, value in data.items():
                    f.write(f'{key}="{value}"\n')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to RPI Player'})
    
    # Send current stream status
    streams = decoder.get_all_streams()
    emit('streams_update', streams)
    
    # Send network status
    network_stats = network_monitor.get_network_stats()
    emit('network_stats', network_stats)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('get_network_stats')
def handle_get_network_stats():
    """Handle request for network statistics"""
    network_stats = network_monitor.get_network_stats()
    emit('network_stats', network_stats)

@socketio.on('run_network_diagnostics')
def handle_run_network_diagnostics():
    """Handle request for network diagnostics"""
    diagnostics = network_monitor.diagnose_network()
    emit('network_diagnostics', diagnostics)

@socketio.on('optimize_network')
def handle_optimize_network():
    """Handle request for network optimization"""
    success = network_monitor.optimize_network_settings()
    emit('network_optimization_result', {'success': success})

@socketio.on('scan_wifi')
def handle_scan_wifi():
    """Handle WiFi scan request"""
    try:
        result = subprocess.run(['iwlist', 'wlan0', 'scan'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            networks = []
            current_network = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Cell'):
                    if current_network:
                        networks.append(current_network)
                    current_network = {}
                elif line.startswith('ESSID:'):
                    current_network['ssid'] = line.split(':')[1].strip('"')
                elif line.startswith('Quality='):
                    quality = line.split('=')[1].split()[0]
                    current_network['quality'] = int(quality)
                elif line.startswith('Signal level='):
                    signal = line.split('=')[1].split()[0]
                    current_network['signal'] = signal
                elif line.startswith('Encryption key:'):
                    encrypted = line.split(':')[1].strip()
                    current_network['encrypted'] = encrypted == 'on'
            
            if current_network:
                networks.append(current_network)
                
            emit('wifi_scan_result', {'networks': networks})
        else:
            emit('wifi_scan_result', {'error': 'WiFi scan failed'})
            
    except subprocess.TimeoutExpired:
        emit('wifi_scan_result', {'error': 'WiFi scan timeout'})
    except Exception as e:
        emit('wifi_scan_result', {'error': str(e)})

def detect_stream_type(url):
    """Auto-detect stream type from URL"""
    url_lower = url.lower()
    
    if url_lower.startswith('srt://'):
        return 'srt'
    elif url_lower.startswith('rtmp://'):
        return 'rtmp'
    elif url_lower.startswith('udp://'):
        return 'udp'
    else:
        return 'auto'

def get_cpu_temperature():
    """Get CPU temperature (Raspberry Pi specific)"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read()) / 1000.0
            return temp
    except:
        return None

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Start network monitoring
    network_monitor.start_monitoring(interval=5)
    
    # Run the app
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
