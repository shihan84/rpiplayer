#!/bin/bash

# RPI Player Network Manager
# Comprehensive network configuration and management

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/etc/rpi-player"
NETWORK_CONFIG="$CONFIG_DIR/network.conf"
HOSTAPD_CONFIG="/etc/hostapd/hostapd.conf"
DNSMASQ_CONFIG="/etc/dnsmasq.conf"
INTERFACES_CONFIG="/etc/network/interfaces.d/rpi-player"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default network settings
DEFAULT_AP_SSID="RPI-Player"
DEFAULT_AP_PASSWORD="rpiplayer123"
DEFAULT_AP_CHANNEL="6"
DEFAULT_AP_IP="192.168.100.1"
DEFAULT_AP_RANGE="192.168.100.100,192.168.100.200,12h"

show_help() {
    echo "RPI Player Network Manager"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  setup-wifi        Configure WiFi connection"
    echo "  setup-ap          Configure WiFi Access Point"
    echo "  setup-ethernet    Configure Ethernet connection"
    echo "  toggle-mode       Switch between AP and client mode"
    echo "  status           Show network status"
    echo "  scan             Scan WiFi networks"
    echo "  test             Test network connectivity"
    echo "  optimize         Optimize network for streaming"
    echo "  backup           Backup network configuration"
    echo "  restore          Restore network configuration"
    echo "  reset            Reset to default settings"
    echo ""
    echo "Examples:"
    echo "  $0 setup-wifi"
    echo "  $0 setup-ap"
    echo "  $0 status"
    echo "  $0 optimize"
}

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

init_config() {
    mkdir -p "$CONFIG_DIR"
    
    if [ ! -f "$NETWORK_CONFIG" ]; then
        cat > "$NETWORK_CONFIG" << EOF
# RPI Player Network Configuration
MODE=client
WIFI_SSID=""
WIFI_PASSWORD=""
WIFI_COUNTRY="US"
AP_SSID="$DEFAULT_AP_SSID"
AP_PASSWORD="$DEFAULT_AP_PASSWORD"
AP_CHANNEL="$DEFAULT_AP_CHANNEL"
AP_IP="$DEFAULT_AP_IP"
AP_RANGE="$DEFAULT_AP_RANGE"
ETH_METHOD=dhcp
ETH_IP=""
ETH_NETMASK=""
ETH_GATEWAY=""
ETH_DNS=""
DNS_SERVERS="8.8.8.8,8.8.4.4"
NTP_SERVERS="0.pool.ntp.org,1.pool.ntp.org"
STREAMING_OPTIMIZATION=true
EOF
    fi
}

load_config() {
    if [ -f "$NETWORK_CONFIG" ]; then
        source "$NETWORK_CONFIG"
    else
        init_config
        source "$NETWORK_CONFIG"
    fi
}

save_config() {
    cat > "$NETWORK_CONFIG" << EOF
# RPI Player Network Configuration
MODE=$MODE
WIFI_SSID="$WIFI_SSID"
WIFI_PASSWORD="$WIFI_PASSWORD"
WIFI_COUNTRY="$WIFI_COUNTRY"
AP_SSID="$AP_SSID"
AP_PASSWORD="$AP_PASSWORD"
AP_CHANNEL="$AP_CHANNEL"
AP_IP="$AP_IP"
AP_RANGE="$AP_RANGE"
ETH_METHOD=$ETH_METHOD
ETH_IP="$ETH_IP"
ETH_NETMASK="$ETH_NETMASK"
ETH_GATEWAY="$ETH_GATEWAY"
ETH_DNS="$ETH_DNS"
DNS_SERVERS="$DNS_SERVERS"
NTP_SERVERS="$NTP_SERVERS"
STREAMING_OPTIMIZATION=$STREAMING_OPTIMIZATION
EOF
}

setup_wifi() {
    log "Setting up WiFi client configuration..."
    
    echo "Available WiFi networks:"
    wpa_cli scan_results 2>/dev/null | tail -n +2 | awk '{print $5}' | sort -u | nl
    
    echo ""
    read -p "Enter WiFi SSID: " ssid
    read -s -p "Enter WiFi password: " password
    echo ""
    read -p "Enter country code (default: US): " country
    country=${country:-US}
    
    # Update wpa_supplicant
    wpa_passphrase "$ssid" "$password" > /tmp/wpa_config.conf
    
    # Configure country code
    wpa_cli -i wlan0 set country "$country" 2>/dev/null || true
    iw reg set "$country"
    
    # Update configuration
    cat /tmp/wpa_config.conf > /etc/wpa_supplicant/wpa_supplicant.conf
    echo "country=$country" >> /etc/wpa_supplicant/wpa_supplicant.conf
    
    # Save to our config
    WIFI_SSID="$ssid"
    WIFI_PASSWORD="$password"
    WIFI_COUNTRY="$country"
    MODE="client"
    save_config
    
    # Restart networking
    systemctl restart wpa_supplicant
    systemctl restart networking
    
    log "WiFi configuration completed"
}

