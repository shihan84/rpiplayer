#!/bin/bash

# RPI Player Broadcast Configuration Script
# Configure video output for different broadcast scenarios

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="/boot/config.txt"
ASOUND_FILE="/etc/asound.conf"

show_help() {
    echo "RPI Player Broadcast Configuration"
    echo "Usage: $0 [output_type]"
    echo ""
    echo "Output types:"
    echo "  hdmi      - HDMI output (default)"
    echo "  composite - Composite/RCA output"
    echo "  displayport - DisplayPort output (RPi4+)"
    echo "  dpi       - DPI LCD panel"
    echo "  dsi       - DSI LCD panel"
    echo "  auto      - Auto-detect display"
    echo ""
    echo "Examples:"
    echo "  $0 hdmi"
    echo "  $0 composite"
    echo "  $0 auto"
}

backup_config() {
    sudo cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Config backed up"
}

configure_hdmi() {
    echo "Configuring HDMI output..."
    
    # Update config.txt for HDMI
    sudo sed -i 's/^hdmi_force_hotplug=.*/hdmi_force_hotplug=1/' "$CONFIG_FILE"
    sudo sed -i 's/^hdmi_drive=.*/hdmi_drive=2/' "$CONFIG_FILE"
    sudo sed -i 's/^hdmi_group=.*/hdmi_group=1/' "$CONFIG_FILE"
    sudo sed -i 's/^hdmi_mode=.*/hdmi_mode=16/' "$CONFIG_FILE"
    
    # Configure audio for HDMI
    sudo sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' "$CONFIG_FILE"
    
    echo "HDMI configuration complete. Reboot to apply changes."
}

configure_composite() {
    echo "Configuring composite (RCA) output..."
    
    # Enable composite output
    sudo sed -i 's/^#*enable_tvout=.*/enable_tvout=1/' "$CONFIG_FILE"
    sudo sed -i 's/^#*sdtv_mode=.*/sdtv_mode=0/' "$CONFIG_FILE"
    sudo sed -i 's/^#*sdtv_aspect=.*/sdtv_aspect=1/' "$CONFIG_FILE"
    
    # Disable HDMI for composite only
    sudo sed -i 's/^hdmi_force_hotplug=.*/hdmi_force_hotplug=0/' "$CONFIG_FILE"
    
    # Configure audio for analog output
    sudo sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' "$CONFIG_FILE"
    
    echo "Composite configuration complete. Reboot to apply changes."
}

configure_displayport() {
    echo "Configuring DisplayPort output..."
    
    # Enable DisplayPort
    sudo sed -i 's/^#*enable_dp=.*/enable_dp=1/' "$CONFIG_FILE"
    sudo sed -i 's/^hdmi_force_hotplug=.*/hdmi_force_hotplug=0/' "$CONFIG_FILE"
    
    echo "DisplayPort configuration complete. Reboot to apply changes."
}

configure_dpi() {
    echo "Configuring DPI LCD panel..."
    
    # Enable DPI
    sudo sed -i 's/^#*dtoverlay=dpi24.*/dtoverlay=dpi24/' "$CONFIG_FILE"
    sudo sed -i 's/^hdmi_force_hotplug=.*/hdmi_force_hotplug=0/' "$CONFIG_FILE"
    
    echo "DPI configuration complete. Reboot to apply changes."
}

configure_dsi() {
    echo "Configuring DSI LCD panel..."
    
    # Enable DSI (for official Raspberry Pi displays)
    sudo sed -i 's/^#*dtoverlay=vc4-kms-dsi.*/dtoverlay=vc4-kms-dsi/' "$CONFIG_FILE"
    sudo sed -i 's/^hdmi_force_hotplug=.*/hdmi_force_hotplug=0/' "$CONFIG_FILE"
    
    echo "DSI configuration complete. Reboot to apply changes."
}

configure_auto() {
    echo "Configuring auto-detect display..."
    
    # Enable all outputs for auto-detection
    sudo sed -i 's/^hdmi_force_hotplug=.*/hdmi_force_hotplug=1/' "$CONFIG_FILE"
    sudo sed -i 's/^#*enable_tvout=.*/enable_tvout=1/' "$CONFIG_FILE"
    sudo sed -i 's/^#*enable_dp=.*/enable_dp=1/' "$CONFIG_FILE"
    
    echo "Auto-detect configuration complete. Reboot to apply changes."
}

optimize_for_streaming() {
    echo "Optimizing system for streaming..."
    
    # Set GPU memory
    sudo sed -i 's/^gpu_mem=.*/gpu_mem=256/' "$CONFIG_FILE"
    
    # Enable hardware acceleration
    sudo sed -i 's/^#*dtoverlay=vc4-kms-v3d.*/dtoverlay=vc4-kms-v3d/' "$CONFIG_FILE"
    
    # Set performance governor
    echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
    
    # Disable unnecessary services
    sudo systemctl disable bluetooth 2>/dev/null || true
    sudo systemctl disable cups 2>/dev/null || true
    
    echo "Streaming optimization complete."
}

# Main script logic
case "${1:-hdmi}" in
    hdmi)
        backup_config
        configure_hdmi
        optimize_for_streaming
        ;;
    composite)
        backup_config
        configure_composite
        optimize_for_streaming
        ;;
    displayport)
        backup_config
        configure_displayport
        optimize_for_streaming
        ;;
    dpi)
        backup_config
        configure_dpi
        optimize_for_streaming
        ;;
    dsi)
        backup_config
        configure_dsi
        optimize_for_streaming
        ;;
    auto)
        backup_config
        configure_auto
        optimize_for_streaming
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown output type: $1"
        show_help
        exit 1
        ;;
esac
