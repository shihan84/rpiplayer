from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import logging
import os
import uuid
import subprocess
import psutil
import socket
from config import Config
from stream_decoder import StreamDecoder
from network_monitor import NetworkMonitor

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('logs/rpiplayer.log'),
        logging.StreamHandler()
    ]
)

# Initialize stream decoder and network monitor
decoder = StreamDecoder()
network_monitor = NetworkMonitor(socketio)

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

@app.route('/api/system_info')
def system_info():
    """Get system information"""
    import psutil
    
    return jsonify({
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'temperature': get_cpu_temperature(),
        'network_stats': network_monitor.get_network_stats()
    })

@app.route('/api/network_status')
def network_status():
    """Get network status and diagnostics"""
    return jsonify(network_monitor.get_network_stats())

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