setup_ap() {
    log "Setting up WiFi Access Point..."
    
    echo "Current AP configuration:"
    echo "SSID: $AP_SSID"
    echo "Password: $AP_PASSWORD"
    echo "Channel: $AP_CHANNEL"
    echo "IP: $AP_IP"
    echo ""
    
    read -p "Use current settings? (Y/n): " use_current
    
    if [[ $use_current =~ ^[Nn]$ ]]; then
        read -p "Enter AP SSID (default: $DEFAULT_AP_SSID): " ssid
        read -s -p "Enter AP password (min 8 chars): " password
        echo ""
        read -p "Enter channel (1-13, default: 6): " channel
        
        AP_SSID=${ssid:-$DEFAULT_AP_SSID}
        AP_PASSWORD=${password:-$DEFAULT_AP_PASSWORD}
        AP_CHANNEL=${channel:-6}
        
        # Validate password
        if [ ${#AP_PASSWORD} -lt 8 ]; then
            error "Password must be at least 8 characters"
            return 1
        fi
    fi
    
    # Install required packages
    apt-get update
    apt-get install -y hostapd dnsmasq
    
    # Stop services
    systemctl stop hostapd
    systemctl stop dnsmasq
    
    # Configure hostapd
    cat > "$HOSTAPD_CONFIG" << EOF
interface=wlan0
driver=nl80211
ssid=$AP_SSID
hw_mode=g
channel=$AP_CHANNEL
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$AP_PASSWORD
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
    
    # Configure dnsmasq
    cat > "$DNSMASQ_CONFIG" << EOF
interface=wlan0
listen-address=$AP_IP
dhcp-range=$AP_RANGE
domain=local
server=$DNS_SERVERS
EOF
    
    # Configure static IP for wlan0
    cat > "$INTERFACES_CONFIG" << EOF
auto wlan0
iface wlan0 inet static
    address $AP_IP
    netmask 255.255.255.0
EOF
    
    # Enable IP forwarding
    sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
    sysctl -p
    
    # Configure NAT (if eth0 is available)
    if ip link show eth0 >/dev/null 2>&1; then
        iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        iptables-save > /etc/iptables.ipv4.nat
        
        # Restore iptables on boot
        cat > /etc/rc.local << 'EOF'
#!/bin/sh -e
iptables-restore < /etc/iptables.ipv4.nat
exit 0
EOF
        chmod +x /etc/rc.local
    fi
    
    # Enable and start services
    systemctl unmask hostapd
    systemctl enable hostapd
    systemctl enable dnsmasq
    systemctl start hostapd
    systemctl start dnsmasq
    
    # Update configuration
    MODE="ap"
    save_config
    
    log "Access Point configuration completed"
    log "SSID: $AP_SSID"
    log "Password: $AP_PASSWORD"
    log "Access IP: $AP_IP"
}

setup_ethernet() {
    log "Setting up Ethernet configuration..."
    
    echo "Available configuration methods:"
    echo "1) DHCP (automatic)"
    echo "2) Static IP"
    echo ""
    read -p "Select method (1-2): " method
    
    case $method in
        1)
            ETH_METHOD="dhcp"
            
            # Remove static configuration
            rm -f "$INTERFACES_CONFIG"
            
            # Configure DHCP
            cat > "$INTERFACES_CONFIG" << EOF
auto eth0
iface eth0 inet dhcp
EOF
            ;;
        2)
            read -p "Enter IP address: " ip
            read -p "Enter netmask (default: 255.255.255.0): " netmask
            read -p "Enter gateway: " gateway
            read -p "Enter DNS servers (comma separated): " dns
            
            ETH_METHOD="static"
            ETH_IP="$ip"
            ETH_NETMASK="${netmask:-255.255.255.0}"
            ETH_GATEWAY="$gateway"
            ETH_DNS="$dns"
            
            cat > "$INTERFACES_CONFIG" << EOF
auto eth0
iface eth0 inet static
    address $ETH_IP
    netmask $ETH_NETMASK
    gateway $ETH_GATEWAY
    dns-nameservers $ETH_DNS
EOF
            ;;
        *)
            error "Invalid method"
            return 1
            ;;
    esac
    
    # Restart networking
    systemctl restart networking
    
    save_config
    log "Ethernet configuration completed"
}

