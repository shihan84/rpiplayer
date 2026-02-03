#!/bin/bash

# RPI Player Network Optimizer
# Optimize network settings for streaming performance

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="/etc/rpi-player/network.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "RPI Player Network Optimizer"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  apply            Apply all network optimizations"
    echo "  kernel           Optimize kernel parameters"
    echo "  interfaces       Optimize network interfaces"
    echo "  wifi             Optimize WiFi settings"
    echo "  ethernet         Optimize Ethernet settings"
    echo "  streaming        Optimize for streaming protocols"
    echo "  qos              Configure QoS for streaming"
    echo "  reset            Reset to default settings"
    echo "  status           Show current optimization status"
    echo "  benchmark        Run network benchmark"
    echo "  silent           Apply optimizations silently"
    echo ""
    echo "Examples:"
    echo "  $0 apply"
    echo "  $0 streaming"
    echo "  $0 status"
}

load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    fi
}

backup_settings() {
    local backup_dir="/home/rpiplayer/rpi-player/backups"
    local backup_file="$backup_dir/network-settings-$(date +%Y%m%d_%H%M%S).backup"
    
    mkdir -p "$backup_dir"
    
    # Backup current settings
    {
        echo "# Network Settings Backup - $(date)"
        echo "# Kernel Parameters"
        sysctl -a | grep -E "(net\.|vm\.)" | sort
        
        echo "# Interface Settings"
        for interface in eth0 wlan0; do
            if ip link show "$interface" >/dev/null 2>&1; then
                echo "interface_$interface:"
                echo "  txqueuelen: $(cat /sys/class/net/$interface/tx_queue_len 2>/dev/null || echo 'N/A')"
                echo "  mtu: $(cat /sys/class/net/$interface/mtu 2>/dev/null || echo 'N/A')"
            fi
        done
        
        echo "# WiFi Settings"
        if command -v iwconfig >/dev/null 2>&1; then
            iwconfig wlan0 2>/dev/null || true
        fi
        
        echo "# QoS Settings"
        tc qdisc show 2>/dev/null || true
        
    } > "$backup_file"
    
    log "Settings backed up to: $backup_file"
}

optimize_kernel_parameters() {
    log "Optimizing kernel parameters for streaming..."
    
    # Network buffer sizes
    sysctl -w net.core.rmem_max=16777216
    sysctl -w net.core.wmem_max=16777216
    sysctl -w net.core.rmem_default=262144
    sysctl -w net.core.wmem_default=262144
    sysctl -w net.core.netdev_max_backlog=5000
    
    # TCP parameters
    sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
    sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
    sysctl -w net.ipv4.tcp_congestion_control=bbr
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0
    sysctl -w net.ipv4.tcp_tw_reuse=1
    sysctl -w net.ipv4.tcp_fin_timeout=15
    sysctl -w net.ipv4.tcp_keepalive_time=600
    sysctl -w net.ipv4.tcp_keepalive_intvl=60
    sysctl -w net.ipv4.tcp_keepalive_probes=3
    
    # UDP parameters for streaming
    sysctl -w net.core.rmem_default=262144
    sysctl -w net.core.wmem_default=262144
    sysctl -w net.ipv4.udp_rmem_min=8192
    sysctl -w net.ipv4.udp_wmem_min=8192
    
    # Memory management
    sysctl -w vm.swappiness=10
    sysctl -w vm.dirty_ratio=15
    sysctl -w vm.dirty_background_ratio=5
    
    # Make settings persistent
    cat >> /etc/sysctl.conf << 'EOF'

# RPI Player Streaming Optimizations
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.core.rmem_default = 262144
net.core.wmem_default = 262144
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.udp_rmem_min = 8192
net.ipv4.udp_wmem_min = 8192
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF
    
    log "Kernel parameters optimized"
}

