#!/usr/bin/env python3

import psutil
import subprocess
import time
import json
import socket
import threading
import logging
from datetime import datetime
from flask_socketio import emit

class NetworkMonitor:
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        self.stats_history = []
        self.max_history = 100
        
        # Network interfaces to monitor
        self.interfaces = ['eth0', 'wlan0', 'wlan1']
        
        # Streaming ports to monitor
        self.streaming_ports = [1935, 5000, 1234, 5004, 1935, 8080]
        
    def start_monitoring(self, interval=5):
        """Start network monitoring thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Network monitoring started")
        
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.logger.info("Network monitoring stopped")
        
    def _monitor_loop(self, interval):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                stats = self.get_network_stats()
                self.stats_history.append(stats)
                
                # Keep only recent history
                if len(self.stats_history) > self.max_history:
                    self.stats_history.pop(0)
                
                # Emit to WebSocket clients
                if self.socketio:
                    self.socketio.emit('network_stats', stats)
                    
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Network monitoring error: {e}")
                time.sleep(interval)
                
    def get_network_stats(self):
        """Get current network statistics"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'interfaces': {},
            'connections': {},
            'bandwidth': {},
            'system': {},
            'streaming': {}
        }
        
        # Interface statistics
        for interface_name in psutil.net_if_addrs().keys():
            if interface_name.startswith(('eth', 'wlan', 'wlp', 'enp')):
                interface_stats = self._get_interface_stats(interface_name)
                if interface_stats:
                    stats['interfaces'][interface_name] = interface_stats
        
        # Network connections
        stats['connections'] = self._get_connection_stats()
        
        # Bandwidth usage
        stats['bandwidth'] = self._get_bandwidth_stats()
        
        # System network info
        stats['system'] = self._get_system_network_info()
        
        # Streaming statistics
        stats['streaming'] = self._get_streaming_stats()
        
        return stats
        
    def _get_interface_stats(self, interface_name):
        """Get statistics for a specific interface"""
        try:
            # Get interface addresses
            addrs = psutil.net_if_addrs().get(interface_name, [])
            ipv4 = None
            ipv6 = None
            mac = None
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ipv4 = addr.address
                elif addr.family == socket.AF_INET6:
                    ipv6 = addr.address
                elif addr.family == psutil.AF_LINK:
                    mac = addr.address
            
            # Get interface I/O stats
            io_stats = psutil.net_io_counters(pernic=True).get(interface_name)
            if not io_stats:
                return None
                
            # Get interface speed and status
            speed = self._get_interface_speed(interface_name)
            is_up = self._is_interface_up(interface_name)
            
            # Get WiFi signal if applicable
            signal = None
            if interface_name.startswith('wlan'):
                signal = self._get_wifi_signal(interface_name)
            
            return {
                'name': interface_name,
                'ipv4': ipv4,
                'ipv6': ipv6,
                'mac': mac,
                'is_up': is_up,
                'speed_mbps': speed,
                'signal_dbm': signal,
                'bytes_sent': io_stats.bytes_sent,
                'bytes_recv': io_stats.bytes_recv,
                'packets_sent': io_stats.packets_sent,
                'packets_recv': io_stats.packets_recv,
                'errors_in': io_stats.errin,
                'errors_out': io_stats.errout,
                'drops_in': io_stats.dropin,
                'drops_out': io_stats.dropout
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stats for {interface_name}: {e}")
            return None
            
    def _get_connection_stats(self):
        """Get network connection statistics"""
        try:
            connections = psutil.net_connections()
            
            stats = {
                'total': len(connections),
                'established': 0,
                'listening': 0,
                'time_wait': 0,
                'streaming_ports': {}
            }
            
            # Count connection states
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    stats['established'] += 1
                elif conn.status == 'LISTEN':
                    stats['listening'] += 1
                elif conn.status == 'TIME_WAIT':
                    stats['time_wait'] += 1
                    
                # Check streaming ports
                if conn.laddr and conn.laddr.port in self.streaming_ports:
                    port = conn.laddr.port
                    if port not in stats['streaming_ports']:
                        stats['streaming_ports'][port] = 0
                    stats['streaming_ports'][port] += 1
                    
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting connection stats: {e}")
            return {}
            
    def _get_bandwidth_stats(self):
        """Get bandwidth usage statistics"""
        try:
            # Get current I/O counters
            current_io = psutil.net_io_counters()
            
            # Calculate bandwidth if we have history
            if self.stats_history:
                last_stats = self.stats_history[-1]
                last_io = last_stats.get('bandwidth', {}).get('current_io', {})
                
                time_diff = time.time() - datetime.fromisoformat(last_stats['timestamp']).timestamp()
                
                if time_diff > 0:
                    bytes_sent_diff = current_io.bytes_sent - last_io.get('bytes_sent', 0)
                    bytes_recv_diff = current_io.bytes_recv - last_io.get('bytes_recv', 0)
                    
                    return {
                        'upload_mbps': (bytes_sent_diff * 8) / (time_diff * 1000000),
                        'download_mbps': (bytes_recv_diff * 8) / (time_diff * 1000000),
                        'current_io': {
                            'bytes_sent': current_io.bytes_sent,
                            'bytes_recv': current_io.bytes_recv,
                            'packets_sent': current_io.packets_sent,
                            'packets_recv': current_io.packets_recv
                        }
                    }
            
            # Return current stats without bandwidth calculation
            return {
                'upload_mbps': 0,
                'download_mbps': 0,
                'current_io': {
                    'bytes_sent': current_io.bytes_sent,
                    'bytes_recv': current_io.bytes_recv,
                    'packets_sent': current_io.packets_sent,
                    'packets_recv': current_io.packets_recv
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting bandwidth stats: {e}")
            return {}
            
    def _get_system_network_info(self):
        """Get system-level network information"""
        try:
            info = {
                'hostname': socket.gethostname(),
                'gateway': self._get_default_gateway(),
                'dns_servers': self._get_dns_servers(),
                'public_ip': self._get_public_ip(),
                'internet_connected': self._test_internet_connection()
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system network info: {e}")
            return {}
            
    def _get_streaming_stats(self):
        """Get streaming-specific statistics"""
        try:
            stats = {
                'active_streams': 0,
                'total_bandwidth': 0,
                'protocols': {},
                'quality': {}
            }
            
            # Check for active streaming processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(keyword in cmdline.lower() for keyword in ['ffmpeg', 'gstreamer', 'vlc']):
                        stats['active_streams'] += 1
                        
                        # Detect protocol
                        for protocol in ['rtmp', 'srt', 'udp', 'hls', 'rtp']:
                            if protocol in cmdline.lower():
                                if protocol not in stats['protocols']:
                                    stats['protocols'][protocol] = 0
                                stats['protocols'][protocol] += 1
                                break
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting streaming stats: {e}")
            return {}
            
    def _get_interface_speed(self, interface_name):
        """Get interface speed in Mbps"""
        try:
            # Try to get speed from ethtool
            result = subprocess.run(
                ['ethtool', interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'Speed:' in line:
                    speed_str = line.split(':')[1].strip()
                    if 'Mb/s' in speed_str:
                        return int(speed_str.replace('Mb/s', ''))
                    elif 'Gb/s' in speed_str:
                        return int(float(speed_str.replace('Gb/s', '')) * 1000)
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Fallback: estimate based on interface type
        if interface_name.startswith('eth'):
            return 1000  # Assume 1Gbps for Ethernet
        elif interface_name.startswith('wlan'):
            return 54   # Assume 54Mbps for WiFi
        else:
            return 100  # Default fallback
            
    def _is_interface_up(self, interface_name):
        """Check if interface is up"""
        try:
            result = subprocess.run(
                ['ip', 'link', 'show', interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return 'state UP' in result.stdout
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False
            
    def _get_wifi_signal(self, interface_name):
        """Get WiFi signal strength in dBm"""
        try:
            result = subprocess.run(
                ['iwconfig', interface_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'Signal level=' in line:
                    signal_str = line.split('Signal level=')[1].split()[0]
                    return int(signal_str.replace('dBm', ''))
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        return None
        
    def _get_default_gateway(self):
        """Get default gateway IP"""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    return line.split('default via ')[1].split()[0]
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
            
        return None
        
    def _get_dns_servers(self):
        """Get DNS servers"""
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_servers = []
                for line in f:
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
                return dns_servers
                
        except (FileNotFoundError, IndexError):
            return []
            
    def _get_public_ip(self):
        """Get public IP address"""
        try:
            # Try multiple services
            services = [
                'https://api.ipify.org',
                'https://ifconfig.me',
                'https://icanhazip.com'
            ]
            
            for service in services:
                result = subprocess.run(
                    ['curl', '-s', '--max-time', '5', service],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    ip = result.stdout.strip()
                    # Validate IP address format
                    if len(ip.split('.')) == 4:
                        return ip
                        
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
            
        return None
        
    def _test_internet_connection(self):
        """Test internet connectivity"""
        try:
            # Test DNS resolution
            socket.gethostbyname('google.com')
            
            # Test ping
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                capture_output=True,
                timeout=5
            )
            
            return result.returncode == 0
            
        except (socket.gaierror, subprocess.TimeoutExpired):
            return False
            
    def get_network_history(self, minutes=10):
        """Get network statistics history"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        
        return [
            stats for stats in self.stats_history
            if datetime.fromisoformat(stats['timestamp']).timestamp() > cutoff_time
        ]
        
    def diagnose_network(self):
        """Run network diagnostics"""
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Test interface connectivity
        for interface in self.interfaces:
            if self._is_interface_up(interface):
                diagnostics['tests'][f'interface_{interface}'] = 'PASS'
            else:
                diagnostics['tests'][f'interface_{interface}'] = 'FAIL'
                
        # Test gateway connectivity
        gateway = self._get_default_gateway()
        if gateway:
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', gateway],
                    capture_output=True,
                    timeout=5
                )
                diagnostics['tests']['gateway'] = 'PASS' if result.returncode == 0 else 'FAIL'
            except:
                diagnostics['tests']['gateway'] = 'FAIL'
        else:
            diagnostics['tests']['gateway'] = 'FAIL'
            
        # Test DNS
        try:
            socket.gethostbyname('google.com')
            diagnostics['tests']['dns'] = 'PASS'
        except:
            diagnostics['tests']['dns'] = 'FAIL'
            
        # Test internet
        diagnostics['tests']['internet'] = 'PASS' if self._test_internet_connection() else 'FAIL'
        
        # Test streaming ports
        for port in self.streaming_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                diagnostics['tests'][f'port_{port}'] = 'PASS' if result == 0 else 'FAIL'
                sock.close()
            except:
                diagnostics['tests'][f'port_{port}'] = 'FAIL'
                
        return diagnostics
        
    def optimize_network_settings(self):
        """Apply network optimization settings"""
        try:
            # Network kernel parameters
            optimizations = [
                ('net.core.rmem_max', '16777216'),
                ('net.core.wmem_max', '16777216'),
                ('net.ipv4.tcp_rmem', '4096 87380 16777216'),
                ('net.ipv4.tcp_wmem', '4096 65536 16777216'),
                ('net.core.netdev_max_backlog', '5000'),
                ('net.ipv4.tcp_slow_start_after_idle', '0'),
                ('net.ipv4.tcp_tw_reuse', '1')
            ]
            
            for param, value in optimizations:
                try:
                    subprocess.run(['sysctl', '-w', f'{param}={value}'], 
                                  capture_output=True, check=True)
                except subprocess.CalledProcessError:
                    self.logger.warning(f"Failed to set {param}")
                    
            # Interface optimizations
            for interface in self.interfaces:
                if self._is_interface_up(interface):
                    try:
                        # Increase txqueuelen
                        subprocess.run(['ifconfig', interface, 'txqueuelen', '10000'],
                                     capture_output=True, check=True)
                        
                        # Disable WiFi power management
                        if interface.startswith('wlan'):
                            subprocess.run(['iwconfig', interface, 'power', 'off'],
                                         capture_output=True, check=True)
                    except subprocess.CalledProcessError:
                        continue
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Network optimization failed: {e}")
            return False
