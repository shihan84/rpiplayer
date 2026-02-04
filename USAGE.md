# V-Player Enterprise - Usage Documentation

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Web Interface Guide](#web-interface-guide)
4. [Streaming Configuration](#streaming-configuration)
5. [Network Management](#network-management)
6. [Output Configuration](#output-configuration)
7. [Cloudflare Zero Trust](#cloudflare-zero-trust)
8. [System Monitoring](#system-monitoring)
9. [API Reference](#api-reference)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### Prerequisites
- Raspberry Pi 3, 4, or 5
- MicroSD Card (16GB+ recommended)
- Network connection (Ethernet or WiFi)
- Modern web browser

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/shihan84/rpiplayer.git
cd rpiplayer

# Run the installation script
sudo ./install-v-player.sh

# Or choose edition interactively
sudo ./deploy/choose-version.sh
```

### 2. First Launch
1. Reboot the Raspberry Pi after installation
2. Open web browser to: `http://v-player.local:5005`
3. Or use IP address: `http://[RPI-IP]:5005`

### 3. Basic Setup
1. Configure network settings (if needed)
2. Set up video output preferences
3. Test with a sample stream

---

## Installation

### Standard Edition Installation
```bash
# Download and install
git clone https://github.com/shihan84/rpiplayer.git
cd rpiplayer
sudo ./install-v-player.sh

# Start the service
sudo systemctl enable v-player.service
sudo systemctl start v-player.service
```

### Enterprise Edition Installation
```bash
# Download and install enterprise version
git clone https://github.com/shihan84/rpiplayer.git
cd rpiplayer
sudo ./enterprise/install-enterprise.sh

# Configure enterprise features
sudo systemctl enable v-player-enterprise.service
sudo systemctl start v-player-enterprise.service
```

### Pre-built Image Installation
1. Download latest image from [GitHub Releases](https://github.com/shihan84/rpiplayer/releases)
2. Flash to SD card using Raspberry Pi Imager
3. Boot and access at `http://v-player.local:5005`

---

## Web Interface Guide

### Dashboard Overview
The V-Player Enterprise dashboard provides a professional broadcasting interface with:

- **Stream Management**: Add, configure, and monitor streams
- **System Status**: Real-time CPU, memory, and network metrics
- **Output Configuration**: Video output settings and routing
- **Network Management**: WiFi, Ethernet, and hotspot controls
- **Cloudflare Integration**: Secure remote access setup

### Navigation Tabs

#### 🏠 Home
- System overview and status
- Quick actions and shortcuts
- Recent stream history

#### 📺 Outputs
- HDMI output configuration
- Resolution and display settings
- Audio output options
- Broadcast format selection

#### 🌐 Network
- WiFi client management
- Ethernet configuration
- Hotspot setup and control
- Network metrics and monitoring
- Cloudflare Zero Trust setup

#### 📊 Streams
- Active stream management
- Stream configuration
- Protocol settings (SRT, RTMP, UDP, HLS, RTP)
- Stream quality and performance

#### ⚙️ Settings
- System configuration
- User preferences
- Advanced options
- Maintenance tools

---

## Streaming Configuration

### Supported Protocols

#### SRT (Secure Reliable Transport)
```
URL Format: srt://hostname:port?parameters
Example: srt://192.168.1.100:1234?passphrase=secret
```

#### RTMP (Real-Time Messaging Protocol)
```
URL Format: rtmp://hostname/app/stream
Example: rtmp://live.example.com/live/streamkey
```

#### UDP (User Datagram Protocol)
```
URL Format: udp://hostname:port
Example: udp://239.1.1.1:5004
```

#### HLS (HTTP Live Streaming)
```
URL Format: https://hostname/path/playlist.m3u8
Example: https://cdn.example.com/live/playlist.m3u8
```

#### RTSP (Real-Time Streaming Protocol)
```
URL Format: rtsp://hostname:port/path
Example: rtsp://192.168.1.100:554/stream
```

### Stream Configuration Steps

1. **Navigate to Streams Tab**
   - Click "Add New Stream"
   - Enter stream URL
   - Select protocol (or use auto-detect)

2. **Configure Stream Settings**
   - Stream name/alias
   - Quality settings
   - Buffer size
   - Timeout settings

3. **Output Configuration**
   - Select video output (HDMI, Composite, etc.)
   - Configure audio settings
   - Set resolution and frame rate

4. **Start Streaming**
   - Click "Start Stream"
   - Monitor status in real-time
   - Check logs for issues

### Advanced Stream Settings

#### Quality Configuration
```yaml
resolution: "1920x1080"
framerate: 30
bitrate: "5000k"
audio_bitrate: "128k"
buffer_size: "2000k"
```

#### Hardware Acceleration
- **H.264**: Hardware decoding on Raspberry Pi
- **H.265**: Supported on Pi 4/5
- **Audio**: Hardware audio processing
- **GPU**: OpenGL ES acceleration

---

## Network Management

### WiFi Configuration

#### Connect to WiFi Network
1. Navigate to **Network → WiFi**
2. Click "Scan Networks"
3. Select network from list
4. Enter password (if required)
5. Click "Connect"

#### WiFi Hotspot Setup
1. Navigate to **Network → Hotspot**
2. Configure hotspot settings:
   - SSID: V-Player-Hotspot (default)
   - Password: vplayer123 (default)
   - Channel: Auto (default)
3. Click "Start Hotspot"

### Ethernet Configuration

#### DHCP (Automatic)
```bash
# Default configuration
interface eth0
dhcp
```

#### Static IP Configuration
```bash
# Static IP example
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

### Network Monitoring

#### Real-time Metrics
- **Connection Speed**: Upload/download rates
- **Signal Strength**: WiFi signal quality
- **Data Usage**: Bandwidth consumption
- **Network Status**: Connection health

#### Network Diagnostics
```bash
# Test network connectivity
ping -c 4 google.com

# Check network interfaces
ip addr show

# Monitor network traffic
iftop -i eth0
```

---

## Output Configuration

### HDMI Output

#### Resolution Settings
- **1080p**: 1920x1080 @ 60Hz (recommended)
- **720p**: 1280x720 @ 60Hz
- **480p**: 720x480 @ 60Hz
- **Auto**: Detect best resolution

#### Audio Configuration
- **HDMI Audio**: Digital audio through HDMI
- **Analog Audio**: 3.5mm jack output
- **Both**: Simultaneous output

### Composite Output
- **PAL**: 720x576 @ 25Hz (Europe/Asia)
- **NTSC**: 720x480 @ 29.97Hz (Americas)
- **Auto**: Detect regional standard

### DSI/DPI LCD Panels
- **Official DSI Display**: 800x480 touchscreen
- **Generic DSI**: Various resolutions supported
- **DPI Displays**: Custom configurations

### Output Switching
```bash
# Switch to HDMI
sudo /opt/v-player/video-output-selector.sh
# Select option 1 for HDMI

# Switch to Composite
sudo /opt/v-player/video-output-selector.sh
# Select option 2 for Composite

# Auto-detect best output
sudo /opt/v-player/video-output-selector.sh
# Select option 3 for Auto
```

---

## Cloudflare Zero Trust

### Overview
Cloudflare Zero Trust provides secure remote access to your V-Player interface without exposing ports to the internet.

### Setup Process

#### 1. Prerequisites
- Cloudflare account
- Registered domain
- V-Player Enterprise installed

#### 2. Dashboard Setup
1. Navigate to **Network → Cloudflare Zero Trust**
2. Click "Generate Setup Instructions"
3. Follow the step-by-step guide:
   - Create Cloudflare account
   - Set up Zero Trust dashboard
   - Configure access policies
   - Install cloudflared

#### 3. Automatic Installation
```bash
# Install cloudflared automatically
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# Configure tunnel
cloudflared tunnel login
cloudflared tunnel create vplayer-enterprise
```

#### 4. Service Configuration
```bash
# Create systemd service
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# Check status
sudo systemctl status cloudflared
```

### Access Policies
- **Email Authentication**: Allow specific email domains
- **Time Restrictions**: Limit access by time
- **Location Rules**: Geographic access control
- **Device Policies**: Require device verification

### Testing Connection
1. Navigate to **Network → Cloudflare Zero Trust**
2. Click "Test Tunnel Connection"
3. Verify secure access through Cloudflare
4. Check status indicators

---

## System Monitoring

### Real-time Metrics

#### CPU Monitoring
- **Usage Percentage**: Current CPU utilization
- **Temperature**: CPU temperature in Celsius
- **Frequency**: Current CPU frequency
- **Load Average**: System load over time

#### Memory Monitoring
- **Total Memory**: Installed RAM
- **Used Memory**: Currently in use
- **Available Memory**: Free RAM
- **Swap Usage**: Virtual memory usage

#### Storage Monitoring
- **Disk Usage**: Storage space utilization
- **SD Card Health**: Card status and lifespan
- **Log Files**: Log file sizes and rotation

#### Network Monitoring
- **Interface Status**: Connection status
- **IP Configuration**: Current network settings
- **Bandwidth Usage**: Data transfer rates
- **Connection Quality**: Signal strength and stability

### Performance Optimization

#### CPU Optimization
```bash
# Set performance governor
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils

# Overclock settings (caution)
echo 'arm_freq=1500' | sudo tee -a /boot/config.txt
echo 'over_voltage=2' | sudo tee -a /boot/config.txt
```

#### Memory Optimization
```bash
# GPU memory split
echo 'gpu_mem=256' | sudo tee -a /boot/config.txt

# Disable unused services
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

#### Storage Optimization
```bash
# Log rotation
sudo logrotate -f /etc/logrotate.conf

# Clean temporary files
sudo apt-get clean
sudo rm -rf /tmp/*
```

---

## API Reference

### REST API Endpoints

#### Authentication
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "password"
}
```

#### Stream Management
```http
# Start Stream
POST /api/streams/start
Content-Type: application/json

{
    "url": "srt://192.168.1.100:1234",
    "name": "Test Stream",
    "output": "hdmi"
}

# Stop Stream
POST /api/streams/stop
Content-Type: application/json

{
    "stream_id": "abc12345"
}

# Get Stream Status
GET /api/streams/{stream_id}

# List All Streams
GET /api/streams
```

#### System Information
```http
GET /api/system/info
GET /api/system/metrics
GET /api/system/logs
```

#### Network Configuration
```http
GET /api/network/status
POST /api/network/wifi/connect
POST /api/network/hotspot/start
GET /api/network/metrics
```

#### Cloudflare Integration
```http
GET /api/cloudflare/status
POST /api/cloudflare/install
POST /api/cloudflare/tunnel/start
POST /api/cloudflare/test
```

### WebSocket Events

#### Client to Server
```javascript
// Get streams list
socket.emit('get_streams');

// Get system info
socket.emit('get_system_info');

// Subscribe to updates
socket.emit('subscribe', {type: 'system'});
```

#### Server to Client
```javascript
// Stream status updates
socket.on('streams_update', (data) => {
    console.log('Streams:', data);
});

// System metrics
socket.on('system_metrics', (data) => {
    console.log('Metrics:', data);
});

// Error notifications
socket.on('error', (error) => {
    console.error('Error:', error);
});
```

---

## Troubleshooting

### Common Issues

#### Stream Won't Start
**Symptoms**: Stream fails to start or immediately stops

**Solutions**:
1. Check stream URL format
2. Verify network connectivity
3. Test stream manually with FFmpeg
4. Check system resources

```bash
# Test stream manually
ffmpeg -i "srt://192.168.1.100:1234" -f null -

# Check logs
sudo journalctl -u v-player.service -f
```

#### No Video Output
**Symptoms**: No display on connected monitor

**Solutions**:
1. Check video cable connections
2. Verify output configuration
3. Test different resolution
4. Check GPU memory settings

```bash
# Check video configuration
cat /boot/config.txt | grep -E "(hdmi|gpu_mem|dtoverlay)"

# Test video output
ffmpeg -f lavfi -i testsrc -t 10 -f fbdev /dev/fb0
```

#### Network Connection Issues
**Symptoms**: Cannot connect to network or internet

**Solutions**:
1. Check network cable
2. Verify WiFi credentials
3. Restart network services
4. Check IP configuration

```bash
# Restart networking
sudo systemctl restart networking
sudo systemctl restart dhcpcd

# Check network status
ip addr show
ping -c 4 8.8.8.8
```

#### High CPU Usage
**Symptoms**: System running slow or overheating

**Solutions**:
1. Check hardware acceleration
2. Reduce stream quality
3. Enable GPU acceleration
4. Monitor temperature

```bash
# Check temperature
vcgencmd measure_temp

# Check throttling
vcgencmd get_throttled

# Enable GPU acceleration
echo 'dtoverlay=vc4-kms-v3d' | sudo tee -a /boot/config.txt
```

### Log Files

#### Application Logs
```bash
# V-Player logs
tail -f /opt/v-player/logs/vplayer.log

# System logs
sudo journalctl -u v-player.service -f

# FFmpeg logs
tail -f /tmp/ffmpeg*.log
```

#### Network Logs
```bash
# DHCP logs
sudo journalctl -u dhcpcd -f

# WiFi logs
sudo journalctl -u wpa_supplicant -f

# Network manager logs
sudo journalctl -u NetworkManager -f
```

### Performance Tuning

#### System Optimization
```bash
# Update system
sudo apt update && sudo upgrade -y

# Remove unnecessary packages
sudo apt autoremove -y

# Optimize boot time
sudo systemctl disable bluetooth
sudo systemctl disable cups
sudo systemctl disable avahi-daemon
```

#### Hardware Optimization
```bash
# Set GPU memory
echo 'gpu_mem=256' | sudo tee -a /boot/config.txt

# Enable performance mode
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils

# Optimize SD card
echo 'tmpfs /tmp tmpfs defaults,noatime,nosuid,size=100m 0 0' | sudo tee -a /etc/fstab
```

---

## Advanced Configuration

### Custom Configuration Files

#### Main Configuration (`config.py`)
```python
class Config:
    HOST = '0.0.0.0'
    PORT = 5005
    DEBUG = False
    SECRET_KEY = 'your-secret-key'
    
    # Stream settings
    MAX_STREAMS = 4
    DEFAULT_BUFFER_SIZE = '2000k'
    DEFAULT_BITRATE = '5000k'
    
    # Hardware settings
    HARDWARE_ACCELERATION = True
    GPU_MEMORY = 256
    
    # Network settings
    HOTSPOT_SSID = 'V-Player-Hotspot'
    HOTSPOT_PASSWORD = 'vplayer123'
```

#### FFmpeg Configuration
```bash
# Custom FFmpeg preset
/opt/v-player/ffmpeg-presets/h264_high_quality.preset

# Hardware acceleration settings
/opt/v-player/ffmpeg-presets/hardware_acceleration.preset
```

### Custom Scripts

#### Stream Testing Script
```bash
#!/bin/bash
# /opt/v-player/scripts/test-stream.sh

STREAM_URL="$1"
OUTPUT_DEVICE="$2"

if [ -z "$STREAM_URL" ]; then
    echo "Usage: $0 <stream_url> [output_device]"
    exit 1
fi

ffmpeg -i "$STREAM_URL" \
    -c:v h264_v4l2m2m \
    -c:a aac \
    -b:v 2000k \
    -b:a 128k \
    -f "${OUTPUT_DEVICE:-fbdev}" \
    /dev/fb0
```

#### Network Diagnostics Script
```bash
#!/bin/bash
# /opt/v-player/scripts/network-diagnostics.sh

echo "=== Network Diagnostics ==="
echo "Date: $(date)"
echo ""

echo "=== Interfaces ==="
ip addr show
echo ""

echo "=== Routing Table ==="
ip route show
echo ""

echo "=== DNS Configuration ==="
cat /etc/resolv.conf
echo ""

echo "=== Connectivity Test ==="
ping -c 4 8.8.8.8
echo ""

echo "=== Speed Test ==="
curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3
```

### Backup and Restore

#### System Backup
```bash
# Create system backup
sudo dd if=/dev/mmcblk0 of=/backup/v-player-backup.img bs=4M

# Backup configuration
tar -czf /backup/v-player-config.tar.gz \
    /opt/v-player/ \
    /etc/systemd/system/v-player.service \
    /boot/config.txt
```

#### Configuration Restore
```bash
# Restore configuration
sudo tar -xzf /backup/v-player-config.tar.gz -C /

# Restore service
sudo systemctl daemon-reload
sudo systemctl enable v-player.service
sudo systemctl start v-player.service
```

---

## Support and Maintenance

### Regular Maintenance
```bash
# Weekly maintenance script
#!/bin/bash
# /opt/v-player/scripts/maintenance.sh

# Update system
sudo apt update && sudo upgrade -y

# Clean logs
sudo journalctl --vacuum-time=7d

# Check disk space
df -h

# Check temperature
vcgencmd measure_temp

# Restart services if needed
sudo systemctl restart v-player.service
```

### Getting Help
- **Documentation**: [GitHub Wiki](https://github.com/shihan84/rpiplayer/wiki)
- **Issues**: [GitHub Issues](https://github.com/shihan84/rpiplayer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shihan84/rpiplayer/discussions)
- **Support**: support@itassistbroadcast.com

### Version Information
```bash
# Check V-Player version
cat /opt/v-player/VERSION

# Check system information
uname -a
cat /etc/os-release

# Check hardware info
vcgencmd version
```

---

*This documentation is maintained by ITAssist Broadcast Solutions. For the latest updates, visit our GitHub repository.*