optimize_interfaces() {
    log "Optimizing network interfaces..."
    
    for interface in eth0 wlan0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            log "Optimizing interface: $interface"
            
            # Increase TX queue length
            echo 10000 > /sys/class/net/$interface/tx_queue_len 2>/dev/null || true
            
            # Set MTU for optimal performance
            if [[ "$interface" == eth* ]]; then
                # Ethernet - use standard MTU
                ip link set "$interface" mtu 1500 2>/dev/null || true
            elif [[ "$interface" == wlan* ]]; then
                # WiFi - use slightly lower MTU to account for overhead
                ip link set "$interface" mtu 1400 2>/dev/null || true
            fi
            
            # Disable generic receive offload (can cause issues with streaming)
            ethtool -K "$interface" gro off 2>/dev/null || true
            ethtool -K "$interface" lro off 2>/dev/null || true
            
            # Enable scatter-gather
            ethtool -K "$interface" sg on 2>/dev/null || true
            
            log "Interface $interface optimized"
        fi
    done
}

optimize_wifi() {
    log "Optimizing WiFi settings..."
    
    if ! ip link show wlan0 >/dev/null 2>&1; then
        warn "WiFi interface not found"
        return
    fi
    
    # Disable power management
    iwconfig wlan0 power off 2>/dev/null || true
    
    # Set regulatory domain
    iw reg set US 2>/dev/null || true
    
    # Optimize WiFi module parameters
    if [ -d /sys/module/8192cu ]; then
        echo 1 > /sys/module/8192cu/parameters/rtw_power_mgnt 2>/dev/null || true
    fi
    
    # Configure WiFi for better performance
    if command -v iw >/dev/null 2>&1; then
        # Set bitrates to auto for best performance
        iw wlan0 set bitrates legacy-2.4 2>/dev/null || true
        
        # Enable HT mode (802.11n) if supported
        iw wlan0 set htmode HT20 2>/dev/null || true
    fi
    
    # Add WiFi optimizations to modprobe config
    cat >> /etc/modprobe.d/rpi-player-wifi.conf << 'EOF'
# RPI Player WiFi Optimizations
options 8192cu rtw_power_mgnt=0
options 8723bs rtw_power_mgnt=0
EOF
    
    log "WiFi settings optimized"
}

optimize_ethernet() {
    log "Optimizing Ethernet settings..."
    
    if ! ip link show eth0 >/dev/null 2>&1; then
        warn "Ethernet interface not found"
        return
    fi
    
    # Check cable connection
    local carrier=$(cat /sys/class/net/eth0/carrier 2>/dev/null || echo "0")
    if [ "$carrier" = "1" ]; then
        # Enable jumbo frames if supported
        local mtu=$(cat /sys/class/net/eth0/mtu 2>/dev/null || echo "1500")
        if [ "$mtu" = "1500" ]; then
            # Try to increase MTU for better performance
            ip link set eth0 mtu 9000 2>/dev/null || log "Jumbo frames not supported"
        fi
        
        # Enable Ethernet offload features
        ethtool -K eth0 tso on 2>/dev/null || true
        ethtool -K eth0 gso on 2>/dev/null || true
        ethtool -K eth0 tx on 2>/dev/null || true
        
        # Set interface to full duplex if not already
        local duplex=$(ethtool eth0 2>/dev/null | grep "Duplex:" | cut -d: -f2 | tr -d ' ')
        if [ "$duplex" = "Half" ]; then
            ethtool -s eth0 autoneg off speed 1000 duplex full 2>/dev/null || true
        fi
        
        log "Ethernet settings optimized"
    else
        warn "Ethernet cable not connected"
    fi
}

optimize_streaming() {
    log "Optimizing for streaming protocols..."
    
    # Configure network for low latency
    sysctl -w net.ipv4.tcp_low_latency=1 2>/dev/null || true
    
    # Increase file descriptor limits
    echo "* soft nofile 65536" >> /etc/security/limits.conf
    echo "* hard nofile 65536" >> /etc/security/limits.conf
    
    # Optimize for UDP streaming (SRT, RTP)
    sysctl -w net.ipv4.udp_mem="102400 873800 16777216"
    sysctl -w net.ipv4.udp_rmem_min=8192
    sysctl -w net.ipv4.udp_wmem_min=8192
    
    # Configure for RTMP streaming
    sysctl -w net.ipv4.tcp_fin_timeout=15
    sysctl -w net.ipv4.tcp_keepalive_time=600
    sysctl -w net.ipv4.tcp_keepalive_intvl=60
    sysctl -w net.ipv4.tcp_keepalive_probes=3
    
    # Optimize for HLS streaming
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0
    sysctl -w net.ipv4.tcp_tw_reuse=1
    
    log "Streaming optimizations applied"
}

