#!/usr/bin/env python3
"""
V-Player Enterprise Raspberry Pi Image Builder
Creates a complete Raspberry Pi OS image with V-Player Enterprise pre-installed
"""

import os
import subprocess
import shutil
from pathlib import Path

class RPiImageBuilder:
    """Build Raspberry Pi image with V-Player Enterprise"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.build_dir = self.project_dir / 'build'
        self.image_dir = self.build_dir / 'rpi-image'
        
    def create_image_structure(self):
        """Create the image directory structure"""
        print("🏗️ Creating image structure...")
        
        # Create directories
        dirs = [
            'home/pi/vplayer',
            'home/pi/.config/autostart',
            'etc/systemd/system',
            'usr/local/bin',
            'opt/vplayer'
        ]
        
        for dir_path in dirs:
            full_path = self.image_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {dir_path}")
    
    def copy_vplayer_files(self):
        """Copy V-Player files to image"""
        print("📦 Copying V-Player files...")
        
        # Copy application files
        app_files = [
            'app.py',
            'config.py',
            'requirements.txt',
            'rpi-output-configs.py',
            'rpi-network-configs.py',
            'cloudflare_integration_2024.py',
            'stream_decoder.py',
            'network_monitor.py'
        ]
        
        for file_name in app_files:
            src = self.project_dir / file_name
            dst = self.image_dir / 'opt/vplayer' / file_name
            if src.exists():
                shutil.copy2(src, dst)
                print(f"  ✅ Copied: {file_name}")
        
        # Copy directories
        dirs_to_copy = ['templates', 'static']
        for dir_name in dirs_to_copy:
            src = self.project_dir / dir_name
            dst = self.image_dir / 'opt/vplayer' / dir_name
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"  ✅ Copied: {dir_name}/")
    
    def create_systemd_service(self):
        """Create systemd service for V-Player"""
        print("⚙️ Creating systemd service...")
        
        service_content = """[Unit]
