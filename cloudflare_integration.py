#!/usr/bin/env python3
"""
V-Player Cloudflare Zero Trust Integration
Secure Remote Access Configuration

This module provides integration with Cloudflare Zero Trust
for secure remote access to the V-Player web interface.
"""

import subprocess
import os
import json
import yaml
from typing import Dict, Optional, List
from pathlib import Path

class CloudflareIntegration:
    """Cloudflare Zero Trust integration for V-Player"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.cloudflared'
        self.config_file = self.config_dir / 'config.yml'
        self.tunnel_name = 'vplayer-tunnel'
        self.service_file = '/etc/systemd/system/cloudflared.service'
        
    def check_cloudflared_installed(self) -> bool:
        """Check if cloudflared is installed"""
        try:
            result = subprocess.run(['cloudflared', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def install_cloudflared(self) -> bool:
        """Install cloudflared on Raspberry Pi"""
        try:
            # Download cloudflared
            download_cmd = [
                'wget', '-O', '/tmp/cloudflared.deb',
                'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb'
            ]
            subprocess.run(download_cmd, check=True)
            
            # Install cloudflared
            install_cmd = ['sudo', 'dpkg', '-i', '/tmp/cloudflared.deb']
            subprocess.run(install_cmd, check=True)
            
            # Clean up
            os.remove('/tmp/cloudflared.deb')
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing cloudflared: {e}")
            return False
    
    def login_cloudflare(self) -> bool:
        """Login to Cloudflare account"""
        try:
            print("Opening browser for Cloudflare authentication...")
            subprocess.run(['cloudflared', 'tunnel', 'login'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error logging into Cloudflare: {e}")
            return False
    
    def create_tunnel(self, hostname: str, local_port: int = 5004) -> bool:
        """Create Cloudflare tunnel"""
        try:
            # Create tunnel
            create_cmd = ['cloudflared', 'tunnel', 'create', self.tunnel_name]
            result = subprocess.run(create_cmd, capture_output=True, text=True, check=True)
            
            # Extract tunnel UUID from output
            tunnel_info = result.stdout
            print(f"Tunnel created: {tunnel_info}")
            
            # Create config directory
            self.config_dir.mkdir(exist_ok=True)
            
            # Create config file
            config = {
                'tunnel': self.tunnel_name,
                'credentials-file': str(self.config_dir / f'{self.tunnel_name}.json'),
                'ingress': [
                    {
                        'hostname': hostname,
                        'service': f'http://localhost:{local_port}'
                    },
                    {'service': 'http_status:404'}
                ]
            }
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Create DNS record
            dns_cmd = ['cloudflared', 'tunnel', 'route', 'dns', 
                      self.tunnel_name, hostname]
            subprocess.run(dns_cmd, check=True)
            
            print(f"DNS record created for {hostname}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating tunnel: {e}")
            return False
    
    def create_systemd_service(self) -> bool:
        """Create systemd service for automatic tunnel startup"""
        try:
            service_content = f"""[Unit]