toggle_mode() {
    load_config
    
    log "Current mode: $MODE"
    
    if [ "$MODE" = "client" ]; then
        echo "Switching to Access Point mode..."
        setup_ap
    else
        echo "Switching to Client mode..."
        setup_wifi
    fi
}

show_status() {
    log "Network Status Report"
    echo "===================="
    
    load_config
    
    echo "Configuration Mode: $MODE"
    echo ""
    
    # Interface status
    echo "Interfaces:"
    ip addr show | grep -E "^[0-9]+:" | while read line; do
        interface=$(echo "$line" | cut -d: -f2 | tr -d ' ')
        status=$(ip link show "$interface" | grep -o "state [A-Z]*" | cut -d' ' -f2)
        ip_addr=$(ip addr show "$interface" | grep "inet " | awk '{print $2}' | head -1)
        echo "  $interface: $status ($ip_addr)"
    done
    echo ""
    
    # WiFi information
    if [ "$MODE" = "client" ] && [ -n "$WIFI_SSID" ]; then
        echo "WiFi Client:"
        echo "  SSID: $WIFI_SSID"
        echo "  Country: $WIFI_COUNTRY"
        wifi_quality=$(wpa_cli signal_poll 2>/dev/null | grep "RSSI" | awk '{print $2}' || echo "N/A")
        echo "  Signal: ${wifi_quality} dBm"
    elif [ "$MODE" = "ap" ]; then
        echo "Access Point:"
        echo "  SSID: $AP_SSID"
        echo "  Channel: $AP_CHANNEL"
        echo "  IP: $AP_IP"
        echo "  Connected clients: $(hostapd_cli all_sta 2>/dev/null | wc -l)"
    fi
    echo ""
    
    # Gateway and DNS
    echo "Routing:"
    ip route | grep default | head -1
    echo ""
    
    echo "DNS:"
    cat /etc/resolv.conf | grep nameserver
    echo ""
    
    # Network test
    echo "Connectivity Test:"
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        echo "  Internet: ✓ Connected"
    else
        echo "  Internet: ✗ Disconnected"
    fi
    
    if ping -c 1 google.com >/dev/null 2>&1; then
        echo "  DNS: ✓ Working"
    else
        echo "  DNS: ✗ Not working"
    fi
}

scan_networks() {
    log "Scanning WiFi networks..."
    
    # Enable interface if down
    ip link set wlan0 up 2>/dev/null || true
    
    # Scan
    wpa_cli scan 2>/dev/null || true
    sleep 3
    
    echo "Available networks:"
    wpa_cli scan_results 2>/dev/null | tail -n +2 | while read line; do
        bssid=$(echo "$line" | awk '{print $1}')
        frequency=$(echo "$line" | awk '{print $2}')
        signal=$(echo "$line" | awk '{print $3}')
        flags=$(echo "$line" | awk '{print $4}')
        ssid=$(echo "$line" | cut -d$'\t' -f5-)
        
        # Convert signal to quality
        if [ "$signal" -lt -50 ]; then
            quality="Excellent"
        elif [ "$signal" -lt -60 ]; then
            quality="Good"
        elif [ "$signal" -lt -70 ]; then
            quality="Fair"
        else
            quality="Poor"
        fi
        
        echo "  $ssid ($quality, ${signal} dBm)"
    done
}

test_connectivity() {
    log "Testing network connectivity..."
    
    echo "Testing local interfaces..."
    for interface in wlan0 eth0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            status=$(ip link show "$interface" | grep -o "state [A-Z]*" | cut -d' ' -f2)
            echo "  $interface: $status"
        fi
    done
    
    echo ""
    echo "Testing gateway connectivity..."
    gateway=$(ip route | grep default | awk '{print $3}' | head -1)
    if [ -n "$gateway" ]; then
        if ping -c 2 "$gateway" >/dev/null 2>&1; then
            echo "  Gateway ($gateway): ✓ Reachable"
        else
            echo "  Gateway ($gateway): ✗ Unreachable"
        fi
    else
        echo "  Gateway: ✗ Not configured"
    fi
    
    echo ""
    echo "Testing Internet connectivity..."
    if ping -c 2 8.8.8.8 >/dev/null 2>&1; then
        echo "  Internet (8.8.8.8): ✓ Reachable"
    else
        echo "  Internet (8.8.8.8): ✗ Unreachable"
    fi
    
    echo ""
    echo "Testing DNS resolution..."
    if nslookup google.com >/dev/null 2>&1; then
        echo "  DNS (google.com): ✓ Working"
    else
        echo "  DNS (google.com): ✗ Failed"
    fi
    
    echo ""
    echo "Testing streaming ports..."
    for port in 1935 5000 1234; do
        if netstat -ln | grep ":$port " >/dev/null; then
            echo "  Port $port: ✓ Open"
        else
            echo "  Port $port: ✗ Closed"
        fi
    done
}

