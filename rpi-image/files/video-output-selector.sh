#!/bin/bash

# RPI Player Video Output Selector
# Interactive menu for selecting video output configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_menu() {
    clear
    echo "==================================="
    echo "    RPI Player Video Output       "
    echo "==================================="
    echo ""
    echo "Select video output configuration:"
    echo ""
    echo "1) HDMI (Default)"
    echo "2) Composite (RCA)"
    echo "3) DisplayPort (RPi4+)"
    echo "4) DPI LCD Panel"
    echo "5) DSI LCD Panel"
    echo "6) Auto-detect"
    echo "7) Show current configuration"
    echo "8) Test current output"
    echo "9) Advanced options"
    echo "0) Exit"
    echo ""
    echo -n "Enter your choice [0-9]: "
}

show_current_config() {
    echo ""
    echo "Current video configuration:"
    echo "==========================="
    
    # Read config.txt
    CONFIG_FILE="/boot/config.txt"
    
    if [ -f "$CONFIG_FILE" ]; then
        echo "HDMI Settings:"
        grep -E "^hdmi_" "$CONFIG_FILE" 2>/dev/null || echo "  No HDMI settings found"
        
        echo ""
        echo "Display Settings:"
        grep -E "^(gpu_mem|framebuffer|disable_overscan)" "$CONFIG_FILE" 2>/dev/null || echo "  No display settings found"
        
        echo ""
        echo "Video Overlays:"
        grep -E "^dtoverlay.*vc4" "$CONFIG_FILE" 2>/dev/null || echo "  No video overlays found"
        
        echo ""
        echo "Audio Settings:"
        grep -E "^(dtparam=audio|audio)" "$CONFIG_FILE" 2>/dev/null || echo "  No audio settings found"
    else
        echo "Config file not found: $CONFIG_FILE"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

test_output() {
    echo ""
    echo "Testing video output..."
    echo "This will display a test pattern for 10 seconds."
    echo ""
    read -p "Press Enter to start test (Ctrl+C to cancel)..."
    
    # Create test video
    ffmpeg -y -f lavfi -i testsrc=duration=10:size=1920x1080:rate=25 \
        -c:v h264_v4l2m2m -f fbdev /dev/fb0 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "Test completed successfully"
    else
        echo "Test failed. Check video configuration."
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

advanced_options() {
    while true; do
        clear
        echo "==================================="
        echo "      Advanced Options            "
        echo "==================================="
        echo ""
        echo "1) GPU Memory Configuration"
        echo "2) Hardware Acceleration"
        echo "3) Audio Output Configuration"
        echo "4) Performance Tuning"
        echo "5) Resolution Settings"
        echo "6) Refresh Rate Settings"
        echo "7) Color Space Configuration"
        echo "8) Backup/Restore Configuration"
        echo "0) Back to main menu"
        echo ""
        echo -n "Enter your choice [0-8]: "
        
        read choice
        
        case $choice in
            1) gpu_memory_menu ;;
            2) hardware_accel_menu ;;
            3) audio_config_menu ;;
            4) performance_menu ;;
            5) resolution_menu ;;
            6) refresh_rate_menu ;;
            7) color_space_menu ;;
            8) backup_restore_menu ;;
            0) break ;;
            *) echo "Invalid choice"; sleep 1 ;;
        esac
    done
}

gpu_memory_menu() {
    clear
    echo "GPU Memory Configuration"
    echo "======================="
    echo ""
    echo "Select GPU memory split:"
    echo "1) 128MB (Minimal)"
    echo "2) 192MB (Balanced)"
    echo "3) 256MB (Recommended for video)"
    echo "4) 512MB (Maximum)"
    echo ""
    echo -n "Enter your choice [1-4]: "
    
    read choice
    
    case $choice in
        1) sudo sed -i 's/^gpu_mem=.*/gpu_mem=128/' /boot/config.txt ;;
        2) sudo sed -i 's/^gpu_mem=.*/gpu_mem=192/' /boot/config.txt ;;
        3) sudo sed -i 's/^gpu_mem=.*/gpu_mem=256/' /boot/config.txt ;;
        4) sudo sed -i 's/^gpu_mem=.*/gpu_mem=512/' /boot/config.txt ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "GPU memory updated. Reboot to apply changes."
    sleep 2
}

