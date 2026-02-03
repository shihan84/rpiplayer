#!/bin/bash

# RPI Player Installation Script
# Automated installation for Raspberry Pi 3

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/home/rpiplayer/rpi-player"
SERVICE_USER="rpiplayer"
PYTHON_VENV="$INSTALL_DIR/venv"

# Functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_raspberry_pi() {
    log "Checking if running on Raspberry Pi..."
    
    if [ ! -f /proc/device-tree/model ]; then
        error "This script is designed for Raspberry Pi only"
    fi
    
    local model=$(tr -d '\0' < /proc/device-tree/model)
    log "Detected: $model"
    
    if ! echo "$model" | grep -q "Raspberry Pi"; then
        error "This script is designed for Raspberry Pi only"
    fi
}

check_dependencies() {
    log "Checking system dependencies..."
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root (use sudo)"
    fi
    
    # Check internet connection
    if ! ping -c 1 google.com >/dev/null 2>&1; then
        warn "No internet connection detected"
    fi
}

update_system() {
    log "Updating system packages..."
    apt-get update
    apt-get upgrade -y
}

install_system_packages() {
    log "Installing system packages..."
    
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        ffmpeg \
        git \
        curl \
        wget \
        unzip \
        build-essential \
        pkg-config \
        libavcodec-dev \
        libavformat-dev \
        libavutil-dev \
        libswscale-dev \
        libavresample-dev \
        v4l-utils \
        libv4l-dev \
        libdrm-dev \
        libgbm-dev \
        libgles2-mesa-dev \
        libegl1-mesa-dev \
        libasound2-dev \
        libpulse-dev \
        libx11-dev \
        libxrandr-dev \
        libxinerama-dev \
        libxcursor-dev \
        libxi-dev \
        libxss-dev \
        libxtst-dev \
        libgtk-3-dev \
        libgstreamer1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-libav \
        gstreamer1.0-tools \
        omxplayer \
        libomxil-bellagio-dev \
        libilbc-dev \
        libopus-dev \
        libvpx-dev \
        libx264-dev \
        libx265-dev \
        libfdk-aac-dev \
        libmp3lame-dev \
        libshine-dev \
        libsrt-dev \
        librtmp-dev \
        libssl-dev \
        libcurl4-openssl-dev
}

create_service_user() {
    log "Creating service user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$SERVICE_USER"
        usermod -a -G video,audio,render,gpio,i2c,spi "$SERVICE_USER"
        log "Created user: $SERVICE_USER"
    else
        log "User $SERVICE_USER already exists"
    fi
}