optimize_network() {
    log "Optimizing network for streaming..."
    
    # Network kernel parameters
    cat >> /etc/sysctl.conf << 'EOF'

# Network optimization for streaming
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_tw_reuse = 1
EOF
    
    sysctl -p
    
    # Configure network interface optimizations
    for interface in wlan0 eth0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            # Increase txqueuelen
            ifconfig "$interface" txqueuelen 10000 2>/dev/null || true
            
            # Disable power management
            iwconfig "$interface" power off 2>/dev/null || true
        fi
    done
    
    # Configure QoS for streaming
    cat > /etc/rc.local << 'EOF'
#!/bin/sh -e
# Network optimizations for streaming
echo 'bbr' > /proc/sys/net/ipv4/tcp_congestion_control
echo 10000 > /proc/sys/net/core/netdev_max_backlog

# Restore iptables if exists
if [ -f /etc/iptables.ipv4.nat ]; then
    iptables-restore < /etc/iptables.ipv4.nat
fi

exit 0
EOF
    chmod +x /etc/rc.local
    
    # Update streaming optimization flag
    STREAMING_OPTIMIZATION=true
    save_config
    
    log "Network optimization completed"
}

backup_config() {
    local backup_dir="/home/rpiplayer/rpi-player/backups"
    local backup_file="$backup_dir/network-config-$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$backup_dir"
    
    tar -czf "$backup_file" \
        /etc/network/interfaces.d/ \
        /etc/wpa_supplicant/ \
        /etc/hostapd/ \
        /etc/dnsmasq.conf \
        /etc/sysctl.conf \
        "$CONFIG_DIR/" 2>/dev/null || true
    
    log "Network configuration backed up to: $backup_file"
}

restore_config() {
    local backup_dir="/home/rpiplayer/rpi-player/backups"
    
    echo "Available backups:"
    ls -1 "$backup_dir"/*.tar.gz 2>/dev/null | nl
    
    read -p "Select backup to restore: " backup_num
    
    backup_file=$(ls -1 "$backup_dir"/*.tar.gz 2>/dev/null | sed -n "${backup_num}p")
    
    if [ -f "$backup_file" ]; then
        tar -xzf "$backup_file" -C /
        
        # Restart networking
        systemctl restart networking
        systemctl restart wpa_supplicant
        systemctl restart hostapd 2>/dev/null || true
        systemctl restart dnsmasq 2>/dev/null || true
        
        log "Network configuration restored from: $backup_file"
    else
        error "Invalid backup selection"
    fi
}

reset_config() {
    warn "This will reset all network configurations to defaults"
    read -p "Continue? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        # Remove custom configurations
        rm -f /etc/network/interfaces.d/rpi-player
        rm -f /etc/hostapd/hostapd.conf
        rm -f /etc/dnsmasq.conf
        rm -f "$NETWORK_CONFIG"
        
        # Reset to default wpa_supplicant
        cat > /etc/wpa_supplicant/wpa_supplicant.conf << 'EOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
EOF
        
        # Disable services
        systemctl disable hostapd dnsmasq 2>/dev/null || true
        systemctl stop hostapd dnsmasq 2>/dev/null || true
        
        # Restart networking
        systemctl restart networking
        
        init_config
        log "Network configuration reset to defaults"
    fi
}

# Main script logic
case "${1:-help}" in
    setup-wifi)
        init_config
        setup_wifi
        ;;
    setup-ap)
        init_config
        setup_ap
        ;;
    setup-ethernet)
        init_config
        setup_ethernet
        ;;
    toggle-mode)
        load_config
        toggle_mode
        ;;
    status)
        show_status
        ;;
    scan)
        scan_networks
        ;;
    test)
        test_connectivity
        ;;
    optimize)
        init_config
        optimize_network
        ;;
    backup)
        backup_config
        ;;
    restore)
        restore_config
        ;;
    reset)
        reset_config
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
