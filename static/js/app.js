class RPIPlayer {
    constructor() {
        this.socket = io();
        this.currentStream = null;
        this.streams = {};
        this.hlsPlayer = null;
        this.systemInfo = {};
        
        this.initializeEventListeners();
        this.initializeSocketListeners();
        this.startSystemMonitoring();
    }
    
    initializeEventListeners() {
        // Stream form submission
        document.getElementById('stream-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startStream();
        });
        
        // Stop stream button
        document.getElementById('stop-btn').addEventListener('click', () => {
            this.stopStream();
        });
        
        // Stream type change
        document.getElementById('stream-type').addEventListener('change', (e) => {
            this.updateStreamUrlPlaceholder(e.target.value);
        });
        
        // Video player events
        const videoPlayer = document.getElementById('video-player');
        videoPlayer.addEventListener('loadstart', () => this.onVideoLoadStart());
        videoPlayer.addEventListener('canplay', () => this.onVideoCanPlay());
        videoPlayer.addEventListener('error', (e) => this.onVideoError(e));
        videoPlayer.addEventListener('ended', () => this.onVideoEnded());
    }
    
    initializeSocketListeners() {
        this.socket.on('connect', () => {
            this.addLog('Connected to RPI Player server', 'success');
        });
        
        this.socket.on('streams_update', (streams) => {
            this.updateStreamsList(streams);
        });
        
        this.socket.on('stream_started', (data) => {
            this.addLog(`Stream started: ${data.stream_id}`, 'success');
            this.updateStreamStatus(data.stream_id, 'playing');
        });
        
        this.socket.on('stream_stopped', (data) => {
            this.addLog(`Stream stopped: ${data.stream_id}`, 'warning');
            this.updateStreamStatus(data.stream_id, 'stopped');
        });
        
        this.socket.on('system_info', (info) => {
            this.updateSystemInfo(info);
        });
        
        this.socket.on('error', (error) => {
            this.addLog(`Server error: ${error.message}`, 'error');
        });
    }
    
    async startStream() {
        const url = document.getElementById('stream-url').value.trim();
        const type = document.getElementById('stream-type').value;
        
        if (!url) {
            this.addLog('Please enter a stream URL', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/start_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, type })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentStream = data.stream_id;
                this.streams[data.stream_id] = {
                    url: url,
                    type: type,
                    status: 'starting'
                };
                
                // Update UI
                document.getElementById('start-btn').disabled = true;
                document.getElementById('stop-btn').disabled = false;
                document.getElementById('current-stream').textContent = `Stream: ${data.stream_id}`;
                
                this.addLog(`Starting stream: ${url}`, 'info');
                
                // Start HLS player after a delay
                setTimeout(() => this.startHLSPlayer(data.stream_id), 2000);
                
            } else {
                this.addLog(`Failed to start stream: ${data.error}`, 'error');
            }
            
        } catch (error) {
            this.addLog(`Network error: ${error.message}`, 'error');
        }
    }
    
    async stopStream() {
        if (!this.currentStream) {
            this.addLog('No active stream to stop', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/stop_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ stream_id: this.currentStream })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.stopHLSPlayer();
                this.currentStream = null;
                
                // Update UI
                document.getElementById('start-btn').disabled = false;
                document.getElementById('stop-btn').disabled = true;
                document.getElementById('current-stream').textContent = 'No stream active';
                document.getElementById('stream-duration').textContent = 'Duration: 00:00';
                
                this.addLog('Stream stopped', 'info');
                
            } else {
                this.addLog(`Failed to stop stream: ${data.error}`, 'error');
            }
            
        } catch (error) {
            this.addLog(`Network error: ${error.message}`, 'error');
        }
    }
    
    startHLSPlayer(streamId) {
        const videoPlayer = document.getElementById('video-player');
        const noStreamPlaceholder = document.getElementById('no-stream');
        
        // Construct HLS URL
        const hlsUrl = `/streams/stream_${streamId}.m3u8`;
        
        if (Hls.isSupported()) {
            this.hlsPlayer = new Hls({
                debug: false,
                enableWorker: true,
                lowLatencyMode: true,
                backBufferLength: 90
            });
            
            this.hlsPlayer.loadSource(hlsUrl);
            this.hlsPlayer.attachMedia(videoPlayer);
            
            this.hlsPlayer.on(Hls.Events.MANIFEST_PARSED, () => {
                videoPlayer.play().catch(error => {
                    this.addLog(`Autoplay failed: ${error.message}`, 'warning');
                });
            });
            
            this.hlsPlayer.on(Hls.Events.ERROR, (event, data) => {
                this.addLog(`HLS Error: ${data.details}`, 'error');
                if (data.fatal) {
                    switch (data.type) {
                        case Hls.ErrorTypes.NETWORK_ERROR:
                            this.addLog('Network error, retrying...', 'warning');
                            setTimeout(() => this.hlsPlayer.startLoad(), 1000);
                            break;
                        case Hls.ErrorTypes.MEDIA_ERROR:
                            this.addLog('Media error, recovering...', 'warning');
                            this.hlsPlayer.recoverMediaError();
                            break;
                        default:
                            this.stopHLSPlayer();
                            break;
                    }
                }
            });
            
        } else if (videoPlayer.canPlayType('application/vnd.apple.mpegurl')) {
            // Native HLS support (Safari)
            videoPlayer.src = hlsUrl;
            videoPlayer.play().catch(error => {
                this.addLog(`Autoplay failed: ${error.message}`, 'warning');
            });
        } else {
            this.addLog('HLS not supported in this browser', 'error');
            return;
        }
        
        // Show video player, hide placeholder
        videoPlayer.style.display = 'block';
        noStreamPlaceholder.style.display = 'none';
        
        this.addLog(`HLS player started for stream ${streamId}`, 'success');
    }
    
    stopHLSPlayer() {
        const videoPlayer = document.getElementById('video-player');
        const noStreamPlaceholder = document.getElementById('no-stream');
        
        if (this.hlsPlayer) {
            this.hlsPlayer.destroy();
            this.hlsPlayer = null;
        }
        
        videoPlayer.pause();
        videoPlayer.src = '';
        
        // Hide video player, show placeholder
        videoPlayer.style.display = 'none';
        noStreamPlaceholder.style.display = 'flex';
        
        this.addLog('HLS player stopped', 'info');
    }
    
    updateStreamUrlPlaceholder(streamType) {
        const urlInput = document.getElementById('stream-url');
        let placeholder = '';
        
        switch (streamType) {
            case 'srt':
                placeholder = 'srt://192.168.1.100:1234';
                break;
            case 'rtmp':
                placeholder = 'rtmp://live.twitch.tv/live/streamkey';
                break;
            case 'udp':
                placeholder = 'udp://239.0.0.1:1234';
                break;
            case 'hls':
                placeholder = 'https://example.com/stream.m3u8';
                break;
            default:
                placeholder = 'Enter stream URL';
        }
        
        urlInput.placeholder = placeholder;
    }
    
    updateStreamsList(streams) {
        const container = document.getElementById('streams-container');
        
        if (Object.keys(streams).length === 0) {
            container.innerHTML = '<div class="no-streams">No active streams</div>';
            return;
        }
        
        let html = '';
        for (const [streamId, streamInfo] of Object.entries(streams)) {
            const statusClass = streamInfo.status || 'unknown';
            const duration = streamInfo.duration ? this.formatDuration(streamInfo.duration) : '00:00';
            
            html += `
                <div class="stream-item ${statusClass}">
                    <div class="stream-header">
                        <span class="stream-id">${streamId}</span>
                        <span class="stream-status ${statusClass}">${statusClass}</span>
                    </div>
                    <div class="stream-url">${streamInfo.url || 'Unknown URL'}</div>
                    <div class="stream-duration">Duration: ${duration}</div>
                </div>
            `;
        }
        
        container.innerHTML = html;
    }
    
    updateStreamStatus(streamId, status) {
        if (this.streams[streamId]) {
            this.streams[streamId].status = status;
        }
        
        // Update streams list
        this.socket.emit('get_streams');
    }
    
    updateSystemInfo(info) {
        this.systemInfo = info;
        
        document.getElementById('cpu-temp').textContent = 
            info.temperature ? `CPU: ${info.temperature.toFixed(1)}°C` : 'CPU: --°C';
        document.getElementById('cpu-usage').textContent = 
            `CPU: ${info.cpu_percent?.toFixed(1) || '--'}%`;
        document.getElementById('mem-usage').textContent = 
            `RAM: ${info.memory_percent?.toFixed(1) || '--'}%`;
    }
    
    startSystemMonitoring() {
        // Request system info every 5 seconds
        setInterval(() => {
            this.socket.emit('get_system_info');
        }, 5000);
        
        // Update stream duration every second
        setInterval(() => {
            if (this.currentStream && this.streams[this.currentStream]) {
                const stream = this.streams[this.currentStream];
                if (stream.status === 'playing') {
                    const duration = Date.now() - stream.startTime;
                    document.getElementById('stream-duration').textContent = 
                        `Duration: ${this.formatDuration(duration / 1000)}`;
                }
            }
        }, 1000);
    }
    
    onVideoLoadStart() {
        this.addLog('Video loading...', 'info');
    }
    
    onVideoCanPlay() {
        this.addLog('Video ready to play', 'success');
        if (this.currentStream) {
            this.streams[this.currentStream].startTime = Date.now();
        }
    }
    
    onVideoError(event) {
        this.addLog(`Video error: ${event.target.error?.message || 'Unknown error'}`, 'error');
    }
    
    onVideoEnded() {
        this.addLog('Video playback ended', 'info');
    }
    
    addLog(message, type = 'info') {
        const logContainer = document.getElementById('log-container');
        const timestamp = new Date().toLocaleTimeString();
        
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        // Keep only last 100 log entries
        while (logContainer.children.length > 100) {
            logContainer.removeChild(logContainer.firstChild);
        }
    }
    
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.rpiPlayer = new RPIPlayer();
    
    // Request initial data
    window.rpiPlayer.socket.emit('get_streams');
    window.rpiPlayer.socket.emit('get_system_info');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Refresh data when page becomes visible
        if (window.rpiPlayer) {
            window.rpiPlayer.socket.emit('get_streams');
            window.rpiPlayer.socket.emit('get_system_info');
        }
    }
});

// Handle connection errors
window.addEventListener('online', () => {
    if (window.rpiPlayer) {
        window.rpiPlayer.addLog('Connection restored', 'success');
    }
});

window.addEventListener('offline', () => {
    if (window.rpiPlayer) {
        window.rpiPlayer.addLog('Connection lost', 'error');
    }
});
