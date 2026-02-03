#!/usr/bin/env python3
"""
V-Player Enterprise Backend
Professional Streaming Solution by Itassist Broadcast Solutions

Enhanced Flask backend for enterprise deployment with OpenResty frontend.
Features: JWT authentication, Redis caching, metrics, advanced monitoring.
"""

import os
import sys
import logging
import json
import time
import uuid
import redis
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Import existing components
sys.path.append('..')
from config import Config
from stream_decoder import StreamDecoder
from network_monitor import NetworkMonitor

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'v-player-enterprise-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)
limiter = Limiter(app, key_func=get_remote_address)

# Configure logging
try:
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'v-player-enterprise.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('V-Player-Enterprise')
    logger.info("V-Player Enterprise backend initialized")
    
except Exception as e:
    print(f"ERROR: Failed to initialize logging: {e}")
    sys.exit(1)

# Initialize Redis
try:
    redis_client = redis.Redis(
        host='localhost', 
        port=6379, 
        db=0, 
        decode_responses=True,
        socket_timeout=5
    )
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None

# Initialize components
try:
    decoder = StreamDecoder()
    network_monitor = NetworkMonitor(socketio)
    logger.info("V-Player Enterprise components initialized")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    sys.exit(1)

# Prometheus metrics
REQUEST_COUNT = Counter('v_player_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('v_player_request_duration_seconds', 'Request duration')
ACTIVE_STREAMS = Gauge('v_player_active_streams', 'Number of active streams')
SYSTEM_LOAD = Gauge('v_player_system_load', 'System load average')

# Middleware for metrics
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_DURATION.observe(time.time() - request.start_time)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    return response

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Enterprise authentication"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Simple authentication (in production, use proper user management)
    if username == 'admin' and password == 'vplayer123':
        access_token = create_access_token(identity=username)
        
        # Cache session in Redis
        if redis_client:
            session_id = str(uuid.uuid4())
            redis_client.setex(f"session:{session_id}", 86400, json.dumps({
                'username': username,
                'login_time': datetime.now().isoformat()
            }))
        
        logger.info(f"User {username} logged in successfully")
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 86400
        })
    
    logger.warning(f"Failed login attempt for {username}")
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Refresh JWT token"""
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_token})

# Protected API endpoints
@app.route('/api/streams', methods=['GET'])
@jwt_required()
def get_streams():
    """Get all active streams"""
    try:
        streams = decoder.get_active_streams()
        
        # Update metrics
        ACTIVE_STREAMS.set(len(streams))
        
        return jsonify({'streams': streams})
    except Exception as e:
        logger.error(f"Error getting streams: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/streams', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def start_stream():
    """Start a new stream with enterprise features"""
    try:
        data = request.get_json()
        stream_url = data.get('url')
        stream_type = data.get('type', 'auto')
        stream_name = data.get('name', f'Stream {uuid.uuid4().hex[:8]}')
        
        if not stream_url:
            return jsonify({'error': 'Stream URL is required'}), 400
        
        # Generate unique stream ID
        stream_id = str(uuid.uuid4())[:8]
        
        # Auto-detect stream type
        if stream_type == 'auto':
            stream_type = detect_stream_type(stream_url)
        
        # Start the stream
        success = decoder.start_stream(stream_id, stream_url, stream_type)
        
        if success:
            # Cache stream info in Redis
            stream_info = {
                'id': stream_id,
                'name': stream_name,
                'url': stream_url,
                'type': stream_type,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'created_by': get_jwt_identity()
            }
            
            if redis_client:
                redis_client.setex(f"stream:{stream_id}", 3600, json.dumps(stream_info))
            
            # Notify clients
            socketio.emit('stream_started', stream_info)
            
            logger.info(f"Stream {stream_id} started by {get_jwt_identity()}")
            return jsonify({'stream': stream_info})
        
        return jsonify({'error': 'Failed to start stream'}), 500
        
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/streams/<stream_id>', methods=['DELETE'])
@jwt_required()
def stop_stream(stream_id):
    """Stop a stream"""
    try:
        success = decoder.stop_stream(stream_id)
        
        if success:
            # Remove from cache
            if redis_client:
                redis_client.delete(f"stream:{stream_id}")
            
            # Notify clients
            socketio.emit('stream_stopped', {'stream_id': stream_id})
            
            logger.info(f"Stream {stream_id} stopped by {get_jwt_identity()}")
            return jsonify({'message': 'Stream stopped'})
        
        return jsonify({'error': 'Stream not found'}), 404
        
    except Exception as e:
        logger.error(f"Error stopping stream: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/system/status', methods=['GET'])
@jwt_required()
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
            'timestamp': datetime.now().isoformat()
        }
        
        # Update system metrics
        SYSTEM_LOAD.set(status['cpu_percent'] / 100.0)
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """Get Prometheus metrics"""
    try:
        metrics_data = generate_latest()
        return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Web interface
@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('../static', filename)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'message': 'Connected to V-Player Enterprise'})
    logger.info('WebSocket client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('WebSocket client disconnected')

@socketio.on('get_network_status')
def handle_get_network_status():
    """Get network status via WebSocket"""
    try:
        status = network_monitor.get_network_status()
        emit('network_status', status)
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        emit('error', {'message': 'Failed to get network status'})

# Utility functions
def detect_stream_type(url):
    """Auto-detect stream type from URL"""
    if url.startswith('srt://'):
        return 'srt'
    elif url.startswith('rtmp://'):
        return 'rtmp'
    elif url.startswith('udp://'):
        return 'udp'
    elif url.startswith('http') and ('.m3u8' in url):
        return 'hls'
    elif url.startswith('rtp://'):
        return 'rtp'
    else:
        return 'auto'

if __name__ == '__main__':
    logger.info("Starting V-Player Enterprise backend...")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)
