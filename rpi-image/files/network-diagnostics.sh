#!/bin/bash

# RPI Player Network Diagnostics
# Comprehensive network testing and troubleshooting

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/network-diagnostics.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create logs directory
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

show_help() {
    echo "RPI Player Network Diagnostics"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  full             Run complete diagnostics"
    echo "  interfaces       Test network interfaces"
    echo "  connectivity     Test internet connectivity"
    echo "  dns              Test DNS resolution"
    echo "  streaming        Test streaming-specific connectivity"
    echo "  performance      Test network performance"
    echo "  wifi             Test WiFi connectivity"
    echo "  ethernet         Test Ethernet connectivity"
    echo "  ports            Test port accessibility"
    echo "  bandwidth        Test bandwidth speed"
    echo "  latency          Test network latency"
    echo "  monitor          Monitor network in real-time"
    echo "  report           Generate diagnostic report"
    echo "  startup          Run startup diagnostics"
    echo ""
    echo "Options:"
    echo "  --verbose        Verbose output"
    echo "  --quiet          Quiet mode (errors only)"
    echo "  --json           JSON output"
    echo "  --save           Save results to file"
    echo ""
    echo "Examples:"
    echo "  $0 full"
    echo "  $0 streaming --verbose"
    echo "  $0 connectivity --json"
    echo "  $0 monitor"
}

# Initialize results tracking
declare -A RESULTS
RESULTS["total"]=0
RESULTS["passed"]=0
RESULTS["failed"]=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"
    
    RESULTS["total"]=$((RESULTS["total"] + 1))
    
    echo -n "Testing $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        local actual_result=$?
        if [ $actual_result -eq $expected_result ]; then
            echo -e "${GREEN}PASS${NC}"
            RESULTS["passed"]=$((RESULTS["passed"] + 1))
            RESULTS["$test_name"]="PASS"
        else
            echo -e "${RED}FAIL${NC} (exit code: $actual_result)"
            RESULTS["failed"]=$((RESULTS["failed"] + 1))
            RESULTS["$test_name"]="FAIL"
        fi
    else
        echo -e "${RED}FAIL${NC}"
        RESULTS["failed"]=$((RESULTS["failed"] + 1))
        RESULTS["$test_name"]="FAIL"
    fi
}

test_interfaces() {
    log "Testing Network Interfaces"
    echo "========================"
    
    # Test physical interfaces
    for interface in eth0 wlan0 wlan1; do
        if ip link show "$interface" >/dev/null 2>&1; then
            echo "Interface $interface exists"
            
            # Test if interface is up
            if ip link show "$interface" | grep -q "state UP"; then
                echo "  Status: UP"
                RESULTS["${interface}_status"]="UP"
            else
                echo "  Status: DOWN"
                RESULTS["${interface}_status"]="DOWN"
            fi
            
            # Test IP address
            local ip_addr=$(ip addr show "$interface" | grep "inet " | awk '{print $2}' | head -1)
            if [ -n "$ip_addr" ]; then
                echo "  IP Address: $ip_addr"
                RESULTS["${interface}_ip"]="$ip_addr"
            else
                echo "  IP Address: None"
                RESULTS["${interface}_ip"]="None"
            fi
            
            # Test MAC address
            local mac_addr=$(ip link show "$interface" | grep -o "link/ether [^ ]*" | cut -d' ' -f2)
            if [ -n "$mac_addr" ]; then
                echo "  MAC Address: $mac_addr"
                RESULTS["${interface}_mac"]="$mac_addr"
            fi
            
            # Test interface speed (Ethernet only)
            if [[ "$interface" == eth* ]]; then
                local speed=$(ethtool "$interface" 2>/dev/null | grep "Speed:" | cut -d: -f2 | tr -d ' ')
                if [ -n "$speed" ]; then
                    echo "  Speed: $speed"
                    RESULTS["${interface}_speed"]="$speed"
                fi
            fi
            
            # Test WiFi signal (WiFi only)
            if [[ "$interface" == wlan* ]]; then
                local signal=$(iwconfig "$interface" 2>/dev/null | grep "Signal level" | grep -o "Signal level=[^ ]*" | cut -d= -f2)
                if [ -n "$signal" ]; then
                    echo "  Signal: $signal"
                    RESULTS["${interface}_signal"]="$signal"
                fi
                
                # Test WiFi SSID
                local ssid=$(iwconfig "$interface" 2>/dev/null | grep "ESSID:" | cut -d: -f2 | tr -d '"')
                if [ -n "$ssid" ]; then
                    echo "  SSID: $ssid"
                    RESULTS["${interface}_ssid"]="$ssid"
                fi
            fi
            
            echo ""
        fi
    done
}