install_rpi_player() {
    log "Installing RPI Player application..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/streams"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/config"
    
    # Copy application files (assuming script is run from repository)
    if [ -f "$(dirname "$0")/app.py" ]; then
        # Install from local repository
        cp -r "$(dirname "$0")"/* "$INSTALL_DIR/"
        log "Installed from local repository"
    else
        # Clone from GitHub
        cd /tmp
        git clone https://github.com/yourusername/rpi-player.git
        cp -r rpi-player/* "$INSTALL_DIR/"
        rm -rf rpi-player
        log "Installed from GitHub repository"
    fi
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
}

setup_python_environment() {
    log "Setting up Python virtual environment..."
    
    sudo -u "$SERVICE_USER" python3 -m venv "$PYTHON_VENV"
    sudo -u "$SERVICE_USER" "$PYTHON_VENV/bin/pip" install --upgrade pip
    
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        sudo -u "$SERVICE_USER" "$PYTHON_VENV/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    else
        warn "requirements.txt not found, installing minimal dependencies"
        sudo -u "$SERVICE_USER" "$PYTHON_VENV/bin/pip" install \
            Flask==2.3.3 \
            Flask-SocketIO==5.3.6 \
            python-socketio==5.8.0 \
            eventlet==0.33.3 \
            psutil==5.9.5 \
            requests==2.31.0
    fi
}

configure_nginx() {
    log "Configuring Nginx..."
    
    # Create nginx configuration
    cat > /etc/nginx/sites-available/rpi-player << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Serve static files
    location /static/ {
        alias /home/rpiplayer/rpi-player/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy to Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Origin "";
    }
    
    # Serve HLS streams
    location /streams/ {
        alias /tmp/;
        add_header Cache-Control no-cache;
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Range';
        
        # CORS preflight
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Range';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
}
EOF
    
    # Enable site
    rm -f /etc/nginx/sites-enabled/default
    ln -s /etc/nginx/sites-available/rpi-player /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    nginx -t
    
    # Restart nginx
    systemctl restart nginx
    systemctl enable nginx
}

setup_systemd_service() {
    log "Setting up systemd service..."
    
    cat > /etc/systemd/system/rpi-player.service << EOF
[Unit]
Description=RPI Stream Player Service
After=network.target nginx.service
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PYTHONPATH=$INSTALL_DIR
Environment=FLASK_ENV=production
ExecStart=$PYTHON_VENV/bin/python app.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR/streams $INSTALL_DIR/logs /tmp
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable rpi-player.service
}

configure_video_output() {
    log "Configuring video output..."
    
    # Backup original config
    if [ -f /boot/config.txt ]; then
        cp /boot/config.txt "/boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Add RPI Player optimizations to config.txt
    cat >> /boot/config.txt << 'EOF'

# RPI Player Optimizations
gpu_mem=256
hdmi_force_hotplug=1
hdmi_drive=2
config_hdmi_boost=4
disable_splash=1
avoid_warnings=1
max_framebuffers=1
disable_overscan=1
framebuffer_depth=32
framebuffer_ignore_alpha=1

# Hardware Acceleration
start_x=1
dtoverlay=vc4-kms-v3d
dtoverlay=vc4-fkms-v3d,cma-256

# Audio
dtparam=audio=on

# Performance
arm_freq=1400
over_voltage=2
sdram_freq=500
core_freq=500
EOF
    
    log "Video output configured. Reboot required to apply changes."
}

create_desktop_shortcuts() {
    log "Creating desktop shortcuts..."
    
    # Create desktop entry
    cat > /usr/share/applications/rpi-player.desktop << 'EOF'
[Desktop Entry]
Name=RPI Player
Comment=Raspberry Pi Stream Player
Exec=xdg-open http://localhost:5000
Icon=video-display
Terminal=false
Type=Application
Categories=AudioVideo;Video;
EOF
    
    # Add to autostart for desktop environments
    mkdir -p /etc/xdg/autostart
    cp /usr/share/applications/rpi-player.desktop /etc/xdg/autostart/
}

setup_firewall() {
    log "Configuring firewall..."
    
    if command -v ufw >/dev/null 2>&1; then
        ufw allow 22/tcp    # SSH
        ufw allow 80/tcp    # HTTP
        ufw allow 5000/tcp  # Flask app (direct access)
        ufw --force enable
        log "Firewall configured with UFW"
    else
        warn "UFW not found, skipping firewall configuration"
    fi
}

run_tests() {
    log "Running basic tests..."
    
    # Test Python environment
    sudo -u "$SERVICE_USER" "$PYTHON_VENV/bin/python" -c "import flask; print('Flask OK')"
    
    # Test FFmpeg
    ffmpeg -version | head -1
    
    # Test nginx
    nginx -t
    
    # Test service
    systemctl status rpi-player.service --no-pager
    
    log "Basic tests completed"
}

show_completion_info() {
    log "Installation completed successfully!"
    echo ""
    echo -e "${BLUE}=== RPI Player Installation Complete ===${NC}"
    echo ""
    echo "Web Interface: http://$(hostname -I | awk '{print $1}'):5000"
    echo "Alternative: http://rpi-player.local:5000"
    echo ""
    echo "Service Commands:"
    echo "  Start:   sudo systemctl start rpi-player"
    echo "  Stop:    sudo systemctl stop rpi-player"
    echo "  Status:  sudo systemctl status rpi-player"
    echo "  Logs:    sudo journalctl -u rpi-player -f"
    echo ""
    echo "Configuration Tools:"
    echo "  Video Output: sudo $INSTALL_DIR/video-output-selector.sh"
    echo "  Stream Test:  sudo $INSTALL_DIR/stream-test.sh"
    echo ""
    echo "Important:"
    echo "  - Reboot required to apply video output settings"
    echo "  - Default user: $SERVICE_USER"
    echo "  - Application directory: $INSTALL_DIR"
    echo "  - Logs directory: $INSTALL_DIR/logs"
    echo ""
    echo -e "${GREEN}Enjoy your RPI Stream Player!${NC}"
}

# Main installation flow
main() {
    echo -e "${BLUE}=== RPI Player Installation Script ===${NC}"
    echo ""
    
    check_raspberry_pi
    check_dependencies
    update_system
    install_system_packages
    create_service_user
    install_rpi_player
    setup_python_environment
    configure_nginx
    setup_systemd_service
    configure_video_output
    create_desktop_shortcuts
    setup_firewall
    run_tests
    show_completion_info
    
    echo ""
    warn "A reboot is required to apply video output settings"
    read -p "Reboot now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Rebooting system..."
        reboot
    fi
}

# Run main function
main "$@"