Description=V-Player Enterprise
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/vplayer
Environment=PYTHONPATH=/opt/vplayer
ExecStart=/usr/bin/python3 /opt/vplayer/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.image_dir / 'etc/systemd/system/vplayer.service'
        service_file.write_text(service_content)
        print("  ✅ Created: vplayer.service")
    
    def create_autostart_desktop(self):
        """Create desktop autostart entry"""
        print("🖥️ Creating desktop autostart...")
        
        desktop_content = """[Desktop Entry]
Type=Application
Name=V-Player Enterprise
Comment=Professional Broadcasting Interface
Exec=/usr/bin/python3 /opt/vplayer/app.py
Icon=video-display
Terminal=false
Categories=AudioVideo;Video;
StartupNotify=true
"""
        
        desktop_file = self.image_dir / 'home/pi/.config/autostart' / 'vplayer.desktop'
        desktop_file.write_text(desktop_content)
        print("  ✅ Created: vplayer.desktop")
    
    def create_startup_script(self):
        """Create startup script for first boot"""
        print("🚀 Creating startup script...")
        
        startup_script = """#!/bin/bash
# V-Player Enterprise First Boot Setup

echo "🎬 V-Player Enterprise - Starting Setup..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install -y python3-pip python3-venv ffmpeg

# Install V-Player dependencies
cd /opt/vplayer
sudo pip3 install -r requirements.txt

# Enable and start V-Player service
sudo systemctl enable vplayer
sudo systemctl start vplayer

# Create desktop shortcut
cp /usr/share/applications/vplayer.desktop /home/pi/Desktop/
chown pi:pi /home/pi/Desktop/vplayer.desktop

echo "✅ V-Player Enterprise setup complete!"
echo "🌐 Access at: http://$(hostname -I | awk '{print $1}'):5005"
echo "📱 Or use: http://localhost:5005"
"""
        
        script_file = self.image_dir / 'usr/local/bin' / 'vplayer-setup.sh'
        script_file.write_text(startup_script)
        os.chmod(script_file, 0o755)
        print("  ✅ Created: vplayer-setup.sh")
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        print("🖱️ Creating desktop shortcut...")
        
        shortcut_content = """[Desktop Entry]
Version=1.0
Type=Link
Name=V-Player Enterprise
Comment=Open V-Player Enterprise Web Interface
URL=http://localhost:5005
Icon=web-browser
"""
        
        shortcut_file = self.image_dir / 'home/pi/Desktop' / 'V-Player Enterprise.desktop'
        shortcut_file.write_text(shortcut_content)
        print("  ✅ Created: V-Player Enterprise.desktop")
    
    def create_network_config(self):
        """Create network configuration files"""
        print("🌐 Creating network configuration...")
        
        # Create dhcpcd.conf additions
        dhcpcd_content = """# V-Player Enterprise Network Configuration
# Static IP configuration (optional)
# interface eth0
# static ip_address=192.168.1.100/24
# static routers=192.168.1.1
# static domain_name_servers=192.168.1.1 8.8.8.8

# WiFi configuration (optional)
# interface wlan0
# static ip_address=192.168.1.101/24
# static routers=192.168.1.1
# static domain_name_servers=192.168.1.1 8.8.8.8
"""
        
        dhcpcd_file = self.image_dir / 'etc' / 'dhcpcd.conf.d' / 'vplayer.conf'
        dhcpcd_file.write_text(dhcpcd_content)
        print("  ✅ Created: vplayer network config")
    
    def create_readme(self):
        """Create README file for the image"""
        print("📖 Creating README...")
        
        readme_content = """# V-Player Enterprise Raspberry Pi Image

## 🎯 About This Image

This Raspberry Pi OS image comes with V-Player Enterprise pre-installed and configured for professional broadcasting.

## 🚀 Quick Start

1. Flash this image to your Raspberry Pi
2. Boot the Raspberry Pi
3. Wait for automatic setup (first boot only)
4. Access V-Player at: http://your-pi-ip:5005

## 🌐 Default Configuration

- **Port**: 5005
- **User**: pi
- **Password**: raspberry (change on first login)
- **Service**: Automatically starts on boot

## 📱 Features Included

- ✅ Professional Broadcasting Interface
- ✅ AWS Elemental MediaLive-style UI
- ✅ Network Configuration (WiFi, Ethernet, Hotspot)
- ✅ Cloudflare Zero Trust Integration
- ✅ Video Output Management
- ✅ Real-time Monitoring
- ✅ Channel Management

## 🔧 Management

### Start/Stop Service
```bash
sudo systemctl start vplayer
sudo systemctl stop vplayer
sudo systemctl restart vplayer
```

### Check Status
```bash
sudo systemctl status vplayer
```

### View Logs
```bash
sudo journalctl -u vplayer -f
```

## 🌐 Remote Access

### Cloudflare Zero Trust
1. Go to Network tab in V-Player
2. Follow Cloudflare setup instructions
3. Access securely from anywhere

### Direct Access
- Local: http://localhost:5005
- Network: http://[PI-IP]:5005

## 📊 System Requirements

- Raspberry Pi 4B (recommended)
- 2GB RAM minimum
- 16GB SD Card minimum
- Ethernet or WiFi connection

## 🔒 Security

- Change default password on first login
- Configure firewall if needed
- Use Cloudflare Zero Trust for remote access
- Regular updates recommended

## 📞 Support

For support and updates:
- Check the V-Player web interface
- Review system logs
- Update regularly

---
V-Player Enterprise - Professional Broadcasting for Raspberry Pi
"""
        
        readme_file = self.image_dir / 'home/pi' / 'README-V-Player.md'
        readme_file.write_text(readme_content)
        print("  ✅ Created: README-V-Player.md")
    
    def create_image_info(self):
        """Create image information file"""
        print("📋 Creating image info...")
        
        info_content = f"""V-Player Enterprise Image Information
=====================================

Build Date: {subprocess.check_output(['date']).decode().strip()}
Version: 1.0.0
Features: Full Enterprise Edition
Components: Flask, SocketIO, Cloudflare Integration
Default Port: 5005
Service: vplayer.service
Web Interface: http://localhost:5005

Installation Path: /opt/vplayer
Service File: /etc/systemd/system/vplayer.service
Autostart: /home/pi/.config/autostart/vplayer.desktop

Network Configuration: /etc/dhcpcd.conf.d/vplayer.conf
Logs: journalctl -u vplayer
"""
        
        info_file = self.image_dir / 'opt/vplayer' / 'image_info.txt'
        info_file.write_text(info_content)
        print("  ✅ Created: image_info.txt")
    
    def build_image(self):
        """Build the complete Raspberry Pi image"""
        print("🎬 Building V-Player Enterprise Raspberry Pi Image...")
        print("=" * 60)
        
        # Create build directory
        self.build_dir.mkdir(exist_ok=True)
        self.image_dir.mkdir(exist_ok=True)
        
        # Build components
        self.create_image_structure()
        self.copy_vplayer_files()
        self.create_systemd_service()
        self.create_autostart_desktop()
        self.create_startup_script()
        self.create_desktop_shortcut()
        self.create_network_config()
        self.create_readme()
        self.create_image_info()
        
        print("=" * 60)
        print("✅ V-Player Enterprise image build complete!")
        print(f"📁 Image location: {self.image_dir}")
        print("🚀 Ready for Raspberry Pi deployment!")
        
        return self.image_dir

if __name__ == "__main__":
    builder = RPiImageBuilder()
    image_dir = builder.build_image()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Copy contents of {image_dir} to Raspberry Pi OS image")
    print(f"2. Flash to SD card")
    print(f"3. Boot Raspberry Pi")
    print(f"4. Access V-Player at http://raspberry-pi-ip:5005")