test_connectivity() {
    log "Testing Internet Connectivity"
    echo "==========================="
    
    # Test default gateway
    local gateway=$(ip route | grep default | awk '{print $3}' | head -1)
    if [ -n "$gateway" ]; then
        echo "Default Gateway: $gateway"
        
        if ping -c 2 -W 2 "$gateway" >/dev/null 2>&1; then
            echo "  Gateway: ${GREEN}REACHABLE${NC}"
            RESULTS["gateway"]="REACHABLE"
        else
            echo "  Gateway: ${RED}UNREACHABLE${NC}"
            RESULTS["gateway"]="UNREACHABLE"
        fi
    else
        echo "Default Gateway: ${RED}NOT CONFIGURED${NC}"
        RESULTS["gateway"]="NOT_CONFIGURED"
    fi
    
    echo ""
    
    # Test external connectivity
    local test_hosts=("8.8.8.8" "1.1.1.1" "208.67.222.222")
    for host in "${test_hosts[@]}"; do
        echo -n "Testing $host... "
        if ping -c 2 -W 3 "$host" >/dev/null 2>&1; then
            echo -e "${GREEN}REACHABLE${NC}"
            RESULTS["external_${host//./_}"]="REACHABLE"
        else
            echo -e "${RED}UNREACHABLE${NC}"
            RESULTS["external_${host//./_}"]="UNREACHABLE"
        fi
    done
    
    echo ""
    
    # Test internet connectivity
    if ping -c 1 -W 3 google.com >/dev/null 2>&1; then
        echo "Internet: ${GREEN}CONNECTED${NC}"
        RESULTS["internet"]="CONNECTED"
    else
        echo "Internet: ${RED}DISCONNECTED${NC}"
        RESULTS["internet"]="DISCONNECTED"
    fi
}

test_dns() {
    log "Testing DNS Resolution"
    echo "===================="
    
    # Get DNS servers
    local dns_servers=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    echo "DNS Servers: $dns_servers"
    
    echo ""
    
    # Test DNS resolution
    local test_domains=("google.com" "github.com" "ffmpeg.org")
    for domain in "${test_domains[@]}"; do
        echo -n "Resolving $domain... "
        if nslookup "$domain" >/dev/null 2>&1; then
            local resolved_ip=$(nslookup "$domain" | grep -A 1 "Name:" | tail -1 | awk '{print $2}')
            echo -e "${GREEN}SUCCESS${NC} ($resolved_ip)"
            RESULTS["dns_${domain//./_}"]="SUCCESS"
        else
            echo -e "${RED}FAILED${NC}"
            RESULTS["dns_${domain//./_}"]="FAILED"
        fi
    done
    
    echo ""
    
    # Test reverse DNS
    local test_ip="8.8.8.8"
    echo -n "Reverse DNS for $test_ip... "
    if nslookup "$test_ip" >/dev/null 2>&1; then
        local reverse_name=$(nslookup "$test_ip" | grep -A 1 "8.8.8.8" | tail -1 | awk '{print $4}')
        echo -e "${GREEN}SUCCESS${NC} ($reverse_name)"
        RESULTS["reverse_dns_8_8_8_8"]="SUCCESS"
    else
        echo -e "${RED}FAILED${NC}"
        RESULTS["reverse_dns_8_8_8_8"]="FAILED"
    fi
}

