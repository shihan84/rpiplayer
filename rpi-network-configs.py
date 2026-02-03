#!/usr/bin/env python3
"""
V-Player Raspberry Pi Network Configuration
Professional Streaming Solution by Itassist Broadcast Solutions

This module provides Raspberry Pi specific network configurations
based on official Raspberry Pi OS documentation.
"""

import subprocess
import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class RaspberryPiNetworkConfig:
    """Raspberry Pi network configuration manager based on official documentation"""
    
    def __init__(self):
        self.dhcpcd_conf = "/etc/dhcpcd.conf"
        self.interfaces_file = "/etc/network/interfaces"
        self.interfaces_d_dir = "/etc/network/interfaces.d"
        self.hostapd_conf = "/etc/hostapd/hostapd.conf"
        self.dnsmasq_conf = "/etc/dnsmasq.conf"
        self.default_hostapd = "/etc/default/hostapd"
        
    def get_current_network_config(self) -> Dict:
        """Get current network configuration"""
        try:
            config = {
                "interfaces": self._get_interface_status(),
                "dhcpcd_config": self._parse_dhcpcd_conf(),
                "routing": self._get_routing_info(),
                "wifi_networks": self._get_wifi_networks(),
                "hotspot_status": self._get_hotspot_status()
            }
            return config
        except Exception as e:
            return {"error": str(e)}
    
    def _get_interface_status(self) -> Dict:
        """Get status of all network interfaces"""
        try:
            # Get interface information
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            interfaces = {}
            
            current_interface = None
            for line in result.stdout.split('\n'):
                if line.strip():
                    if line[0].isdigit() or ':' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            current_interface = parts[1].rstrip(':')
                            interfaces[current_interface] = {
                                'state': parts[0] if parts[0].isdigit() else 'UNKNOWN',
                                'mac': parts[1] if ':' in parts[1] else None,
                                'ip_addresses': []
                            }
                    elif current_interface and 'inet' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            interfaces[current_interface]['ip_addresses'].append(parts[1])
            
            return interfaces
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_dhcpcd_conf(self) -> Dict:
        """Parse dhcpcd.conf configuration"""
        try:
            if not os.path.exists(self.dhcpcd_conf):
                return {"exists": False}
            
            with open(self.dhcpcd_conf, 'r') as f:
                content = f.read()
            
            config = {"exists": True, "interfaces": {}}
            current_interface = None
            
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('interface '):
                    current_interface = line.split()[1]
                    config["interfaces"][current_interface] = {}
                elif current_interface and '=' in line:
                    key, value = line.split('=', 1)
                    config["interfaces"][current_interface][key.strip()] = value.strip()
            
            return config
        except Exception as e:
            return {"exists": True, "error": str(e)}
    
    def _get_routing_info(self) -> Dict:
        """Get routing information"""
        try:
            result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
            routes = []
            
            for line in result.stdout.split('\n'):
                if line.strip() and 'default' in line:
                    parts = line.split()
                    route_info = {
                        'destination': parts[0],
                        'gateway': parts[2] if len(parts) > 2 else None,
                        'interface': parts[4] if len(parts) > 4 else None
                    }
                    routes.append(route_info)
            
            return {"routes": routes}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_wifi_networks(self) -> List[Dict]:
        """Get available WiFi networks"""
        try:
            result = subprocess.run(['iwlist', 'scan'], capture_output=True, text=True)
            networks = []
            
            current_cell = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Cell '):
                    if current_cell:
                        networks.append(current_cell)
                    current_cell = {}
                elif ':' in line and current_cell is not None:
                    key, value = line.split(':', 1)
                    current_cell[key.strip()] = value.strip()
            
            if current_cell:
                networks.append(current_cell)
            
            return networks
        except Exception as e:
            return [{"error": str(e)}]
    
    def _get_hotspot_status(self) -> Dict:
        """Get hotspot status"""
        try:
            # Check if hostapd is running
            result = subprocess.run(['systemctl', 'is-active', 'hostapd'], 
                                  capture_output=True, text=True)
            hostapd_active = result.stdout.strip() == 'active'
            
            # Check if dnsmasq is running
            result = subprocess.run(['systemctl', 'is-active', 'dnsmasq'], 
                                  capture_output=True, text=True)
            dnsmasq_active = result.stdout.strip() == 'active'
            
            # Get hotspot configuration if exists
            hotspot_config = {}
            if os.path.exists(self.hostapd_conf):
                with open(self.hostapd_conf, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            hotspot_config[key.strip()] = value.strip()
            
            return {
                "active": hostapd_active and dnsmasq_active,
                "hostapd_active": hostapd_active,
                "dnsmasq_active": dnsmasq_active,
                "config": hotspot_config
            }
        except Exception as e:
            return {"error": str(e)}
    
    def configure_static_ip(self, interface: str, ip_address: str, netmask: str, 
                           gateway: str, dns_servers: List[str]) -> bool:
        """Configure static IP address using official dhcpcd.conf method"""
        try:
            # Backup original dhcpcd.conf
            if os.path.exists(self.dhcpcd_conf):
                subprocess.run(['sudo', 'cp', self.dhcpcd.conf, f"{self.dhcpcd.conf}.backup"])
            
            # Read current configuration
            config_lines = []
            if os.path.exists(self.dhcpcd.conf):
                with open(self.dhcpcd_conf, 'r') as f:
                    config_lines = f.readlines()
            
            # Remove existing configuration for this interface
            filtered_lines = []
            skip_lines = False
            for line in config_lines:
                if line.strip().startswith(f'interface {interface}'):
                    skip_lines = True
                elif skip_lines and line.strip().startswith('interface '):
                    skip_lines = False
                    filtered_lines.append(line)
                elif not skip_lines:
                    filtered_lines.append(line)
            
            # Add new static configuration
            static_config = [
                f"\n# Static IP configuration for {interface}\n",
                f"interface {interface}\n",
                f"static ip_address={ip_address}/{self._cidr_from_netmask(netmask)}\n",
                f"static routers={gateway}\n",
                f"static domain_name_servers={' '.join(dns_servers)}\n"
            ]
            
            # Write new configuration
            with open('/tmp/dhcpcd.conf', 'w') as f:
                f.writelines(filtered_lines)
                f.writelines(static_config)
            
            # Apply configuration
            subprocess.run(['sudo', 'cp', '/tmp/dhcpcd.conf', self.dhcpcd_conf])
            subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'])
            
            return True
        except Exception as e:
            print(f"Error configuring static IP: {e}")
            return False
    
    def configure_hotspot(self, ssid: str, password: str, channel: int = 9, 
                         country_code: str = 'US') -> bool:
        """Configure WiFi hotspot using official method"""
        try:
            # Install required packages
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'dnsmasq', 'hostapd'], check=True)
            
            # Stop services
            subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'])
            subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'])
            
            # Configure static IP for wlan0
            self._configure_hotspot_static_ip()
            
            # Configure dnsmasq
            self._configure_dnsmasq()
            
            # Configure hostapd
            self._configure_hostapd(ssid, password, channel, country_code)
            
            # Enable IP forwarding
            self._enable_ip_forwarding()
            
            # Start services
            subprocess.run(['sudo', 'systemctl', 'start', 'dnsmasq'])
            subprocess.run(['sudo', 'systemctl', 'unmask', 'hostapd'])
            subprocess.run(['sudo', 'systemctl', 'enable', 'hostapd'])
            subprocess.run(['sudo', 'systemctl', 'start', 'hostapd'])
            
            return True
        except Exception as e:
            print(f"Error configuring hotspot: {e}")
            return False
    
    def _configure_hotspot_static_ip(self):
        """Configure static IP for hotspot"""
        config = f"""
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
"""
        
        with open('/tmp/dhcpcd_hotspot.conf', 'w') as f:
            f.write(config)
        
        subprocess.run(['sudo', 'cp', '/tmp/dhcpcd_hotspot.conf', self.dhcpcd_conf])
        subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'])
    
    def _configure_dnsmasq(self):
        """Configure dnsmasq for hotspot"""
        config = """
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/#/192.168.4.1
"""
        
        with open('/tmp/dnsmasq.conf', 'w') as f:
            f.write(config)
        
        subprocess.run(['sudo', 'cp', '/tmp/dnsmasq.conf', self.dnsmasq_conf])
    
    def _configure_hostapd(self, ssid: str, password: str, channel: int, country_code: str):
        """Configure hostapd for hotspot"""
        config = f"""
country_code={country_code}
interface=wlan0
ssid={ssid}
channel={channel}
auth_algs=1
wpa=2
wpa_passphrase={password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
        
        with open('/tmp/hostapd.conf', 'w') as f:
            f.write(config)
        
        subprocess.run(['sudo', 'cp', '/tmp/hostapd.conf', self.hostapd_conf])
        
        # Update default hostapd configuration
        with open('/tmp/default_hostapd', 'w') as f:
            f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"\n')
        
        subprocess.run(['sudo', 'cp', '/tmp/default_hostapd', self.default_hostapd])
    
    def _enable_ip_forwarding(self):
        """Enable IP forwarding for hotspot"""
        # Enable IP forwarding
        with open('/tmp/sysctl.conf', 'w') as f:
            f.write('net.ipv4.ip_forward=1\n')
        
        subprocess.run(['sudo', 'cp', '/tmp/sysctl.conf', '/etc/sysctl.conf'])
        subprocess.run(['sudo', 'sysctl', '-p'])
        
        # Configure NAT
        subprocess.run(['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', 'eth0', '-j', 'MASQUERADE'])
        subprocess.run(['sudo', 'sh', '-c', 'iptables-save > /etc/iptables.ipv4.nat'])
        
        # Create systemd service for iptables
        service_content = """