Description=cloudflared
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'pi')}
ExecStart=/usr/bin/cloudflared tunnel run {self.tunnel_name}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target"""
            
            # Write service file
            with open('/tmp/cloudflared.service', 'w') as f:
                f.write(service_content)
            
            # Copy to systemd directory
            subprocess.run(['sudo', 'cp', '/tmp/cloudflared.service', self.service_file], check=True)
            
            # Reload systemd
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            # Enable service
            subprocess.run(['sudo', 'systemctl', 'enable', 'cloudflared'], check=True)
            
            # Clean up
            os.remove('/tmp/cloudflared.service')
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating systemd service: {e}")
            return False
    
    def start_tunnel(self) -> bool:
        """Start the Cloudflare tunnel"""
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'cloudflared'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error starting tunnel: {e}")
            return False
    
    def stop_tunnel(self) -> bool:
        """Stop the Cloudflare tunnel"""
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'cloudflared'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error stopping tunnel: {e}")
            return False
    
    def get_tunnel_status(self) -> Dict:
        """Get tunnel status"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'is-active', 'cloudflared'], 
                                  capture_output=True, text=True)
            status = result.stdout.strip()
            
            # Get service details
            result = subprocess.run(['sudo', 'systemctl', 'status', 'cloudflared'], 
                                  capture_output=True, text=True)
            
            return {
                'active': status == 'active',
                'status': status,
                'details': result.stdout
            }
        except Exception as e:
            return {'active': False, 'error': str(e)}
    
    def get_tunnel_info(self) -> Dict:
        """Get tunnel configuration info"""
        try:
            if not self.config_file.exists():
                return {'error': 'Config file not found'}
            
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return {
                'tunnel_name': config.get('tunnel'),
                'ingress': config.get('ingress', []),
                'config_exists': True
            }
        except Exception as e:
            return {'error': str(e)}
    
    def test_tunnel_connection(self, hostname: str) -> Dict:
        """Test if tunnel is accessible"""
        try:
            import requests
            
            # Test connection with timeout
            response = requests.get(f'https://{hostname}', timeout=10)
            
            return {
                'accessible': True,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                'accessible': False,
                'error': str(e)
            }
    
    def generate_setup_script(self, hostname: str, local_port: int = 5004) -> str:
        """Generate setup script for easy deployment"""
        script = f"""#!/bin/bash
# V-Player Cloudflare Zero Trust Setup Script

set -e

echo "🚀 Setting up Cloudflare Zero Trust for V-Player..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this script as a regular user (not root)"
    exit 1
fi

# Install cloudflared
echo "📦 Installing cloudflared..."
wget -O /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i /tmp/cloudflared.deb
rm /tmp/cloudflared.deb

# Login to Cloudflare
echo "🔐 Logging into Cloudflare..."
cloudflared tunnel login

# Create tunnel
echo "🌐 Creating tunnel for {hostname}..."
cloudflared tunnel create {self.tunnel_name}

# Create config
echo "⚙️ Creating configuration..."
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: {self.tunnel_name}
credentials-file: ~/.cloudflared/{self.tunnel_name}.json

ingress:
  - hostname: {hostname}
    service: http://localhost:{local_port}
  - service: http_status:404
EOF

# Create DNS record
echo "🌍 Creating DNS record..."
cloudflared tunnel route dns {self.tunnel_name} {hostname}

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /tmp/cloudflared.service << EOF
[Unit]
Description=cloudflared
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/cloudflared tunnel run {self.tunnel_name}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/cloudflared.service /etc/systemd/system/cloudflared.service
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
rm /tmp/cloudflared.service

# Start tunnel
echo "🚀 Starting tunnel..."
sudo systemctl start cloudflared

echo "✅ Cloudflare Zero Trust setup complete!"
echo "🌐 Access your V-Player at: https://{hostname}"
echo "📱 Configure Zero Trust policies in Cloudflare dashboard"
"""
        return script

# Example usage
if __name__ == "__main__":
    cf = CloudflareIntegration()
    
    # Check installation
    if not cf.check_cloudflared_installed():
        print("❌ cloudflared not installed")
        print("📦 Installing cloudflared...")
        if cf.install_cloudflared():
            print("✅ cloudflared installed successfully")
        else:
            print("❌ Failed to install cloudflared")
            exit(1)
    
    # Generate setup script
    hostname = "vplayer.yourdomain.com"  # Replace with your domain
    script = cf.generate_setup_script(hostname)
    
    # Save script
    with open('setup_cloudflare.sh', 'w') as f:
        f.write(script)
    
    os.chmod('setup_cloudflare.sh', 0o755)
    print(f"✅ Setup script generated: setup_cloudflare.sh")
    print(f"🌐 Your V-Player will be accessible at: https://{hostname}")
