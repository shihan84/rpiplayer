#!/bin/bash

# V-Player Installation Script
# Professional Streaming Solution by Itassist Broadcast Solutions
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation configuration
INSTALL_DIR="/home/rpiplayer/v-player"
SERVICE_NAME="v-player"
NGINX_CONFIG="nginx-v-player.conf"
SYSTEMD_SERVICE="v-player.service"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to detect Raspberry Pi model
detect_rpi_model() {
    if [[ -f /proc/device-tree/model ]]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
        print_status "Detected: $MODEL"
    else
        print_warning "Could not detect Raspberry Pi model"
    fi
}

# Function to update system
update_system() {
    print_status "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    print_success "System updated"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Basic dependencies
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        ffmpeg \
        git \
        curl \
        wget \
        htop \
        vim \
        nano \
        supervisor \
        systemd \
        network-manager \
        wireless-tools \
        wpasupplicant \
        hostapd \
        dnsmasq \
        net-tools \
        iproute2 \
        ethtool \
        dnsutils \
        iptables \
        iputils-ping \
        traceroute \
        nmap \
        tcpdump \
        vnstat \
        iftop \
        nethogs \
        bridge-utils \
        vlan \
        avahi-daemon \
        avahi-utils \
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
    
    print_success "Dependencies installed"
}

# Function to create user
create_user() {
    print_status "Creating V-Player user..."
    
    if ! id "rpiplayer" &>/dev/null; then
        useradd -m -s /bin/bash rpiplayer
        usermod -a -G video,audio,render,gpio,i2c,spi,netdev,input,dialout rpiplayer
        print_success "User rpiplayer created"
    else
        print_warning "User rpiplayer already exists"
    fi
    
    # Set password
    echo "rpiplayer:rpiplayer123" | chpasswd
    print_success "Password set for rpiplayer"
}

# Function to create directories
create_directories() {
    print_status "Creating V-Player directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"/{streams,logs,config,scripts}
    mkdir -p "$INSTALL_DIR"/{templates,static/css,static/js}
    
    chown -R rpiplayer:rpiplayer "$INSTALL_DIR"
    print_success "Directories created"
}