[Unit]
Description=iptables rules for NAT
Before=network.target

[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore < /etc/iptables.ipv4.nat
ExecReload=/sbin/iptables-restore < /etc/iptables.ipv4.nat
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""
        
        with open('/tmp/iptables-restore.service', 'w') as f:
            f.write(service_content)
        
        subprocess.run(['sudo', 'cp', '/tmp/iptables-restore.service', '/etc/systemd/system/'])
        subprocess.run(['sudo', 'systemctl', 'enable', 'iptables-restore'])
        subprocess.run(['sudo', 'systemctl', 'start', 'iptables-restore'])
    
    def stop_hotspot(self) -> bool:
        """Stop hotspot and restore normal WiFi"""
        try:
            subprocess.run(['sudo', 'systemctl', 'stop', 'hostapd'])
            subprocess.run(['sudo', 'systemctl', 'stop', 'dnsmasq'])
            subprocess.run(['sudo', 'systemctl', 'disable', 'hostapd'])
            
            # Restore original dhcpcd.conf if backup exists
            if os.path.exists(f"{self.dhcpcd.conf}.backup"):
                subprocess.run(['sudo', 'cp', f"{self.dhcpcd.conf}.backup", self.dhcpcd.conf])
            
            subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'])
            return True
        except Exception as e:
            print(f"Error stopping hotspot: {e}")
            return False
    
    def scan_wifi_networks(self) -> List[Dict]:
        """Scan for available WiFi networks"""
        try:
            result = subprocess.run(['iwlist', 'wlan0', 'scan'], capture_output=True, text=True)
            networks = []
            
            current_cell = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith('Cell '):
                    if current_cell:
                        networks.append(current_cell)
                    current_cell = {'Address': line.split()[-1]}
                elif ':' in line and current_cell is not None:
                    key, value = line.split(':', 1)
                    current_cell[key.strip()] = value.strip()
            
            if current_cell:
                networks.append(current_cell)
            
            return networks
        except Exception as e:
            return [{"error": str(e)}]
    
    def connect_wifi(self, ssid: str, password: str) -> bool:
        """Connect to WiFi network"""
        try:
            # Generate wpa_supplicant configuration
            psk_result = subprocess.run(['wpa_passphrase', ssid, password], 
                                       capture_output=True, text=True)
            
            if psk_result.returncode != 0:
                return False
            
            # Add to wpa_supplicant.conf
            with open('/tmp/wpa_supplicant.conf', 'w') as f:
                f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
                f.write('update_config=1\n')
                f.write('country=US\n')
                f.write(psk_result.stdout)
            
            subprocess.run(['sudo', 'cp', '/tmp/wpa_supplicant.conf', '/etc/wpa_supplicant/wpa_supplicant.conf'])
            subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
            
            return True
        except Exception as e:
            print(f"Error connecting to WiFi: {e}")
            return False
    
    def _cidr_from_netmask(self, netmask: str) -> int:
        """Convert netmask to CIDR notation"""
        try:
            octets = list(map(int, netmask.split('.')))
            binary_str = ''.join(f'{octet:08b}' for octet in octets)
            return binary_str.count('1')
        except:
            return 24  # Default to /24
    
    def get_network_metrics(self) -> Dict:
        """Get network performance metrics"""
        try:
            # Get interface statistics
            result = subprocess.run(['cat', '/proc/net/dev'], capture_output=True, text=True)
            interfaces = {}
            
            for line in result.stdout.split('\n')[2:]:  # Skip header lines
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 17:
                        interface = parts[0].rstrip(':')
                        interfaces[interface] = {
                            'rx_bytes': int(parts[1]),
                            'tx_bytes': int(parts[9]),
                            'rx_packets': int(parts[2]),
                            'tx_packets': int(parts[10])
                        }
            
            # Get WiFi signal strength if available
            wifi_info = {}
            try:
                result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Signal level=' in line:
                        match = re.search(r'Signal level=(-?\d+) dBm', line)
                        if match:
                            wifi_info['signal_level'] = int(match.group(1))
                    elif 'Link Quality=' in line:
                        match = re.search(r'Link Quality=(\d+)/(\d+)', line)
                        if match:
                            wifi_info['link_quality'] = f"{match.group(1)}/{match.group(2)}"
            except:
                pass
            
            return {
                'interfaces': interfaces,
                'wifi': wifi_info
            }
        except Exception as e:
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    config = RaspberryPiNetworkConfig()
    
    # Get current network configuration
    current_config = config.get_current_network_config()
    print("Current Network Configuration:")
    print(current_config)
    
    # Get network metrics
    metrics = config.get_network_metrics()
    print("\nNetwork Metrics:")
    print(metrics)
    
    # Scan WiFi networks
    networks = config.scan_wifi_networks()
    print(f"\nFound {len(networks)} WiFi networks")
    for network in networks[:3]:  # Show first 3
        print(f"SSID: {network.get('ESSID', 'Unknown')} - Signal: {network.get('Quality', 'Unknown')}")