hardware_accel_menu() {
    clear
    echo "Hardware Acceleration"
    echo "====================="
    echo ""
    echo "Select hardware acceleration:"
    echo "1) Enable KMS (Kernel Mode Setting)"
    echo "2) Enable FKMS (Fake KMS)"
    echo "3) Enable Legacy (Broadcom)"
    echo "4) Disable hardware acceleration"
    echo ""
    echo -n "Enter your choice [1-4]: "
    
    read choice
    
    case $choice in
        1)
            sudo sed -i '/^dtoverlay=vc4/d' /boot/config.txt
            echo "dtoverlay=vc4-kms-v3d" | sudo tee -a /boot/config.txt
            ;;
        2)
            sudo sed -i '/^dtoverlay=vc4/d' /boot/config.txt
            echo "dtoverlay=vc4-fkms-v3d" | sudo tee -a /boot/config.txt
            ;;
        3)
            sudo sed -i '/^dtoverlay=vc4/d' /boot/config.txt
            echo "dtoverlay=vc4" | sudo tee -a /boot/config.txt
            ;;
        4)
            sudo sed -i '/^dtoverlay=vc4/d' /boot/config.txt
            ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "Hardware acceleration updated. Reboot to apply changes."
    sleep 2
}

audio_config_menu() {
    clear
    echo "Audio Output Configuration"
    echo "=========================="
    echo ""
    echo "Select audio output:"
    echo "1) HDMI Audio"
    echo "2) Analog Audio (3.5mm jack)"
    echo "3) Both HDMI and Analog"
    echo "4) Auto-detect"
    echo ""
    echo -n "Enter your choice [1-4]: "
    
    read choice
    
    case $choice in
        1)
            sudo sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' /boot/config.txt
            # Set HDMI as default in ALSA
            sudo sed -i 's/^pcm.!default.*/pcm.!default {\n    type hw\n    card 0\n    device 3\n}/' /etc/asound.conf
            ;;
        2)
            sudo sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' /boot/config.txt
            # Set analog as default in ALSA
            sudo sed -i 's/^pcm.!default.*/pcm.!default {\n    type hw\n    card 0\n    device 0\n}/' /etc/asound.conf
            ;;
        3)
            sudo sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' /boot/config.txt
            # Configure for both outputs
            ;;
        4)
            sudo sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' /boot/config.txt
            ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "Audio configuration updated. Reboot to apply changes."
    sleep 2
}

performance_menu() {
    clear
    echo "Performance Tuning"
    echo "=================="
    echo ""
    echo "Select performance profile:"
    echo "1) Power Save (Default)"
    echo "2) Balanced"
    echo "3) High Performance"
    echo "4) Maximum Performance"
    echo ""
    echo -n "Enter your choice [1-4]: "
    
    read choice
    
    case $choice in
        1)
            # Conservative settings
            sudo sed -i 's/^arm_freq=.*/arm_freq=900/' /boot/config.txt
            sudo sed -i 's/^over_voltage=.*/over_voltage=0/' /boot/config.txt
            ;;
        2)
            # Balanced settings
            sudo sed -i 's/^arm_freq=.*/arm_freq=1200/' /boot/config.txt
            sudo sed -i 's/^over_voltage=.*/over_voltage=2/' /boot/config.txt
            ;;
        3)
            # High performance
            sudo sed -i 's/^arm_freq=.*/arm_freq=1400/' /boot/config.txt
            sudo sed -i 's/^over_voltage=.*/over_voltage=4/' /boot/config.txt
            ;;
        4)
            # Maximum performance
            sudo sed -i 's/^arm_freq=.*/arm_freq=1500/' /boot/config.txt
            sudo sed -i 's/^over_voltage=.*/over_voltage=6/' /boot/config.txt
            ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "Performance settings updated. Reboot to apply changes."
    sleep 2
}

resolution_menu() {
    clear
    echo "Resolution Settings"
    echo "==================="
    echo ""
    echo "Select resolution:"
    echo "1) 640x480 (VGA)"
    echo "2) 720x576 (PAL)"
    echo "3) 1280x720 (720p)"
    echo "4) 1920x1080 (1080p)"
    echo "5) 3840x2160 (4K - RPi4+)"
    echo ""
    echo -n "Enter your choice [1-5]: "
    
    read choice
    
    case $choice in
        1)
            sudo sed -i 's/^hdmi_group=.*/hdmi_group=2/' /boot/config.txt
            sudo sed -i 's/^hdmi_mode=.*/hdmi_mode=4/' /boot/config.txt
            ;;
        2)
            sudo sed -i 's/^hdmi_group=.*/hdmi_group=1/' /boot/config.txt
            sudo sed -i 's/^hdmi_mode=.*/hdmi_mode=17/' /boot/config.txt
            ;;
        3)
            sudo sed -i 's/^hdmi_group=.*/hdmi_group=1/' /boot/config.txt
            sudo sed -i 's/^hdmi_mode=.*/hdmi_mode=82/' /boot/config.txt
            ;;
        4)
            sudo sed -i 's/^hdmi_group=.*/hdmi_group=1/' /boot/config.txt
            sudo sed -i 's/^hdmi_mode=.*/hdmi_mode=82/' /boot/config.txt
            ;;
        5)
            sudo sed -i 's/^hdmi_group=.*/hdmi_group=1/' /boot/config.txt
            sudo sed -i 's/^hdmi_mode=.*/hdmi_mode=97/' /boot/config.txt
            ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "Resolution updated. Reboot to apply changes."
    sleep 2
}

