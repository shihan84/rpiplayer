#!/bin/bash

# V-Player Version Selection Script
# Professional Streaming Solution by Itassist Broadcast Solutions
# Choose between Standard and Enterprise editions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored header
print_header() {
    echo -e "${CYAN}"
    echo "==================================="
    echo "    V-Player Version Selector"
    echo "  Professional Streaming Solution"
    echo " by Itassist Broadcast Solutions"
    echo "==================================="
    echo -e "${NC}"
}

# Print version info
print_version_info() {
    echo -e "${BLUE}Available V-Player Editions:${NC}"
    echo
    echo -e "${GREEN}1. Standard Edition${NC}"
    echo "   • Flask-based architecture"
    echo "   • Nginx reverse proxy"
    echo "   • Basic authentication"
    echo "   • Simple deployment"
    echo "   • Lower resource usage"
    echo "   • Perfect for small deployments"
    echo
    echo -e "${PURPLE}2. Enterprise Edition${NC}"
    echo "   • OpenResty + Flask hybrid"
    echo "   • Advanced Lua scripting"
    echo "   • JWT authentication"
    echo "   • Redis caching"
    echo "   • Prometheus metrics"
    echo "   • Rate limiting"
    echo "   • Advanced monitoring"
    echo "   • High performance"
    echo "   • Enterprise-grade security"
    echo "   • Perfect for large deployments"
    echo
}

# Check system requirements
check_requirements() {
    echo -e "${YELLOW}Checking system requirements...${NC}"
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This script must be run as root (use sudo)${NC}"
        exit 1
    fi
    
    # Check Raspberry Pi model
    if [[ -f /proc/device-tree/model ]]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
        echo -e "${GREEN}Detected: $MODEL${NC}"
    else
        echo -e "${YELLOW}Could not detect Raspberry Pi model${NC}"
    fi
    
    # Check available memory
    MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [[ $MEMORY -lt 512 ]]; then
        echo -e "${RED}Warning: Low memory available ($MEMORY MB). Enterprise edition requires at least 1GB RAM.${NC}"
    else
        echo -e "${GREEN}Available memory: $MEMORY MB${NC}"
    fi
    
    # Check disk space
    DISK=$(df / | awk 'NR==2{printf "%.0f", $4/1024}')
    if [[ $DISK -lt 2 ]]; then
        echo -e "${RED}Warning: Low disk space available ($DISK GB). At least 2GB recommended.${NC}"
    else
        echo -e "${GREEN}Available disk space: $DISK GB${NC}"
    fi
    
    echo
}

# Get user choice
get_user_choice() {
    while true; do
        echo -e "${CYAN}Choose V-Player Edition (1-2):${NC}"
        read -p "Enter your choice [1-2]: " choice
        
        case $choice in
            1)
                echo -e "${GREEN}Selected: Standard Edition${NC}"
                return 1
                ;;
            2)
                echo -e "${GREEN}Selected: Enterprise Edition${NC}"
                return 2
                ;;
            *)
                echo -e "${RED}Invalid choice. Please enter 1 or 2.${NC}"
                ;;
        esac
    done
}

# Install Standard Edition
install_standard() {
    echo -e "${BLUE}Installing V-Player Standard Edition...${NC}"
    
    # Check if standard installation exists
    if [[ -f "install-v-player.sh" ]]; then
        echo -e "${YELLOW}Running Standard Edition installer...${NC}"
        chmod +x install-v-player.sh
        ./install-v-player.sh
    else
        echo -e "${RED}Standard installer not found. Please ensure install-v-player.sh exists.${NC}"
        exit 1
    fi
}

# Install Enterprise Edition
install_enterprise() {
    echo -e "${PURPLE}Installing V-Player Enterprise Edition...${NC}"
    
    # Check if enterprise installation exists
    if [[ -f "enterprise/install-enterprise.sh" ]]; then
        echo -e "${YELLOW}Running Enterprise Edition installer...${NC}"
        chmod +x enterprise/install-enterprise.sh
        ./enterprise/install-enterprise.sh
    else
        echo -e "${RED}Enterprise installer not found. Please ensure enterprise/install-enterprise.sh exists.${NC}"
        exit 1
    fi
}

# Display installation summary
display_summary() {
    local edition=$1
    echo
    echo -e "${GREEN}==================================="
    echo -e "${GREEN}V-Player $edition Edition Installed!${NC}"
    echo -e "${GREEN}===================================${NC}"
    echo
    echo -e "${BLUE}Access Information:${NC}"
    echo "  Web Interface: http://$(hostname -I | awk '{print $1}')"
    echo "  SSH: ssh rpiplayer@$(hostname -I | awk '{print $1}')"
    echo "  Username: rpiplayer"
    echo "  Password: rpiplayer123"
    echo
    echo -e "${BLUE}Service Management:${NC}"
    echo "  Start: sudo systemctl start v-player"
    echo "  Stop: sudo systemctl stop v-player"
    echo "  Restart: sudo systemctl restart v-player"
    echo "  Status: sudo systemctl status v-player"
    echo "  Logs: sudo journalctl -u v-player -f"
    echo
    
    if [[ $edition == "Enterprise" ]]; then
        echo -e "${PURPLE}Enterprise Features:${NC}"
        echo "  • Metrics: http://$(hostname -I | awk '{print $1}')/metrics"
        echo "  • Health: http://$(hostname -I | awk '{print $1}')/health"
        echo "  • Redis: redis-cli ping"
        echo "  • Advanced authentication enabled"
        echo "  • Rate limiting active"
        echo
    fi
    
    echo -e "${CYAN}Thank you for choosing V-Player!${NC}"
    echo -e "${CYAN}Professional Streaming Solution by Itassist Broadcast Solutions${NC}"
}

# Main function
main() {
    print_header
    print_version_info
    check_requirements
    
    local choice=$(get_user_choice)
    
    echo
    echo -e "${YELLOW}Starting installation...${NC}"
    echo
    
    case $choice in
        1)
            install_standard
            display_summary "Standard"
            ;;
        2)
            install_enterprise
            display_summary "Enterprise"
            ;;
    esac
}

# Run main function
main "$@"