configure_qos() {
    log "Configuring QoS for streaming..."
    
    # Install tc if not available
    if ! command -v tc >/dev/null 2>&1; then
        apt-get update
        apt-get install -y iproute2
    fi
    
    # Clear existing QoS rules
    tc qdisc del dev eth0 root 2>/dev/null || true
    tc qdisc del dev wlan0 root 2>/dev/null || true
    
    # Configure QoS for streaming traffic
    for interface in eth0 wlan0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            # Create root qdisc
            tc qdisc add dev "$interface" root handle 1: htb default 30
            
            # Create main class
            tc class add dev "$interface" parent 1: classid 1:1 htb rate 1000mbit ceil 1000mbit
            
            # Create high priority class for streaming (RTMP, SRT, UDP)
            tc class add dev "$interface" parent 1:1 classid 1:10 htb rate 500mbit ceil 800mbit prio 1
            
            # Create medium priority class for web traffic
            tc class add dev "$interface" parent 1:1 classid 1:20 htb rate 300mbit ceil 500mbit prio 2
            
            # Create low priority class for bulk traffic
            tc class add dev "$interface" parent 1:1 classid 1:30 htb rate 200mbit ceil 300mbit prio 3
            
            # Add filters for streaming protocols
            tc filter add dev "$interface" parent 1:0 protocol ip prio 1 u32 match ip dport 1935 0xffff flowid 1:10  # RTMP
            tc filter add dev "$interface" parent 1:0 protocol ip prio 1 u32 match ip dport 1234 0xffff flowid 1:10  # SRT
            tc filter add dev "$interface" parent 1:0 protocol ip prio 1 u32 match ip dport 5004 0xffff flowid 1:10  # RTP
            tc filter add dev "$interface" parent 1:0 protocol ip prio 1 u32 match ip protocol 17 0xff flowid 1:10  # UDP
            
            # Add filter for web traffic
            tc filter add dev "$interface" parent 1:0 protocol ip prio 2 u32 match ip dport 80 0xffff flowid 1:20
            tc filter add dev "$interface" parent 1:0 protocol ip prio 2 u32 match ip dport 443 0xffff flowid 1:20
            
            log "QoS configured for $interface"
        fi
    done
    
    # Save QoS rules for persistence
    cat > /etc/network/if-up.d/rpi-player-qos << 'EOF'
#!/bin/sh
# Apply QoS rules on interface up

if [ "$IFACE" = "eth0" ] || [ "$IFACE" = "wlan0" ]; then
    # QoS rules will be applied by network-optimizer.sh
    /home/rpiplayer/rpi-player/network-optimizer.sh qos
fi
EOF
    chmod +x /etc/network/if-up.d/rpi-player-qos
    
    log "QoS configuration completed"
}

reset_optimizations() {
    log "Resetting network optimizations..."
    
    # Reset kernel parameters to defaults
    sysctl -w net.core.rmem_max=212992
    sysctl -w net.core.wmem_max=212992
    sysctl -w net.core.rmem_default=212992
    sysctl -w net.core.wmem_default=212992
    sysctl -w net.core.netdev_max_backlog=1000
    sysctl -w net.ipv4.tcp_rmem="4096 87380 6291456"
    sysctl -w net.ipv4.tcp_wmem="4096 65536 6291456"
    sysctl -w net.ipv4.tcp_congestion_control=cubic
    sysctl -w net.ipv4.tcp_slow_start_after_idle=1
    sysctl -w net.ipv4.tcp_tw_reuse=0
    
    # Reset interface settings
    for interface in eth0 wlan0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            ip link set "$interface" mtu 1500 2>/dev/null || true
            echo 1000 > /sys/class/net/$interface/tx_queue_len 2>/dev/null || true
        fi
    done
    
    # Clear QoS rules
    tc qdisc del dev eth0 root 2>/dev/null || true
    tc qdisc del dev wlan0 root 2>/dev/null || true
    
    # Remove optimization files
    rm -f /etc/modprobe.d/rpi-player-wifi.conf
    rm -f /etc/network/if-up.d/rpi-player-qos
    
    # Remove sysctl optimizations
    sed -i '/# RPI Player Streaming Optimizations/,/^$/d' /etc/sysctl.conf
    
    log "Network optimizations reset to defaults"
}