test_streaming() {
    log "Testing Streaming Connectivity"
    echo "============================"
    
    # Test streaming ports
    local streaming_ports=(1935 5000 1234 5004 8080 9000)
    echo "Testing streaming ports:"
    
    for port in "${streaming_ports[@]}"; do
        echo -n "  Port $port... "
        if netstat -ln | grep ":$port " >/dev/null 2>&1; then
            echo -e "${GREEN}OPEN${NC}"
            RESULTS["port_$port"]="OPEN"
        else
            echo -e "${YELLOW}CLOSED${NC}"
            RESULTS["port_$port"]="CLOSED"
        fi
    done
    
    echo ""
    
    # Test streaming protocols
    echo "Testing streaming protocols:"
    
    # Test RTMP connectivity
    echo -n "  RTMP (1935)... "
    if timeout 5 bash -c "</dev/tcp/127.0.0.1/1935" 2>/dev/null; then
        echo -e "${GREEN}AVAILABLE${NC}"
        RESULTS["protocol_rtmp"]="AVAILABLE"
    else
        echo -e "${YELLOW}NOT AVAILABLE${NC}"
        RESULTS["protocol_rtmp"]="NOT_AVAILABLE"
    fi
    
    # Test SRT connectivity
    echo -n "  SRT (1234)... "
    if timeout 5 bash -c "</dev/tcp/127.0.0.1/1234" 2>/dev/null; then
        echo -e "${GREEN}AVAILABLE${NC}"
        RESULTS["protocol_srt"]="AVAILABLE"
    else
        echo -e "${YELLOW}NOT AVAILABLE${NC}"
        RESULTS["protocol_srt"]="NOT_AVAILABLE"
    fi
    
    # Test UDP connectivity
    echo -n "  UDP (5004)... "
    if netstat -lu | grep ":5004" >/dev/null 2>&1; then
        echo -e "${GREEN}AVAILABLE${NC}"
        Results["protocol_udp"]="AVAILABLE"
    else
        echo -e "${YELLOW}NOT AVAILABLE${NC}"
        RESULTS["protocol_udp"]="NOT_AVAILABLE"
    fi
    
    echo ""
    
    # Test bandwidth requirements
    echo "Testing bandwidth requirements:"
    
    # Test upload capacity
    echo -n "  Upload capacity... "
    local upload_test=$(timeout 10 dd if=/dev/zero bs=1M count=10 2>/dev/null | nc -l 5005 >/dev/null 2>&1 &)
    sleep 1
    if timeout 5 bash -c "</dev/tcp/127.0.0.1/5005" 2>/dev/null; then
        echo -e "${GREEN}SUFFICIENT${NC}"
        RESULTS["bandwidth_upload"]="SUFFICIENT"
    else
        echo -e "${YELLOW}UNKNOWN${NC}"
        RESULTS["bandwidth_upload"]="UNKNOWN"
    fi
    killall nc 2>/dev/null || true
}