refresh_rate_menu() {
    clear
    echo "Refresh Rate Settings"
    echo "====================="
    echo ""
    echo "Select refresh rate:"
    echo "1) 24 Hz (Cinema)"
    echo "2) 30 Hz"
    echo "3) 50 Hz (PAL)"
    echo "4) 60 Hz (NTSC)"
    echo "5) 75 Hz"
    echo ""
    echo -n "Enter your choice [1-5]: "
    
    read choice
    
    case $choice in
        1)
            sudo sed -i 's/^hdmi_pixel_encoding=.*/hdmi_pixel_encoding=1/' /boot/config.txt
            ;;
        2)
            sudo sed -i 's/^hdmi_pixel_encoding=.*/hdmi_pixel_encoding=1/' /boot/config.txt
            ;;
        3)
            sudo sed -i 's/^hdmi_pixel_encoding=.*/hdmi_pixel_encoding=1/' /boot/config.txt
            ;;
        4)
            sudo sed -i 's/^hdmi_pixel_encoding=.*/hdmi_pixel_encoding=1/' /boot/config.txt
            ;;
        5)
            sudo sed -i 's/^hdmi_pixel_encoding=.*/hdmi_pixel_encoding=1/' /boot/config.txt
            ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "Refresh rate updated. Reboot to apply changes."
    sleep 2
}

color_space_menu() {
    clear
    echo "Color Space Configuration"
    echo "========================="
    echo ""
    echo "Select color space:"
    echo "1) RGB (Limited)"
    echo "2) RGB (Full)"
    echo "3) YUV 4:2:2"
    echo "4) YUV 4:4:4"
    echo ""
    echo -n "Enter your choice [1-4]: "
    
    read choice
    
    case $choice in
        1)
            echo "hdmi_pixel_encoding=0" | sudo tee -a /boot/config.txt
            ;;
        2)
            echo "hdmi_pixel_encoding=1" | sudo tee -a /boot/config.txt
            ;;
        3)
            echo "hdmi_pixel_encoding=2" | sudo tee -a /boot/config.txt
            ;;
        4)
            echo "hdmi_pixel_encoding=3" | sudo tee -a /boot/config.txt
            ;;
        *) echo "Invalid choice"; return ;;
    esac
    
    echo "Color space updated. Reboot to apply changes."
    sleep 2
}

backup_restore_menu() {
    clear
    echo "Backup/Restore Configuration"
    echo "============================"
    echo ""
    echo "1) Backup current configuration"
    echo "2) Restore configuration"
    echo "3) List available backups"
    echo "0) Back"
    echo ""
    echo -n "Enter your choice [0-3]: "
    
    read choice
    
    case $choice in
        1)
            BACKUP_FILE="/boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)"
            sudo cp /boot/config.txt "$BACKUP_FILE"
            echo "Configuration backed up to: $BACKUP_FILE"
            sleep 2
            ;;
        2)
            echo "Available backups:"
            ls -la /boot/config.txt.backup.* 2>/dev/null || echo "No backups found"
            echo ""
            echo -n "Enter backup filename to restore: "
            read backup_file
            if [ -f "$backup_file" ]; then
                sudo cp "$backup_file" /boot/config.txt
                echo "Configuration restored from: $backup_file"
            else
                echo "Backup file not found: $backup_file"
            fi
            sleep 2
            ;;
        3)
            echo "Available backups:"
            ls -la /boot/config.txt.backup.* 2>/dev/null || echo "No backups found"
            sleep 3
            ;;
        0)
            return
            ;;
        *)
            echo "Invalid choice"
            sleep 1
            ;;
    esac
}

# Main menu loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            "$SCRIPT_DIR/broadcast-config.sh" hdmi
            echo "HDMI configuration applied. Reboot to apply changes."
            sleep 2
            ;;
        2)
            "$SCRIPT_DIR/broadcast-config.sh" composite
            echo "Composite configuration applied. Reboot to apply changes."
            sleep 2
            ;;
        3)
            "$SCRIPT_DIR/broadcast-config.sh" displayport
            echo "DisplayPort configuration applied. Reboot to apply changes."
            sleep 2
            ;;
        4)
            "$SCRIPT_DIR/broadcast-config.sh" dpi
            echo "DPI configuration applied. Reboot to apply changes."
            sleep 2
            ;;
        5)
            "$SCRIPT_DIR/broadcast-config.sh" dsi
            echo "DSI configuration applied. Reboot to apply changes."
            sleep 2
            ;;
        6)
            "$SCRIPT_DIR/broadcast-config.sh" auto
            echo "Auto-detect configuration applied. Reboot to apply changes."
            sleep 2
            ;;
        7)
            show_current_config
            ;;
        8)
            test_output
            ;;
        9)
            advanced_options
            ;;
        0)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            sleep 1
            ;;
    esac
done