# Function to install application files
install_application() {
    print_status "Installing V-Player application..."
    
    # Copy application files
    cp app.py "$INSTALL_DIR/"
    cp config.py "$INSTALL_DIR/"
    cp stream_decoder.py "$INSTALL_DIR/"
    cp network_monitor.py "$INSTALL_DIR/"
    cp requirements.txt "$INSTALL_DIR/"
    
    # Copy web interface
    cp -r templates/* "$INSTALL_DIR/templates/"
    cp -r static/* "$INSTALL_DIR/static/"
    
    # Copy scripts if they exist
    if [[ -d "rpi-image/files" ]]; then
        cp rpi-image/files/*.sh "$INSTALL_DIR/scripts/" 2>/dev/null || true
        chmod +x "$INSTALL_DIR/scripts/"*.sh 2>/dev/null || true
    fi
    
    # Set ownership
    chown -R rpiplayer:rpiplayer "$INSTALL_DIR"
    print_success "Application files installed"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Create virtual environment
    sudo -u rpiplayer python3 -m venv "$INSTALL_DIR/venv"
    
    # Install dependencies
    sudo -u rpiplayer "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
    sudo -u rpiplayer "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    print_success "Python dependencies installed"
}

# Function to configure systemd service
configure_systemd() {
    print_status "Configuring systemd service..."
    
    # Copy service file
    cp "$SYSTEMD_SERVICE" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable "$SERVICE_NAME"
    
    print_success "Systemd service configured"
}

# Function to configure nginx
configure_nginx() {
    print_status "Configuring nginx..."
    
    # Copy nginx configuration
    cp "$NGINX_CONFIG" /etc/nginx/sites-available/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Enable V-Player site
    ln -sf /etc/nginx/sites-available/"$NGINX_CONFIG" /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    nginx -t
    
    # Restart nginx
    systemctl restart nginx
    systemctl enable nginx
    
    print_success "Nginx configured"
}

# Function to configure boot settings
configure_boot() {
    print_status "Configuring boot settings (disabling splash)..."
    
    # Backup original config
    if [[ -f /boot/config.txt ]]; then
        cp /boot/config.txt /boot/config.txt.backup
    fi
    
    # Add V-Player configuration
    cat >> /boot/config.txt << 'EOF'

# V-Player Configuration
gpu_mem=256
hdmi_force_hotplug=1
hdmi_drive=2
config_hdmi_boost=4

# Disable splash screen
disable_splash=1
disable_boot_splash=1
avoid_warnings=1
max_framebuffers=1
disable_overscan=1
framebuffer_depth=32
framebuffer_ignore_alpha=1
logo.nologo=1
boot_delay=0
silent_level=1

# Hardware acceleration
start_x=1
dtoverlay=vc4-kms-v3d
dtoverlay=vc4-fkms-v3d,cma-256

# Audio configuration
dtparam=audio=on
dtoverlay=i2s-mmap
dtoverlay=i2s-dac

# Performance optimizations
arm_freq=1400
over_voltage=2
sdram_freq=500
core_freq=500

# Network performance
dwc_otg.lpm_enable=0
smsc95xx.turbo_mode=1
EOF
    
    # Backup and update cmdline.txt
    if [[ -f /boot/cmdline.txt ]]; then
        cp /boot/cmdline.txt /boot/cmdline.txt.backup
    fi
    
    # Update cmdline.txt for silent boot
    sed -i 's/quiet/quiet logo.nologo splash=off loglevel=0/' /boot/cmdline.txt
    
    print_success "Boot settings configured"
}

# Function to configure SSH
configure_ssh() {
    print_status "Configuring SSH..."
    
    # Enable SSH
    touch /boot/ssh
    
    # Configure SSH for security
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
    
    # Restart SSH
    systemctl restart ssh
    systemctl enable ssh
    
    print_success "SSH configured"
}

# Function to configure sudoers
configure_sudoers() {
    print_status "Configuring sudoers..."
    
    echo "rpiplayer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/rpiplayer
    
    print_success "Sudoers configured"
}

# Function to create rc.local for splash clearing
create_rclocal() {
    print_status "Creating rc.local for splash clearing..."
    
    cat > /etc/rc.local << 'EOF'
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.

# Clear screen immediately for V-Player
/usr/bin/clear > /dev/tty1 2>&1 || true

exit 0
EOF
    
    chmod +x /etc/rc.local
    print_success "rc.local created"
}

# Function to start services
start_services() {
    print_status "Starting V-Player services..."
    
    # Start V-Player service
    systemctl start "$SERVICE_NAME"
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "V-Player service started successfully"
    else
        print_error "V-Player service failed to start"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
    
    print_success "All services started"
}

# Function to display installation summary
display_summary() {
    print_success "V-Player installation completed!"
    echo
    echo "==================================="
    echo "V-Player Professional Streaming Solution"
    echo "by Itassist Broadcast Solutions"
    echo "==================================="
    echo
    echo "Access Information:"
    echo "  Web Interface: http://$(hostname -I | awk '{print $1}'):5000"
    echo "  SSH: ssh rpiplayer@$(hostname -I | awk '{print $1}')"
    echo "  Username: rpiplayer"
    echo "  Password: rpiplayer123"
    echo
    echo "Service Commands:"
    echo "  Start: sudo systemctl start v-player"
    echo "  Stop: sudo systemctl stop v-player"
    echo "  Restart: sudo systemctl restart v-player"
    echo "  Status: sudo systemctl status v-player"
    echo "  Logs: sudo journalctl -u v-player -f"
    echo
    echo "Configuration Files:"
    echo "  Application: $INSTALL_DIR"
    echo "  Nginx: /etc/nginx/sites-available/$NGINX_CONFIG"
    echo "  Service: /etc/systemd/system/$SYSTEMD_SERVICE"
    echo "  Boot: /boot/config.txt"
    echo
    echo "Features:"
    echo "  ✓ Professional V-Player branding"
    echo "  ✓ Splash screen disabled"
    echo "  ✓ Hardware acceleration enabled"
    echo "  ✓ Network management tools"
    echo "  ✓ WiFi hotspot support"
    echo "  ✓ Multiple streaming protocols"
    echo "  ✓ Web-based management interface"
    echo
    print_success "Installation complete! Reboot recommended."
}

# Main installation function
main() {
    echo "==================================="
    echo "V-Player Installation Script"
    echo "Professional Streaming Solution"
    echo "by Itassist Broadcast Solutions"
    echo "==================================="
    echo
    
    check_root
    detect_rpi_model
    
    print_status "Starting V-Player installation..."
    
    update_system
    install_dependencies
    create_user
    create_directories
    install_application
    install_python_deps
    configure_systemd
    configure_nginx
    configure_boot
    configure_ssh
    configure_sudoers
    create_rclocal
    start_services
    display_summary
    
    print_success "V-Player installation completed successfully!"
}

# Run main function
main "$@"