test_performance() {
    log "Testing Network Performance"
    echo "=========================="
    
    # Test latency to common hosts
    local test_hosts=("8.8.8.8" "1.1.1.1" "google.com")
    echo "Latency Test:"
    
    for host in "${test_hosts[@]}"; do
        echo -n "  $host... "
        local ping_result=$(ping -c 3 -W 2 "$host" 2>/dev/null | tail -1)
        if [ $? -eq 0 ]; then
            local avg_latency=$(echo "$ping_result" | grep -o "avg = [0-9.]*" | cut -d= -f2 | tr -d ' ')
            echo -e "${GREEN}${avg_latency} ms${NC}"
            RESULTS["latency_${host//./_}"]="$avg_latency"
        else
            echo -e "${RED}FAILED${NC}"
            RESULTS["latency_${host//./_}"]="FAILED"
        fi
    done
    
    echo ""
    
    # Test jitter
    echo "Jitter Test:"
    local jitter_test=$(ping -c 10 -W 2 8.8.8.8 2>/dev/null)
    if [ $? -eq 0 ]; then
        local jitter=$(echo "$jitter_test" | grep "mdev" | awk '{print $4}' | tr -d ' ')
        echo -e "  Jitter: ${GREEN}${jitter} ms${NC}"
        RESULTS["jitter_8_8_8_8"]="$jitter"
    else
        echo -e "  Jitter: ${RED}FAILED${NC}"
        RESULTS["jitter_8_8_8_8"]="FAILED"
    fi
    
    echo ""
    
    # Test packet loss
    echo "Packet Loss Test:"
    local packet_loss_test=$(ping -c 20 -W 2 8.8.8.8 2>/dev/null)
    if [ $? -eq 0 ]; then
        local packet_loss=$(echo "$packet_loss_test" | grep "packet loss" | grep -o "[0-9]*%" | tr -d '%')
        echo -e "  Packet Loss: ${GREEN}${packet_loss}%${NC}"
        RESULTS["packet_loss_8_8_8_8"]="$packet_loss"
    else
        echo -e "  Packet Loss: ${RED}FAILED${NC}"
        RESULTS["packet_loss_8_8_8_8"]="FAILED"
    fi
}

test_wifi() {
    log "Testing WiFi Connectivity"
    echo "======================="
    
    # Check WiFi interface
    if ! ip link show wlan0 >/dev/null 2>&1; then
        echo "WiFi interface not found"
        RESULTS["wifi_interface"]="NOT_FOUND"
        return
    fi
    
    echo "WiFi interface: wlan0"
    
    # Test WiFi driver
    echo -n "WiFi driver... "
    if iwconfig wlan0 >/dev/null 2>&1; then
        echo -e "${GREEN}LOADED${NC}"
        RESULTS["wifi_driver"]="LOADED"
    else
        echo -e "${RED}NOT LOADED${NC}"
        RESULTS["wifi_driver"]="NOT_LOADED"
    fi
    
    # Test WiFi connection
    echo -n "WiFi connection... "
    local wifi_ssid=$(iwconfig wlan0 2>/dev/null | grep "ESSID:" | cut -d: -f2 | tr -d '"')
    if [ -n "$wifi_ssid" ] && [ "$wifi_ssid" != "off/any" ]; then
        echo -e "${GREEN}CONNECTED${NC} ($wifi_ssid)"
        RESULTS["wifi_connection"]="CONNECTED"
        RESULTS["wifi_ssid"]="$wifi_ssid"
    else
        echo -e "${RED}NOT CONNECTED${NC}"
        RESULTS["wifi_connection"]="NOT_CONNECTED"
    fi
    
    # Test WiFi signal
    echo -n "WiFi signal... "
    local wifi_signal=$(iwconfig wlan0 2>/dev/null | grep "Signal level" | grep -o "Signal level=[^ ]*" | cut -d= -f2)
    if [ -n "$wifi_signal" ]; then
        echo -e "${GREEN}$wifi_signal${NC}"
        RESULTS["wifi_signal"]="$wifi_signal"
    else
        echo -e "${YELLOW}UNKNOWN${NC}"
        RESULTS["wifi_signal"]="UNKNOWN"
    fi
    
    # Test WiFi scan
    echo -n "WiFi scan capability... "
    if iwlist wlan0 scan >/dev/null 2>&1; then
        echo -e "${GREEN}WORKING${NC}"
        RESULTS["wifi_scan"]="WORKING"
        
        # Count available networks
        local network_count=$(iwlist wlan0 scan 2>/dev/null | grep -c "ESSID:" || echo "0")
        echo "  Available networks: $network_count"
        RESULTS["wifi_network_count"]="$network_count"
    else
        echo -e "${RED}NOT WORKING${NC}"
        RESULTS["wifi_scan"]="NOT_WORKING"
    fi
}