show_status() {
    log "Network Optimization Status"
    echo "=========================="
    
    # Check kernel parameters
    echo "Kernel Parameters:"
    echo "  rmem_max: $(sysctl -n net.core.rmem_max)"
    echo "  wmem_max: $(sysctl -n net.core.wmem_max)"
    echo "  netdev_max_backlog: $(sysctl -n net.core.netdev_max_backlog)"
    echo "  tcp_congestion_control: $(sysctl -n net.ipv4.tcp_congestion_control)"
    echo ""
    
    # Check interface settings
    echo "Interface Settings:"
    for interface in eth0 wlan0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            echo "  $interface:"
            echo "    MTU: $(cat /sys/class/net/$interface/mtu 2>/dev/null || echo 'N/A')"
            echo "    TX Queue: $(cat /sys/class/net/$interface/tx_queue_len 2>/dev/null || echo 'N/A')"
            echo "    Status: $(ip link show "$interface" | grep -o 'state [A-Z]*' | cut -d' ' -f2)"
        fi
    done
    echo ""
    
    # Check QoS status
    echo "QoS Status:"
    for interface in eth0 wlan0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            local qdisc=$(tc qdisc show dev "$interface" 2>/dev/null)
            if [ -n "$qdisc" ]; then
                echo "  $interface: Configured"
            else
                echo "  $interface: Not configured"
            fi
        fi
    done
    echo ""
    
    # Check WiFi settings
    if ip link show wlan0 >/dev/null 2>&1; then
        echo "WiFi Settings:"
        local power_mgmt=$(iwconfig wlan0 2>/dev/null | grep "Power Management" | cut -d: -f2 | tr -d ' ')
        echo "  Power Management: $power_mgmt"
    fi
}

run_benchmark() {
    log "Running Network Benchmark"
    echo "======================="
    
    # Test latency
    echo "Latency Test:"
    ping -c 10 -W 2 8.8.8.8 | tail -1
    
    echo ""
    
    # Test bandwidth
    echo "Bandwidth Test:"
    if command -v wget >/dev/null 2>&1; then
        echo "Download test..."
        timeout 30 wget -O /dev/null http://speedtest.wdc01.softlayer.com/downloads/test10.zip 2>&1 | grep -o "[0-9.]* MB/s" || echo "Test failed"
    fi
    
    echo ""
    
    # Test concurrent connections
    echo "Connection Test:"
    echo "Testing 10 concurrent connections..."
    for i in {1..10}; do
        (ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1 && echo -n "✓" || echo -n "✗") &
    done
    wait
    echo ""
    
    # Test streaming performance
    echo "Streaming Performance:"
    echo "Testing UDP packet loss..."
    if command -v hping3 >/dev/null 2>&1; then
        hping3 -c 100 -i u 8.8.8.8 2>/dev/null | grep "packets transmitted" || echo "Test failed"
    else
        echo "hping3 not available for UDP test"
    fi
}

apply_all_optimizations() {
    log "Applying all network optimizations..."
    
    backup_settings
    optimize_kernel_parameters
    optimize_interfaces
    optimize_wifi
    optimize_ethernet
    optimize_streaming
    configure_qos
    
    log "All network optimizations applied successfully"
}

# Main script logic
case "${1:-apply}" in
    apply)
        apply_all_optimizations
        ;;
    kernel)
        optimize_kernel_parameters
        ;;
    interfaces)
        optimize_interfaces
        ;;
    wifi)
        optimize_wifi
        ;;
    ethernet)
        optimize_ethernet
        ;;
    streaming)
        optimize_streaming
        ;;
    qos)
        configure_qos
        ;;
    reset)
        reset_optimizations
        ;;
    status)
        show_status
        ;;
    benchmark)
        run_benchmark
        ;;
    silent)
        # Apply optimizations without output
        backup_settings >/dev/null 2>&1
        optimize_kernel_parameters >/dev/null 2>&1
        optimize_interfaces >/dev/null 2>&1
        optimize_wifi >/dev/null 2>&1
        optimize_ethernet >/dev/null 2>&1
        optimize_streaming >/dev/null 2>&1
        configure_qos >/dev/null 2>&1
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