test_ethernet() {
    log "Testing Ethernet Connectivity"
    echo "==========================="
    
    # Check Ethernet interface
    if ! ip link show eth0 >/dev/null 2>&1; then
        echo "Ethernet interface not found"
        RESULTS["ethernet_interface"]="NOT_FOUND"
        return
    fi
    
    echo "Ethernet interface: eth0"
    
    # Test cable connection
    echo -n "Cable connection... "
    local carrier=$(cat /sys/class/net/eth0/carrier 2>/dev/null || echo "0")
    if [ "$carrier" = "1" ]; then
        echo -e "${GREEN}CONNECTED${NC}"
        RESULTS["ethernet_cable"]="CONNECTED"
    else
        echo -e "${RED}NOT CONNECTED${NC}"
        RESULTS["ethernet_cable"]="NOT_CONNECTED"
    fi
    
    # Test link speed
    echo -n "Link speed... "
    local speed=$(ethtool eth0 2>/dev/null | grep "Speed:" | cut -d: -f2 | tr -d ' ')
    if [ -n "$speed" ]; then
        echo -e "${GREEN}$speed${NC}"
        RESULTS["ethernet_speed"]="$speed"
    else
        echo -e "${YELLOW}UNKNOWN${NC}"
        RESULTS["ethernet_speed"]="UNKNOWN"
    fi
    
    # Test duplex mode
    echo -n "Duplex mode... "
    local duplex=$(ethtool eth0 2>/dev/null | grep "Duplex:" | cut -d: -f2 | tr -d ' ')
    if [ -n "$duplex" ]; then
        echo -e "${GREEN}$duplex${NC}"
        RESULTS["ethernet_duplex"]="$duplex"
    else
        echo -e "${YELLOW}UNKNOWN${NC}"
        RESULTS["ethernet_duplex"]="UNKNOWN"
    fi
}

test_bandwidth() {
    log "Testing Bandwidth Speed"
    echo "====================="
    
    # Test download speed
    echo -n "Download speed test... "
    local download_result=$(timeout 30 wget -O /dev/null http://speedtest.wdc01.softlayer.com/downloads/test10.zip 2>&1 | grep -o "[0-9.]* MB/s" | tail -1)
    if [ -n "$download_result" ]; then
        echo -e "${GREEN}$download_result${NC}"
        RESULTS["bandwidth_download"]="$download_result"
    else
        echo -e "${YELLOW}FAILED${NC}"
        RESULTS["bandwidth_download"]="FAILED"
    fi
    
    # Test upload speed (basic test)
    echo -n "Upload speed test... "
    local upload_test=$(timeout 10 dd if=/dev/zero bs=1M count=5 2>/dev/null | nc -l 5006 >/dev/null 2>&1 &)
    sleep 1
    local upload_result=$(timeout 5 dd if=/dev/zero bs=1M count=1 2>/dev/null | nc 127.0.0.1 5006 2>&1 | grep -o "[0-9.]* MB/s" || echo "")
    killall nc 2>/dev/null || true
    
    if [ -n "$upload_result" ]; then
        echo -e "${GREEN}$upload_result${NC}"
        RESULTS["bandwidth_upload"]="$upload_result"
    else
        echo -e "${YELLOW}UNKNOWN${NC}"
        RESULTS["bandwidth_upload"]="UNKNOWN"
    fi
}

monitor_network() {
    log "Real-time Network Monitoring"
    echo "==========================="
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    while true; do
        clear
        
        # System time
        echo "Time: $(date)"
        echo ""
        
        # Interface status
        echo "Interface Status:"
        for interface in eth0 wlan0; do
            if ip link show "$interface" >/dev/null 2>&1; then
                local status=$(ip link show "$interface" | grep -o "state [A-Z]*" | cut -d' ' -f2)
                local ip_addr=$(ip addr show "$interface" | grep "inet " | awk '{print $2}' | head -1)
                echo "  $interface: $status ($ip_addr)"
            fi
        done
        echo ""
        
        # Network traffic
        echo "Network Traffic:"
        local net_io=$(cat /proc/net/dev | grep -E "(eth0|wlan0)")
        echo "$net_io" | while read line; do
            local interface=$(echo "$line" | cut -d: -f1 | tr -d ' ')
            local rx_bytes=$(echo "$line" | awk '{print $2}')
            local tx_bytes=$(echo "$line" | awk '{print $10}')
            
            # Convert to MB
            local rx_mb=$((rx_bytes / 1024 / 1024))
            local tx_mb=$((tx_bytes / 1024 / 1024))
            
            echo "  $interface: RX ${rx_mb}MB, TX ${tx_mb}MB"
        done
        echo ""
        
        # Active connections
        echo "Active Connections: $(netstat -an | grep ESTABLISHED | wc -l)"
        
        # Memory usage
        echo "Memory Usage: $(free -m | grep Mem | awk '{print $3}')MB / $(free -m | grep Mem | awk '{print $2}')MB"
        echo ""
        
        sleep 2
    done
}

generate_report() {
    local report_file="$SCRIPT_DIR/logs/network-report-$(date +%Y%m%d_%H%M%S).txt"
    
    log "Generating Network Report"
    echo "======================="
    
    {
        echo "RPI Player Network Diagnostic Report"
        echo "====================================="
        echo "Generated: $(date)"
        echo ""
        
        echo "System Information:"
        echo "  Hostname: $(hostname)"
        echo "  Kernel: $(uname -r)"
        echo "  Uptime: $(uptime -p)"
        echo ""
        
        echo "Network Configuration:"
        echo "  Interfaces: $(ip link show | grep -E "^[0-9]+:" | wc -l)"
        echo "  Default Gateway: $(ip route | grep default | awk '{print $3}' | head -1)"
        echo "  DNS Servers: $(grep nameserver /etc/resolv.conf | awk '{print $2}' | tr '\n' ' ')"
        echo ""
        
        echo "Test Results Summary:"
        echo "  Total Tests: ${RESULTS["total"]}"
        echo "  Passed: ${RESULTS["passed"]}"
        echo "  Failed: ${RESULTS["failed"]}"
        echo ""
        
        echo "Detailed Results:"
        for key in "${!RESULTS[@]}"; do
            if [ "$key" != "total" ] && [ "$key" != "passed" ] && [ "$key" != "failed" ]; then
                echo "  $key: ${RESULTS[$key]}"
            fi
        done
        
    } > "$report_file"
    
    echo "Report saved to: $report_file"
}

run_startup_diagnostics() {
    log "Running Startup Diagnostics"
    echo "=========================="
    
    # Quick interface check
    for interface in eth0 wlan0; do
        if ip link show "$interface" >/dev/null 2>&1; then
            if ip link show "$interface" | grep -q "state UP"; then
                log "Interface $interface is UP"
            else
                warn "Interface $interface is DOWN"
            fi
        fi
    done
    
    # Quick connectivity check
    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        log "Internet connectivity OK"
    else
        warn "Internet connectivity FAILED"
    fi
    
    # Check streaming ports
    for port in 5000 1935 1234; do
        if netstat -ln | grep ":$port " >/dev/null 2>&1; then
            log "Streaming port $port is open"
        fi
    done
}

# Main script logic
case "${1:-full}" in
    full)
        test_interfaces
        test_connectivity
        test_dns
        test_streaming
        test_performance
        echo ""
        log "Diagnostic Summary: ${RESULTS["passed"]}/${RESULTS["total"]} tests passed"
        ;;
    interfaces)
        test_interfaces
        ;;
    connectivity)
        test_connectivity
        ;;
    dns)
        test_dns
        ;;
    streaming)
        test_streaming
        ;;
    performance)
        test_performance
        ;;
    wifi)
        test_wifi
        ;;
    ethernet)
        test_ethernet
        ;;
    ports)
        test_streaming
        ;;
    bandwidth)
        test_bandwidth
        ;;
    latency)
        test_performance
        ;;
    monitor)
        monitor_network
        ;;
    report)
        generate_report
        ;;
    startup)
        run_startup_diagnostics
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
